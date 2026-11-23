# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    jjsumi_version = fields.Char(string='Versión', default='1.0', copy=True)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    jjsumi_combustible_real = fields.Float(string='Combustible real usado (L)')
    jjsumi_merma_bolsas = fields.Integer(string='Bolsas de merma')
    jjsumi_costo_total = fields.Float(
        string='Costo de materiales', compute='_compute_jjsumi_costos', digits=(16, 2))
    jjsumi_costo_bolsa = fields.Float(
        string='Costo por bolsa', compute='_compute_jjsumi_costos', digits=(16, 2))

    @api.depends('move_raw_ids.product_uom_qty', 'move_raw_ids.product_id', 'product_qty', 'jjsumi_merma_bolsas')
    def _compute_jjsumi_costos(self):
        for mo in self:
            total = sum(m.product_uom_qty * (m.product_id.standard_price or 0.0) for m in mo.move_raw_ids)
            utiles = (mo.product_qty or 0.0) - (mo.jjsumi_merma_bolsas or 0)
            mo.jjsumi_costo_total = total
            mo.jjsumi_costo_bolsa = total / utiles if utiles > 0 else 0.0
