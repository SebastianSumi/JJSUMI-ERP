# -*- coding: utf-8 -*-
import math

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

ZONAS = [
    ('local', 'Distribución local (Juliaca)'),
    ('intercity', 'Distribución fuera de ciudad'),
]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_bonus = fields.Boolean(string='Bonificación', default=False, copy=False)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_zone = fields.Selection(ZONAS, string='Zona de entrega', default='local', required=True)
    bolsas_total = fields.Integer(string='Bolsas compradas', compute='_compute_bolsas', store=True)
    bolsas_bonificadas = fields.Integer(string='Bolsas de bonificación', compute='_compute_bolsas', store=True)
    viajes_estimados = fields.Integer(string='Viajes estimados', compute='_compute_bolsas', store=True)
    transport_cost = fields.Monetary(
        string='Costo de transporte', currency_field='currency_id',
        compute='_compute_transport_cost', store=True, readonly=False)
    total_cost = fields.Monetary(
        string='Costo total estimado', compute='_compute_costs', store=True, currency_field='currency_id')
    profit = fields.Monetary(
        string='Ganancia / Pérdida estimada (sin IGV)', compute='_compute_costs', store=True,
        currency_field='currency_id')

    # ------------------------------------------------------------------
    # Parámetros
    # ------------------------------------------------------------------
    def _jjsumi_param(self, key, default):
        return self.env['ir.config_parameter'].jjsumi_get_float(key, default)

    @staticmethod
    def _es_bolsa(line):
        return bool(
            line.product_id and not line.display_type
            and line.product_id.type != 'service')

    # ------------------------------------------------------------------
    # Cálculos
    # ------------------------------------------------------------------
    @api.depends('order_line.product_uom_qty', 'order_line.product_id', 'order_line.is_bonus')
    def _compute_bolsas(self):
        cada = int(self._jjsumi_param('jjsumi.bonus_cada', 200)) or 200
        bono = int(self._jjsumi_param('jjsumi.bonus_bolsas', 3))
        capacidad = int(self._jjsumi_param('jjsumi.capacidad_vehiculo', 300)) or 300
        for order in self:
            lines = order.order_line.filtered(self._es_bolsa)
            compradas = int(sum(lines.filtered(lambda l: not l.is_bonus).mapped('product_uom_qty')))
            bonificadas = (compradas // cada) * bono
            order.bolsas_total = compradas
            order.bolsas_bonificadas = bonificadas
            order.viajes_estimados = math.ceil((compradas + bonificadas) / capacidad) if compradas else 0

    @api.depends('delivery_zone', 'viajes_estimados')
    def _compute_transport_cost(self):
        local = self._jjsumi_param('jjsumi.transporte_local', 0.0)
        inter = self._jjsumi_param('jjsumi.transporte_intercity', 0.0)
        for order in self:
            tarifa = local if order.delivery_zone == 'local' else inter
            order.transport_cost = order.viajes_estimados * tarifa

    @api.depends('order_line.product_id', 'order_line.product_uom_qty', 'transport_cost', 'amount_untaxed')
    def _compute_costs(self):
        for order in self:
            costo = 0.0
            for line in order.order_line.filtered(self._es_bolsa):
                costo += line.product_uom_qty * (line.product_id.standard_price or 0.0)
            order.total_cost = costo + (order.transport_cost or 0.0)
            order.profit = (order.amount_untaxed or 0.0) - order.total_cost

    # ------------------------------------------------------------------
    # Reglas de negocio (se aplican al confirmar)
    # ------------------------------------------------------------------
    def _jjsumi_check_enteros(self):
        for order in self:
            for line in order.order_line.filtered(lambda l: not l.display_type and l.product_id):
                qty = line.product_uom_qty or 0.0
                if abs(qty - round(qty)) > 1e-6:
                    raise ValidationError(_(
                        'No se permiten decimales en la cantidad. '
                        'El producto "%s" tiene cantidad %s; ingrese un número entero.',
                        line.product_id.display_name, qty))

    def _jjsumi_check_minimos(self):
        min_local = int(self._jjsumi_param('jjsumi.min_local', 50))
        min_inter = int(self._jjsumi_param('jjsumi.min_intercity', 200))
        for order in self:
            if order.delivery_zone == 'local' and order.bolsas_total < min_local:
                raise ValidationError(_(
                    'El mínimo para distribución local es %s bolsas (el pedido tiene %s).',
                    min_local, order.bolsas_total))
            if order.delivery_zone == 'intercity' and order.bolsas_total < min_inter:
                raise ValidationError(_(
                    'El mínimo para distribución fuera de ciudad es %s bolsas (el pedido tiene %s).',
                    min_inter, order.bolsas_total))

    def _jjsumi_aplicar_bonificacion(self):
        """Regla 200+3: por cada 200 bolsas compradas, 3 bolsas gratis (misma variante de la línea mayor)."""
        for order in self:
            order.order_line.filtered('is_bonus').unlink()
            lines = order.order_line.filtered(self._es_bolsa)
            if not lines or not order.bolsas_bonificadas:
                continue
            principal = max(lines, key=lambda l: l.product_uom_qty)
            self.env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': principal.product_id.id,
                'product_uom_qty': order.bolsas_bonificadas,
                'price_unit': 0.0,
                'is_bonus': True,
                'sequence': max(order.order_line.mapped('sequence') or [10]) + 1,
                'name': _('Bonificación %(cada)s+%(bono)s: %(producto)s',
                          cada=int(self._jjsumi_param('jjsumi.bonus_cada', 200)),
                          bono=int(self._jjsumi_param('jjsumi.bonus_bolsas', 3)),
                          producto=principal.product_id.display_name),
            })

    def action_confirm(self):
        for order in self.filtered(lambda o: o.state in ('draft', 'sent')):
            order._jjsumi_check_enteros()
            order._jjsumi_check_minimos()
            order._jjsumi_aplicar_bonificacion()
        return super().action_confirm()
