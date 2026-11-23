# -*- coding: utf-8 -*-
from odoo import models


class PurchaseOrderN8n(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super().button_confirm()
        dispatcher = self.env['jjsumi.n8n.dispatcher']
        for po in self:
            if po.amount_total >= 5000:
                dispatcher.send_event('purchase.order.high_amount', {
                    'id': po.id,
                    'name': po.name,
                    'partner_name': po.partner_id.name or '',
                    'partner_vat': po.partner_id.vat or '',
                    'amount_total': po.amount_total,
                    'currency': po.currency_id.name,
                    'company': po.company_id.name or '',
                    'user': po.user_id.name or '',
                    'state': po.state,
                })
        return res
