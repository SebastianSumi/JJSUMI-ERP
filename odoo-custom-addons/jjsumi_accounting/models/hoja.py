# -*- coding: utf-8 -*-
from odoo import api, fields, models


class JjsumiHoja(models.Model):
    _name = 'jjsumi.hoja'
    _description = 'Hoja de cálculo JJSumi (presupuestos / costos / flujo)'
    _order = 'fecha desc, id desc'

    name = fields.Char(string='Nombre', required=True)
    tipo = fields.Selection([
        ('costos', 'Costos de producción'),
        ('presupuesto', 'Presupuesto'),
        ('flujo', 'Flujo de caja'),
        ('otro', 'Otro'),
    ], default='costos', required=True)
    fecha = fields.Date(default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    line_ids = fields.One2many('jjsumi.hoja.linea', 'hoja_id', string='Filas')
    total_ingresos = fields.Monetary(compute='_compute_totales', store=True, currency_field='currency_id')
    total_egresos = fields.Monetary(compute='_compute_totales', store=True, currency_field='currency_id')
    resultado = fields.Monetary(compute='_compute_totales', store=True, currency_field='currency_id')
    margen = fields.Float(string='Margen %', compute='_compute_totales', store=True)

    @api.depends('line_ids.monto', 'line_ids.sentido')
    def _compute_totales(self):
        for rec in self:
            ing = sum(rec.line_ids.filtered(lambda l: l.sentido == 'ingreso').mapped('monto'))
            egr = sum(rec.line_ids.filtered(lambda l: l.sentido == 'egreso').mapped('monto'))
            rec.total_ingresos = ing
            rec.total_egresos = egr
            rec.resultado = ing - egr
            rec.margen = (ing - egr) / ing * 100.0 if ing else 0.0


class JjsumiHojaLinea(models.Model):
    _name = 'jjsumi.hoja.linea'
    _description = 'Fila de hoja JJSumi'
    _order = 'sequence, id'

    hoja_id = fields.Many2one('jjsumi.hoja', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    currency_id = fields.Many2one(related='hoja_id.currency_id')
    concepto = fields.Char(required=True)
    sentido = fields.Selection([('ingreso', 'Ingreso'), ('egreso', 'Egreso')], default='egreso', required=True)
    cantidad = fields.Float(default=1.0)
    precio = fields.Monetary(string='Precio unitario', currency_field='currency_id')
    monto = fields.Monetary(compute='_compute_monto', store=True, currency_field='currency_id')

    @api.depends('cantidad', 'precio')
    def _compute_monto(self):
        for line in self:
            line.monto = line.cantidad * line.precio
