# -*- coding: utf-8 -*-
from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def jjsumi_get_float(self, key, default=0.0):
        """Lee un parámetro del sistema (jjsumi.*) como número."""
        value = self.sudo().get_param(key)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
