# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class JjsumiArea(models.Model):
    _name = "jjsumi.area"
    _description = "Área JJSUMI"
    _order = "code"

    code = fields.Char(string="Código", required=True, index=True)
    name = fields.Char(string="Nombre", required=True, translate=True)
    department_id = fields.Many2one("hr.department", string="Departamento", required=True, index=True)
    scope = fields.Char(string="Alcance / Sucursal", help="Corporativa o lista de sedes")
    manager_employee_id = fields.Many2one("hr.employee", string="Responsable")
    company_id = fields.Many2one("res.company", string="Compañía", default=lambda self: self.env.company)

    _jjsumi_area_code_uniq = models.Constraint(
        "unique(code)", "El código de área debe ser único.",
    )

    @api.constrains("manager_employee_id", "department_id")
    def _check_manager(self):
        leadership = self.env["jjsumi.org"]._area_leadership_jobs()
        for rec in self:
            emp = rec.manager_employee_id
            if not emp:
                continue
            job = emp.job_id
            if job and job.jjsumi_code and job.jjsumi_code not in leadership:
                raise ValidationError(_(
                    "El responsable %(name)s tiene el cargo %(job)s, que no es de jefatura/coordinación para dirigir un área."
                ) % {"name": emp.display_name, "job": job.display_name})
