# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class JjsumiReparto(models.Model):
    _name = 'jjsumi.reparto'
    _description = 'Hoja de reparto JJSumi'
    _inherit = ['mail.thread']
    _order = 'fecha desc, id desc'

    name = fields.Char(string='Número', default=lambda self: _('Nuevo'), readonly=True, copy=False)
    fecha = fields.Date(default=fields.Date.context_today, required=True)
    vehiculo_id = fields.Many2one('jjsumi.vehiculo', string='Vehículo', required=True)
    zona = fields.Selection([
        ('local', 'Distribución local (Juliaca)'),
        ('intercity', 'Distribución fuera de ciudad'),
    ], default='local', required=True)
    picking_ids = fields.Many2many(
        'stock.picking', string='Entregas',
        domain="[('picking_type_code', '=', 'outgoing'), ('state', 'not in', ('done', 'cancel'))]")
    capacidad = fields.Integer(related='vehiculo_id.capacidad_bolsas', string='Capacidad (bolsas)')
    bolsas_total = fields.Integer(string='Bolsas a repartir', compute='_compute_bolsas', store=True)
    ocupacion = fields.Float(string='Ocupación %', compute='_compute_bolsas', store=True)
    excede = fields.Boolean(string='Excede capacidad', compute='_compute_bolsas', store=True)
    state = fields.Selection([
        ('planificado', 'Planificado'),
        ('en_ruta', 'En ruta'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ], default='planificado', tracking=True, copy=False)

    @api.depends('picking_ids.move_ids.product_uom_qty', 'vehiculo_id.capacidad_bolsas')
    def _compute_bolsas(self):
        for rec in self:
            moves = rec.picking_ids.move_ids.filtered(lambda m: m.product_id.type != 'service')
            total = int(sum(moves.mapped('product_uom_qty')))
            cap = rec.vehiculo_id.capacidad_bolsas
            rec.bolsas_total = total
            rec.ocupacion = total / cap * 100.0 if cap else 0.0
            rec.excede = bool(cap) and total > cap

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('jjsumi.reparto') or _('Nuevo')
        return super().create(vals_list)

    def action_salir(self):
        for rec in self:
            if not rec.picking_ids:
                raise UserError(_('Agregue al menos una entrega a la hoja de reparto.'))
            if rec.excede:
                raise UserError(_(
                    'La carga (%(total)s bolsas) excede la capacidad del vehículo (%(cap)s).',
                    total=rec.bolsas_total, cap=rec.capacidad))
        self.write({'state': 'en_ruta'})

    def action_entregado(self):
        self.write({'state': 'entregado'})

    def action_cancelar(self):
        self.write({'state': 'cancelado'})
