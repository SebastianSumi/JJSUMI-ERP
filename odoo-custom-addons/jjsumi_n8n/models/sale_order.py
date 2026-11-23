# -*- coding: utf-8 -*-
from odoo import models


class SaleOrderN8n(models.Model):
    _inherit = 'sale.order'

    def _jjsumi_n8n_payload(self):
        self.ensure_one()
        lines_desc = [
            f"- {l.product_id.display_name}: {int(l.product_uom_qty)} u. x S/ {l.price_unit:.2f} = S/ {l.price_subtotal:.2f}"
            for l in self.order_line.filtered(lambda x: not x.display_type and x.product_id)
        ]
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'partner_id': self.partner_id.id,
            'partner_name': self.partner_id.name,
            'partner_vat': self.partner_id.vat or '',
            'partner_phone': self.partner_id.phone or '',
            'partner_email': self.partner_id.email or '',
            'amount_total': self.amount_total,
            'currency': self.currency_id.name,
            'company': self.company_id.name,
            'team': self.team_id.name or '',
            'salesperson': self.user_id.name or '',
            'delivery_zone': self.delivery_zone,
            'bolsas_total': self.bolsas_total,
            'bolsas_bonificadas': self.bolsas_bonificadas,
            'descuento_max': self.jjsumi_descuento_max,
            'aprobacion_requerida': self.jjsumi_aprobacion_requerida,
            'description': '\n'.join(lines_desc),
        }

    def action_confirm(self):
        res = super().action_confirm()
        dispatcher = self.env['jjsumi.n8n.dispatcher']
        for order in self:
            dispatcher.send_event('sale.order.confirmed', order._jjsumi_n8n_payload())
        return res

    def action_jjsumi_aprobar_descuento(self):
        res = super().action_jjsumi_aprobar_descuento()
        dispatcher = self.env['jjsumi.n8n.dispatcher']
        for order in self:
            dispatcher.send_event('sale.order.discount_approved', order._jjsumi_n8n_payload())
        return res
