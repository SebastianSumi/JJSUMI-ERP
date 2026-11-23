# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# Mapa cargo → roles permitidos (Fase 1 canónico)
CARGO_ROLES = {
    "CAR-001": {"ROL-001", "ROL-002"},
    "CAR-002": set(),
    "CAR-003": {"ROL-002"},
    "CAR-004": set(),
    "CAR-005": {"ROL-009"},
    "CAR-006": {"ROL-009"},
    "CAR-007": set(),
    "CAR-008": {"ROL-010"},
    "CAR-009": set(),
    "CAR-010": {"ROL-001"},
    "CAR-011": set(),
    "CAR-012": {"ROL-012"},
    "CAR-013": {"ROL-004"},
    "CAR-014": {"ROL-004"},
    "CAR-015": set(),
    "CAR-016": {"ROL-014"},
    "CAR-017": {"ROL-011"},
    "CAR-018": {"ROL-011"},
    "CAR-019": {"ROL-005"},
    "CAR-020": {"ROL-005"},
    "CAR-021": {"ROL-015"},
    "CAR-022": {"ROL-006"},
    "CAR-023": {"ROL-006"},
    "CAR-024": {"ROL-013"},
    "CAR-025": {"ROL-007"},
    "CAR-026": {"ROL-008"},
    "CAR-027": {"ROL-003"},
}

# Excepciones documentadas: (login, rol)
EXCEPCIONES = {
    ("ana.flores", "ROL-001"),
    ("juan.delgado", "ROL-001"),
}

ROLE_XML = {
    "ROL-001": "jjsumi_security.group_jjsumi_admin",
    "ROL-002": "jjsumi_security.group_jjsumi_general_manager",
    "ROL-003": "jjsumi_security.group_jjsumi_branch_manager",
    "ROL-004": "jjsumi_security.group_jjsumi_production_manager",
    "ROL-005": "jjsumi_security.group_jjsumi_warehouse_supervisor",
    "ROL-006": "jjsumi_security.group_jjsumi_buyer",
    "ROL-007": "jjsumi_security.group_jjsumi_salesperson",
    "ROL-008": "jjsumi_security.group_jjsumi_cashier",
    "ROL-009": "jjsumi_security.group_jjsumi_accountant",
    "ROL-010": "jjsumi_security.group_jjsumi_hr_manager",
    "ROL-011": "jjsumi_security.group_jjsumi_maintenance_technician",
    "ROL-012": "jjsumi_security.group_jjsumi_auditor",
    "ROL-013": "jjsumi_security.group_jjsumi_sales_supervisor",
    "ROL-014": "jjsumi_security.group_jjsumi_quality_manager",
    "ROL-015": "jjsumi_security.group_jjsumi_distribution_coordinator",
}


class HrEmployeeSede(models.Model):
    """Cambiar la sucursal del empleado no debe dejar desalineado al usuario vinculado."""
    _inherit = "hr.employee"

    @api.constrains("company_id", "user_id")
    def _check_user_sede_matches_company(self):
        for emp in self:
            user = emp.user_id.sudo()
            if not user or not user.jjsumi_sede_id or not emp.company_id.parent_id:
                continue
            if user.jjsumi_sede_id != emp.company_id:
                raise ValidationError(_(
                    "La sucursal del empleado %(emp)s (%(emp_sede)s) no coincide con la sede del usuario %(user)s (%(user_sede)s)."
                ) % {
                    "emp": emp.display_name,
                    "emp_sede": emp.company_id.name,
                    "user": user.login,
                    "user_sede": user.jjsumi_sede_id.name,
                })


class ResUsersExt(models.Model):
    _inherit = "res.users"

    jjsumi_sede_id = fields.Many2one(
        "res.company", string="Sede (branch)", domain="[('parent_id', '!=', False)]",
        help="Sucursal operativa del usuario. Debe coincidir con la sede del empleado vinculado.",
    )
    jjsumi_role_codes = fields.Char(
        string="Códigos de rol", default="", help="Códigos ROL-xxx separados por coma (informativo/Fase 1).",
    )

    def _jjsumi_employee(self):
        """Empleado vinculado, resuelto sin depender de company_ids activos."""
        self.ensure_one()
        return self.env["hr.employee"].sudo().search(
            [("user_id", "=", self.id), ("active", "=", True)], limit=1
        )

    @api.constrains("jjsumi_sede_id", "employee_ids")
    def _check_sede_matches_employee(self):
        for user in self:
            if not user.jjsumi_sede_id:
                continue
            emp = user._jjsumi_employee()
            if not emp:
                continue
            # sede del empleado = company_id si es branch hija
            emp_company = emp.company_id
            if emp_company and emp_company.id != user.jjsumi_sede_id.id:
                # solo exigir coincidencia si el empleado tiene sede branch asignada
                if emp_company.parent_id:
                    raise ValidationError(_(
                        "La sede del usuario %(user)s (%(user_sede)s) no coincide con la sede del empleado (%(emp_sede)s)."
                    ) % {
                        "user": user.login,
                        "user_sede": user.jjsumi_sede_id.name,
                        "emp_sede": emp_company.name,
                    })

    @api.constrains("jjsumi_role_codes", "employee_ids", "group_ids")
    def _check_roles_vs_cargo(self):
        for user in self:
            codes = [c.strip() for c in (user.jjsumi_role_codes or "").split(",") if c.strip()]
            emp = user._jjsumi_employee()
            if not codes or not emp or not emp.job_id:
                continue
            job_code = emp.job_id.jjsumi_code or ""
            allowed = set(CARGO_ROLES.get(job_code, set()))
            for code in codes:
                if code not in allowed and (user.login, code) not in EXCEPCIONES:
                    raise ValidationError(_(
                        "El rol %(role)s no está permitido para el cargo %(job)s del usuario %(user)s."
                    ) % {
                        "role": code,
                        "job": emp.job_id.display_name,
                        "user": user.login,
                    })
            # special: cashier requires CAR-026; branch manager requires CAR-027
            if "ROL-008" in codes and job_code != "CAR-026":
                raise ValidationError(_("Solo el cargo Cajero (CAR-026) puede tener rol Cajero."))
            if "ROL-003" in codes and job_code != "CAR-027":
                raise ValidationError(_("Solo el cargo Gerente de Sucursal (CAR-027) puede tener rol Gerente de Sucursal."))

    def _jjsumi_apply_role_groups(self):
        """Asigna grupos res.groups a partir de jjsumi_role_codes (idempotente)."""
        internal = self.env.ref("base.group_user", raise_if_not_found=False)
        for user in self:
            codes = [c.strip() for c in (user.jjsumi_role_codes or "").split(",") if c.strip()]
            groups = self.env["res.groups"]
            for code in codes:
                xmlid = ROLE_XML.get(code)
                if not xmlid:
                    continue
                try:
                    groups |= self.env.ref(xmlid)
                except ValueError:
                    continue
            if internal:
                groups |= internal
            if groups:
                user.group_ids = [(4, g.id) for g in groups]
