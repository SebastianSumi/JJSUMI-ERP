# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmTeamComision(models.Model):
    _inherit = 'crm.team'

    x_jjsumi_comision_pct = fields.Float(string='Comisión vendedor (% neto cobrado)', default=2.0)
