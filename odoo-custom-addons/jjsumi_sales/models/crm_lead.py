# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    bolsas_estimadas = fields.Integer(string='Bolsas estimadas')
    delivery_zone = fields.Selection([
        ('local', 'Distribución local (Juliaca)'),
        ('intercity', 'Distribución fuera de ciudad'),
    ], string='Zona de entrega', default='local')
