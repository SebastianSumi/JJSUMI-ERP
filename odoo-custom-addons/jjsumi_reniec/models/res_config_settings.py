# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jjsumi_reniec_provider = fields.Selection([
        ('mock', 'Modo Pruebas local (sin API real)'),
        ('apisnetpe', 'apis.net.pe (v2 - Bearer Token)'),
        ('apisperu', 'apisperu.com (Token query)'),
        ('apiperudev', 'apiperu.dev (Bearer Token)'),
    ], string='Proveedor RENIEC / SUNAT',
       config_parameter='jjsumi.reniec_provider',
       default='mock')

    jjsumi_reniec_token = fields.Char(
        string='Token API RENIEC / SUNAT',
        config_parameter='jjsumi.reniec_token',
    )
