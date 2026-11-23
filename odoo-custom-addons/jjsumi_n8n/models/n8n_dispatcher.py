# -*- coding: utf-8 -*-
import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class JjsumiN8nDispatcher(models.AbstractModel):
    _name = 'jjsumi.n8n.dispatcher'
    _description = 'Despachador de eventos JJSUMI hacia n8n'

    @api.model
    def send_event(self, event_name, payload):
        icp = self.env['ir.config_parameter'].sudo()
        if icp.get_param('jjsumi.n8n_enabled', 'False') != 'True':
            return False
        url = (icp.get_param('jjsumi.n8n_webhook_url') or '').strip()
        if not url:
            return False
        secret = (icp.get_param('jjsumi.n8n_secret') or '').strip()
        headers = {'Content-Type': 'application/json'}
        if secret:
            headers['X-JJSUMI-Secret'] = secret
        body = {
            'event': event_name,
            'timestamp': fields.Datetime.now().isoformat(),
            'database': self.env.cr.dbname,
            'data': payload,
        }
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=3)
            if resp.status_code >= 400:
                _logger.warning('n8n webhook %s respondió HTTP %s: %s', event_name, resp.status_code, resp.text[:200])
                return False
            return True
        except requests.RequestException as exc:
            _logger.warning('No se pudo enviar evento %s a n8n (%s): %s', event_name, url, exc)
            return False
