# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class JjsumiCalidad(models.Model):
    _name = 'jjsumi.calidad'
    _description = 'Control de calidad JJSumi'
    _inherit = ['mail.thread']
    _order = 'fecha desc, id desc'

    name = fields.Char(string='Número', default=lambda self: _('Nuevo'), readonly=True, copy=False)
    production_id = fields.Many2one('mrp.production', string='Orden de fabricación')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    fecha = fields.Date(default=fields.Date.context_today)
    inspector_id = fields.Many2one('res.users', string='Inspector', default=lambda self: self.env.user)
    peso_nominal = fields.Float(string='Peso nominal (kg)', required=True, default=23.0)
    peso_medido = fields.Float(string='Peso medido (kg)')
    humedad = fields.Float(string='Humedad (%)')
    tiempo_fraguado = fields.Float(string='Tiempo de fraguado (min)')
    resultado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ], compute='_compute_resultado', store=True, tracking=True)
    observaciones = fields.Text()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # Intenta leer el peso del nombre de la variante (p. ej. "Yeso (23 kg)")
        for rec in self:
            nombre = rec.product_id.display_name or ''
            for peso in (30.0, 26.0, 23.0):
                if '%d kg' % int(peso) in nombre:
                    rec.peso_nominal = peso
                    break

    @api.depends('peso_nominal', 'peso_medido', 'humedad')
    def _compute_resultado(self):
        # SUPUESTOS (parámetros del sistema): tolerancia de peso ±2 % y humedad máx. 1 %
        icp = self.env['ir.config_parameter']
        tol = icp.jjsumi_get_float('jjsumi.tolerancia_peso', 2.0)
        hum_max = icp.jjsumi_get_float('jjsumi.humedad_max', 1.0)
        for rec in self:
            if not rec.peso_medido:
                rec.resultado = 'pendiente'
                continue
            desvio = abs(rec.peso_medido - rec.peso_nominal) / rec.peso_nominal * 100.0 if rec.peso_nominal else 100.0
            ok = desvio <= tol and rec.humedad <= hum_max
            rec.resultado = 'aprobado' if ok else 'rechazado'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('jjsumi.calidad') or _('Nuevo')
        return super().create(vals_list)
