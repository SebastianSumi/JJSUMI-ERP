# -*- coding: utf-8 -*-
from odoo import models


class StockPickingN8n(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        dispatcher = self.env['jjsumi.n8n.dispatcher']
        for picking in self:
            bajos = []
            for move in picking.move_ids.filtered(lambda m: m.product_id):
                prod = move.product_id
                if prod.qty_available <= 0:
                    bajos.append({
                        'product_id': prod.id,
                        'product_name': prod.display_name,
                        'qty_available': prod.qty_available,
                    })
            if bajos:
                dispatcher.send_event('inventory.stock.low', {
                    'picking_id': picking.id,
                    'picking_name': picking.name,
                    'company': picking.company_id.name or '',
                    'productos': bajos,
                })
        return res
