# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jjsumi_n8n_enabled = fields.Boolean(
        string='Activar integración n8n',
        config_parameter='jjsumi.n8n_enabled',
    )
    jjsumi_n8n_webhook_url = fields.Char(
        string='URL Webhook n8n',
        config_parameter='jjsumi.n8n_webhook_url',
        default='http://127.0.0.1:5678/webhook/jjsumi-odoo',
    )
    jjsumi_n8n_secret = fields.Char(
        string='Token secreto (X-JJSUMI-Secret)',
        config_parameter='jjsumi.n8n_secret',
    )
