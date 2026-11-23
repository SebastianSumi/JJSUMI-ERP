# -*- coding: utf-8 -*-
import logging
from datetime import date, timedelta
import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_DEFAULT_BSC_URL = 'http://127.0.0.1:3000/bsc/sync-odoo'
_DEFAULT_BSC_SECRET = 'bsc-techperu-dev-secret-change-me'

_COMPANY_TO_BSC = [
    (None, 'jjsumi'),
    (7, 'jjsumi-juliaca'),
    (8, 'jjsumi-puno'),
    (9, 'jjsumi-arequipa'),
    (10, 'jjsumi-cusco'),
    (11, 'jjsumi-tacna'),
]


def _quarter_start(ref_date):
    q_month = ((ref_date.month - 1) // 3) * 3 + 1
    return date(ref_date.year, q_month, 1)


class JjsumiBscSync(models.AbstractModel):
    _name = 'jjsumi.bsc.sync'
    _description = 'Sincronizador en tiempo real de Odoo hacia BSC (Comercial, Finanzas SUNAT e Inventario)'

    @api.model
    def _get_sync_config(self):
        ICP = self.env['ir.config_parameter'].sudo()
        url = ICP.get_param('jjsumi_bsc.sync_url', _DEFAULT_BSC_URL)
        secret = ICP.get_param('jjsumi_bsc.sync_secret', _DEFAULT_BSC_SECRET)
        return url, secret

    @api.model
    def push_realtime(self, origen='ODOO_REALTIME'):
        SaleOrder = self.env['sale.order'].sudo()
        PosOrder = self.env['pos.order'].sudo()
        Partner = self.env['res.partner'].sudo()
        Lead = self.env['crm.lead'].sudo()
        AccountMove = self.env['account.move'].sudo()
        Product = self.env['product.product'].sudo()
        Quant = self.env['stock.quant'].sudo()

        hoy = fields.Date.context_today(self)
        inicio_trimestre = _quarter_start(hoy)
        hace_30_dias = hoy - timedelta(days=30)

        clientes_total = Partner.search_count([('active', '=', True), ('customer_rank', '>', 0)])
        payload = []

        for comp_id, bsc_id in _COMPANY_TO_BSC:
            comp_dom = [('company_id', '=', comp_id)] if comp_id else []

            # 1. Ventas B2B y POS del trimestre activo
            so_dom = [('state', '=', 'sale'), ('date_order', '>=', inicio_trimestre)] + comp_dom
            pos_dom = [('state', 'in', ('paid', 'done', 'invoiced')), ('date_order', '>=', inicio_trimestre)] + comp_dom
            lead_dom = list(comp_dom)

            orders = SaleOrder.search(so_dom)
            ventas_b2b = len(orders)
            monto_b2b = sum(orders.mapped('amount_total'))
            untaxed = sum(orders.mapped('amount_untaxed'))
            profit = sum(orders.mapped('profit')) if 'profit' in SaleOrder._fields else 0.0
            margen = round((profit / untaxed) * 100, 1) if untaxed > 0 else 0.0

            pos_orders = PosOrder.search(pos_dom)
            ventas_pos = len(pos_orders)
            monto_pos = sum(pos_orders.mapped('amount_total'))

            leads_all = Lead.search_count(lead_dom)
            leads_won = Lead.search_count(lead_dom + [('probability', '=', 100)])
            conv = round((leads_won / leads_all) * 100, 1) if leads_all > 0 else 0.0

            # 2. Finanzas y Cumplimiento SUNAT / RENIEC (l10n_pe + account.move)
            inv_out_dom = [
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', inicio_trimestre),
            ] + comp_dom
            inv_in_dom = [
                ('state', '=', 'posted'),
                ('move_type', '=', 'in_invoice'),
                ('invoice_date', '>=', inicio_trimestre),
            ] + comp_dom
            nc_out_dom = [
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_refund'),
                ('invoice_date', '>=', inicio_trimestre),
            ] + comp_dom

            out_invoices = AccountMove.search(inv_out_dom)
            in_invoices = AccountMove.search(inv_in_dom)
            out_refunds = AccountMove.search(nc_out_dom)

            igv_ventas = sum(out_invoices.mapped('amount_tax'))
            igv_compras = sum(in_invoices.mapped('amount_tax'))
            igv_nc = sum(out_refunds.mapped('amount_tax'))
            igv_neto = round(igv_ventas - igv_compras - igv_nc, 2)

            total_facturado = sum(out_invoices.mapped('amount_total'))
            total_nc = sum(out_refunds.mapped('amount_total'))
            tasa_nc = round((total_nc / total_facturado) * 100, 2) if total_facturado > 0 else 0.0

            # Riesgo fiscal SUNAT/RENIEC: % de monto con RUC/DNI verificado Activo/Habido o cache local
            todas_facturas = out_invoices | in_invoices
            monto_total_ops = sum(todas_facturas.mapped('amount_total'))
            monto_verificado = 0.0
            for mv in todas_facturas:
                estado_reniec = (mv.partner_id.jjsumi_reniec_estado or '').lower()
                if 'activo' in estado_reniec or 'habido' in estado_reniec or 'verificado' in estado_reniec or 'caché' in estado_reniec:
                    monto_verificado += mv.amount_total
            cumplimiento_sunat = round((monto_verificado / monto_total_ops) * 100, 1) if monto_total_ops > 0 else 100.0

            # Cartera vencida CxC > 30 dias
            cxc_vencida_dom = [
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ('not_paid', 'partial')),
                ('invoice_date_due', '<', hace_30_dias),
            ] + comp_dom
            cxc_vencida = sum(AccountMove.search(cxc_vencida_dom).mapped('amount_residual'))
            pct_cartera_vencida = round((cxc_vencida / total_facturado) * 100, 2) if total_facturado > 0 else 0.0

            # 3. Inventario (quiebres de stock y valorización)
            prods = Product.search([('type', '=', 'consu'), ('is_storable', '=', True)] if 'is_storable' in Product._fields else [('type', '=', 'product')])
            total_prods = len(prods)
            sin_stock = 0
            valor_inv = 0.0
            if total_prods > 0:
                if comp_id:
                    quants = Quant.search([('location_id.usage', '=', 'internal'), ('company_id', '=', comp_id)])
                else:
                    quants = Quant.search([('location_id.usage', '=', 'internal')])
                qty_by_prod = {}
                for q in quants:
                    qty_by_prod[q.product_id.id] = qty_by_prod.get(q.product_id.id, 0.0) + q.quantity
                    valor_inv += q.quantity * q.product_id.standard_price
                for p in prods:
                    if qty_by_prod.get(p.id, 0.0) <= 0:
                        sin_stock += 1
            pct_quiebre = round((sin_stock / total_prods) * 100, 1) if total_prods > 0 else 0.0

            payload.append({
                'empresaId': bsc_id,
                'kpis': {
                    'K1': margen,
                    'K2': ventas_b2b,
                    'K3': round(monto_b2b + monto_pos, 2),
                    'K5': clientes_total,
                    'K6': conv,
                    'K7': ventas_pos,
                    'K14': igv_neto,
                    'K15': cumplimiento_sunat,
                    'K16': tasa_nc,
                    'K17': pct_cartera_vencida,
                    'K19': pct_quiebre,
                    'K20': round(valor_inv, 2),
                },
            })

        url, secret = self._get_sync_config()
        try:
            resp = requests.post(
                url,
                json={'origen': origen, 'empresas': payload},
                headers={'x-jjsumi-secret': secret, 'Content-Type': 'application/json'},
                timeout=15,
            )
            resp.raise_for_status()
            return True
        except requests.RequestException as exc:
            _logger.warning('No se pudo sincronizar con BSC (%s): %s', url, exc)
            return False


class SaleOrderBsc(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        self.env['jjsumi.bsc.sync'].push_realtime('ODOO_SALE_CONFIRM')
        return res

    def _action_cancel(self):
        res = super()._action_cancel()
        self.env['jjsumi.bsc.sync'].push_realtime('ODOO_SALE_CANCEL')
        return res


class PosOrderBsc(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.env['jjsumi.bsc.sync'].push_realtime('ODOO_POS_ORDER')
        return recs


class ResPartnerBsc(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        if any(v.get('customer_rank', 0) > 0 for v in vals_list):
            self.env['jjsumi.bsc.sync'].push_realtime('ODOO_NEW_CUSTOMER')
        return recs


class CrmLeadBsc(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self.env['jjsumi.bsc.sync'].push_realtime('ODOO_CRM_LEAD')
        return recs


class AccountMoveBsc(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        self.env['jjsumi.bsc.sync'].push_realtime('ODOO_ACCOUNT_POST')
        return res


class StockPickingBsc(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        self.env['jjsumi.bsc.sync'].push_realtime('ODOO_STOCK_VALIDATE')
        return res
