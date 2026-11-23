# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrDepartmentExt(models.Model):
    _inherit = "hr.department"

    jjsumi_code = fields.Char(string="Código JJSUMI", index=True)
    jjsumi_sede = fields.Char(string="Sede principal")

    _jjsumi_dep_code_uniq = models.Constraint(
        "unique(jjsumi_code)", "El código de departamento debe ser único.",
    )

    @api.constrains("manager_id", "jjsumi_code")
    def _check_manager_job(self):
        leadership = self.env["jjsumi.org"]._leadership_jobs()
        for rec in self:
            if not rec.manager_id or not rec.jjsumi_code:
                continue
            job = rec.manager_id.job_id
            if job and job.jjsumi_code and job.jjsumi_code not in leadership:
                raise ValidationError(_(
                    "El responsable de %(dep)s (%(emp)s) tiene cargo %(job)s incompatible con jefatura de departamento."
                ) % {
                    "dep": rec.display_name,
                    "emp": rec.manager_id.display_name,
                    "job": job.display_name,
                })


class HrJobExt(models.Model):
    _inherit = "hr.job"

    jjsumi_code = fields.Char(string="Código JJSUMI", index=True)

    _jjsumi_job_code_uniq = models.Constraint(
        "unique(jjsumi_code)", "El código de cargo debe ser único.",
    )


class HrEmployeeExt(models.Model):
    _inherit = "hr.employee"

    jjsumi_code = fields.Char(string="Código EMP", index=True, copy=False)
    jjsumi_area_id = fields.Many2one("jjsumi.area", string="Área")

    _jjsumi_emp_code_uniq = models.Constraint(
        "unique(jjsumi_code)", "El código de empleado debe ser único.",
    )

    @api.constrains("jjsumi_code", "department_id", "job_id")
    def _check_required_org(self):
        for rec in self:
            if rec.jjsumi_code and not rec.department_id:
                raise ValidationError(_("El empleado %s debe tener departamento.") % rec.display_name)
            if rec.jjsumi_code and not rec.job_id:
                raise ValidationError(_("El empleado %s debe tener cargo.") % rec.display_name)


class HrVersionExt(models.Model):
    """department_id y job_id viven en hr.version; sin esta restricción el
    write de hr.employee los escribe sin pasar por la validación del empleado."""
    _inherit = "hr.version"

    @api.constrains("department_id", "job_id", "employee_id")
    def _check_jjsumi_required_org(self):
        for rec in self:
            emp = rec.employee_id
            if not emp or not emp.jjsumi_code:
                continue
            if not rec.department_id:
                raise ValidationError(_("El empleado %s debe tener departamento.") % emp.display_name)
            if not rec.job_id:
                raise ValidationError(_("El empleado %s debe tener cargo.") % emp.display_name)


class JjsumiOrgAbstract(models.AbstractModel):
    _name = "jjsumi.org"
    _description = "Utilidades de organización JJSUMI"

    LEADERSHIP_JOBS = {
        "CAR-001", "CAR-003", "CAR-005", "CAR-006", "CAR-008", "CAR-010",
        "CAR-012", "CAR-013", "CAR-014", "CAR-016", "CAR-017", "CAR-019",
        "CAR-021", "CAR-022", "CAR-024", "CAR-025", "CAR-027",
    }
    # Áreas: además de jefaturas, coordinación funcional (ARE-006 EMP-013
    # Analista de RR. HH. y ARE-008 EMP-015 Soporte Técnico).
    AREA_LEADERSHIP_JOBS = LEADERSHIP_JOBS | {"CAR-009", "CAR-011"}

    def _leadership_jobs(self):
        return set(self.LEADERSHIP_JOBS)

    def _area_leadership_jobs(self):
        return set(self.AREA_LEADERSHIP_JOBS)
