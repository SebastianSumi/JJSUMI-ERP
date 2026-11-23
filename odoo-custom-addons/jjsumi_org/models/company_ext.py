# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompanyExt(models.Model):
    _inherit = "res.company"

    jjsumi_code = fields.Char(string="Código JJSUMI", index=True)

    _jjsumi_code_uniq = models.Constraint(
        "unique(jjsumi_code)", "El código de compañía debe ser único.",
    )
