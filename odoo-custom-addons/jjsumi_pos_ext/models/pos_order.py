# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

GRP_SUP = 'jjsumi_security.group_jjsumi_sales_supervisor'
GRP_BM = 'jjsumi_security.group_jjsumi_branch_manager'
GRP_GM = 'jjsumi_security.group_jjsumi_general_manager'


class PosOrderJjsumi(models.Model):
    _inherit = 'pos.order'

    x_jjsumi_autorizado_por = fields.Many2one('res.users', string='Descuento autorizado por', copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            cmds = vals.get('lines') or []
            config = self.env['pos.config'].browse(vals.get('config_id'))
            wh = config.warehouse_id or config.picking_type_id.warehouse_id
            autorizado = self.env['res.users'].browse(vals.get('x_jjsumi_autorizado_por')) if vals.get('x_jjsumi_autorizado_por') else self.env['res.users']
            for cmd in cmds:
                if not (isinstance(cmd, (list, tuple)) and len(cmd) == 3 and isinstance(cmd[2], dict)):
                    continue
                line = cmd[2]
                if (line.get('discount') or 0) > 5:
                    if not autorizado or not (autorizado.has_group(GRP_SUP) or autorizado.has_group(GRP_BM) or autorizado.has_group(GRP_GM)):
                        raise UserError(_('Descuento mayor al 5%% requiere autorización de supervisor.'))
                product = self.env['product.product'].browse(line.get('product_id'))
                if product and product.type == 'consu' and product.is_storable and wh:
                    disp = product.with_context(location=wh.lot_stock_id.id, warehouse_id=wh.id).qty_available
                    if disp < (line.get('qty') or 0):
                        raise UserError(_('Stock insuficiente en %s para %s (disponible %s).', wh.name, product.display_name, disp))
        return super().create(vals_list)
