# -*- coding: utf-8 -*-
from odoo import fields, models


class HrVersionSalario(models.Model):
    _inherit = 'hr.version'

    wage = fields.Monetary(groups='jjsumi_security.group_jjsumi_hr_manager,jjsumi_security.group_jjsumi_admin')
