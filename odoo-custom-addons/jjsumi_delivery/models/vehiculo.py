# -*- coding: utf-8 -*-
from odoo import fields, models


class JjsumiVehiculo(models.Model):
    _name = 'jjsumi.vehiculo'
    _description = 'Vehículo de reparto JJSumi'

    name = fields.Char(string='Placa / nombre', required=True)
    capacidad_bolsas = fields.Integer(string='Capacidad (bolsas)', default=300)
    conductor_id = fields.Many2one('res.partner', string='Conductor')
    active = fields.Boolean(default=True)
