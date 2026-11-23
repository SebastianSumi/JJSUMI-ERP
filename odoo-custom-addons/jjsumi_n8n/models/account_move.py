# -*- coding: utf-8 -*-
from odoo import models


class AccountMoveN8n(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        dispatcher = self.env['jjsumi.n8n.dispatcher']
        for move in self:
            if move.move_type not in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
                continue
            reniec_estado = move.partner_id.jjsumi_reniec_estado or 'Sin verificar'
            doc_type = move.l10n_latam_document_type_id.name or move.move_type
            payload = {
                'id': move.id,
                'name': move.name,
                'move_type': move.move_type,
                'document_type': doc_type,
                'partner_name': move.partner_id.name or '',
                'partner_vat': move.partner_id.vat or '',
                'reniec_estado': reniec_estado,
                'amount_untaxed': move.amount_untaxed,
                'amount_tax': move.amount_tax,
                'amount_total': move.amount_total,
                'company': move.company_id.name or '',
            }
            dispatcher.send_event('finance.invoice.posted', payload)

            if move.move_type == 'out_refund':
                dispatcher.send_event('finance.credit_note.posted', payload)

            if move.move_type == 'in_invoice':
                est_low = reniec_estado.lower()
                es_valido = any(k in est_low for k in ('activo', 'habido', 'verificado', 'caché'))
                if not es_valido:
                    dispatcher.send_event('finance.sunat.risk', payload)
        return res
