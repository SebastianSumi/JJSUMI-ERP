# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

GRP_GM = 'jjsumi_security.group_jjsumi_general_manager'
GRP_SUP = 'jjsumi_security.group_jjsumi_sales_supervisor'


class SaleOrderDescuentos(models.Model):
    _inherit = 'sale.order'

    jjsumi_descuento_max = fields.Float(string='Descuento máximo (%)', compute='_compute_jjsumi_descuento', store=True)
    jjsumi_aprobacion_requerida = fields.Selection([
        ('ninguna', 'No requiere'),
        ('supervisor', 'Supervisor comercial (>5%)'),
        ('general', 'Gerente general (>15%)'),
    ], string='Aprobación de descuento', compute='_compute_jjsumi_descuento', store=True)
    jjsumi_aprobado = fields.Boolean(string='Descuento aprobado', copy=False)
    jjsumi_descuento_aprobado = fields.Float(string='Descuento aprobado (%)', copy=False)

    @api.depends('order_line.discount')
    def _compute_jjsumi_descuento(self):
        for order in self:
            d = max(order.order_line.mapped('discount') or [0.0])
            order.jjsumi_descuento_max = d
            order.jjsumi_aprobacion_requerida = 'general' if d > 15 else ('supervisor' if d > 5 else 'ninguna')

    def _jjsumi_check_descuento(self):
        for order in self:
            if order.jjsumi_aprobacion_requerida == 'ninguna':
                continue
            if not order.jjsumi_aprobado or order.jjsumi_descuento_max > order.jjsumi_descuento_aprobado + 1e-9:
                raise ValidationError(_(
                    'El descuento de %.2f%% requiere aprobación (%s). Solicite la aprobación antes de confirmar.',
                    order.jjsumi_descuento_max, dict(self._fields['jjsumi_aprobacion_requerida'].selection)[order.jjsumi_aprobacion_requerida]))

    def action_jjsumi_aprobar_descuento(self):
        for order in self:
            if order.jjsumi_aprobacion_requerida == 'ninguna':
                continue
            user = self.env.user
            if order.create_uid == user:
                raise UserError(_('No puede aprobar un descuento que usted mismo solicitó.'))
            puede = user.has_group(GRP_GM) or (
                order.jjsumi_aprobacion_requerida == 'supervisor' and user.has_group(GRP_SUP))
            if not puede:
                raise UserError(_('Su perfil no puede aprobar un descuento de %.2f%%.', order.jjsumi_descuento_max))
            order.write({'jjsumi_aprobado': True, 'jjsumi_descuento_aprobado': order.jjsumi_descuento_max})
            order.message_post(body=_('Descuento de %.2f%% aprobado por %s.', order.jjsumi_descuento_max, user.name))
        return True

    def action_confirm(self):
        for order in self.filtered(lambda o: o.state in ('draft', 'sent')):
            order._jjsumi_check_descuento()
        return super().action_confirm()
