# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError

GRP_GM = 'jjsumi_security.group_jjsumi_general_manager'
GRP_BM = 'jjsumi_security.group_jjsumi_branch_manager'
GRP_ADM = 'jjsumi_security.group_jjsumi_admin'


class PurchaseOrderApproval(models.Model):
    _inherit = 'purchase.order'

    def button_approve(self, force=False):
        for po in self.filtered(lambda o: o.state == 'to approve'):
            user = self.env.user
            if po.create_uid == user:
                raise UserError(_('No puede aprobar una orden de compra que usted creó.'))
            if po.amount_total > 5000 and not (user.has_group(GRP_GM) or user.has_group(GRP_BM) or user.has_group(GRP_ADM)):
                raise UserError(_('Las compras mayores a S/ 5,000 requieren aprobación del jefe de sucursal o gerencia.'))
            if po.amount_total > 20000 and not (user.has_group(GRP_GM) or user.has_group(GRP_ADM)):
                raise UserError(_('Las compras mayores a S/ 20,000 solo pueden ser aprobadas por el Gerente General.'))
        return super().button_approve(force=force)


class AccountMoveTresVias(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Validación de 3 vías: precio de factura de proveedor > 5% sobre la OC requiere contador o admin."""
        grp_ok = ('jjsumi_security.group_jjsumi_accountant', 'jjsumi_security.group_jjsumi_admin')
        for move in self.filtered(lambda m: m.move_type == 'in_invoice'):
            for line in move.invoice_line_ids.filtered('purchase_line_id'):
                pl = line.purchase_line_id
                if not pl.price_unit:
                    continue
                desv = abs(line.price_unit - pl.price_unit) / pl.price_unit
                if desv > 0.05 and not any(self.env.user.has_group(g) for g in grp_ok):
                    raise UserError(_(
                        'Discrepancia de precio %.1f%% frente a la OC %s (producto %s). Requiere contador o administrador.',
                        desv * 100, pl.order_id.name, line.product_id.display_name))
        return super().action_post()
