# -*- coding: utf-8 -*-
from odoo import api, models


class CrmLeadN8n(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        dispatcher = self.env['jjsumi.n8n.dispatcher']
        for lead in leads:
            dispatcher.send_event('crm.lead.created', {
                'id': lead.id,
                'name': lead.name,
                'partner_name': lead.partner_name or lead.partner_id.name or '',
                'email_from': lead.email_from or '',
                'phone': lead.phone or '',
                'expected_revenue': lead.expected_revenue,
                'company': lead.company_id.name or '',
                'team': lead.team_id.name or '',
                'salesperson': lead.user_id.name or '',
            })
        return leads
