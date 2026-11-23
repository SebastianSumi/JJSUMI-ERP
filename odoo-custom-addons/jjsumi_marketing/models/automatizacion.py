# -*- coding: utf-8 -*-
import re
from datetime import datetime, time, timedelta
from html import escape
from urllib.parse import quote

from odoo import _, api, fields, models


class JjsumiAutomatizacion(models.Model):
    _name = 'jjsumi.automatizacion'
    _description = 'Automatización de marketing JJSumi'
    _inherit = ['mail.thread']

    name = fields.Char(string='Nombre', required=True)
    activo = fields.Boolean(default=True)
    disparador = fields.Selection([
        ('postventa', 'Post-venta: N días después de confirmar un pedido'),
        ('reactivacion', 'Reactivación: N días desde la última compra'),
    ], default='postventa', required=True)
    dias = fields.Integer(string='Días', default=3, required=True)
    canal = fields.Selection([
        ('correo', 'Correo electrónico'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp (enlace de 1 clic)'),
    ], default='correo', required=True)
    asunto = fields.Char(string='Asunto (correo)')
    mensaje = fields.Text(string='Mensaje', required=True,
                          help='Use {nombre} para insertar el nombre del cliente.')
    log_ids = fields.One2many('jjsumi.automatizacion.log', 'automatizacion_id', string='Historial')
    log_count = fields.Integer(compute='_compute_log_count')

    @api.depends('log_ids')
    def _compute_log_count(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)

    # ------------------------------------------------------------------
    @api.model
    def _cron_ejecutar(self):
        for auto in self.search([('activo', '=', True)]):
            auto._ejecutar()

    def action_ejecutar_ahora(self):
        for auto in self:
            auto._ejecutar()
        return True

    def _partners_objetivo(self):
        self.ensure_one()
        hoy = fields.Date.context_today(self)
        dia = hoy - timedelta(days=self.dias)
        inicio = datetime.combine(dia, time.min)
        fin = datetime.combine(dia, time.max)
        SO = self.env['sale.order'].sudo()
        orders = SO.search([('state', '=', 'sale'), ('date_order', '>=', inicio), ('date_order', '<=', fin)])
        partners = orders.mapped('partner_id')
        if self.disparador == 'reactivacion':
            partners = partners.filtered(lambda p: not SO.search_count([
                ('partner_id', '=', p.id), ('state', '=', 'sale'), ('date_order', '>', fin)]))
        return partners

    def _ejecutar(self):
        self.ensure_one()
        hoy = fields.Date.context_today(self)
        for partner in self._partners_objetivo():
            if self.env['jjsumi.automatizacion.log'].search_count([
                    ('automatizacion_id', '=', self.id), ('partner_id', '=', partner.id), ('fecha', '=', hoy)]):
                continue
            self._enviar(partner, hoy)

    @staticmethod
    def _telefono_pe(numero):
        digitos = re.sub(r'\D', '', numero or '')
        if len(digitos) == 9 and digitos.startswith('9'):
            digitos = '51' + digitos
        return digitos

    def _enviar(self, partner, hoy):
        self.ensure_one()
        cuerpo = (self.mensaje or '').replace('{nombre}', partner.name or '')
        vals = {'automatizacion_id': self.id, 'partner_id': partner.id, 'fecha': hoy,
                'canal': self.canal, 'estado': 'omitido', 'detalle': ''}
        telefono = (partner.mobile if 'mobile' in partner._fields else False) or partner.phone
        if self.canal == 'correo':
            if not partner.email:
                vals['detalle'] = _('El contacto no tiene correo.')
            else:
                self.env['mail.mail'].sudo().create({
                    'subject': self.asunto or self.name,
                    'body_html': '<p>%s</p>' % escape(cuerpo).replace('\n', '<br/>'),
                    'email_to': partner.email,
                    'email_from': self.env.company.email_formatted or self.env.user.email_formatted,
                    'auto_delete': True,
                })
                vals['estado'] = 'enviado'
        elif self.canal == 'sms':
            if not telefono:
                vals['detalle'] = _('El contacto no tiene teléfono.')
            else:
                self.env['sms.sms'].sudo().create({'number': telefono, 'body': cuerpo, 'partner_id': partner.id})
                vals['estado'] = 'enviado'
        else:  # whatsapp: sin API, se genera un enlace para enviar con 1 clic
            numero = self._telefono_pe(telefono)
            if not numero:
                vals['detalle'] = _('El contacto no tiene teléfono.')
            else:
                vals['enlace'] = 'https://wa.me/%s?text=%s' % (numero, quote(cuerpo))
                vals['estado'] = 'pendiente_manual'
        self.env['jjsumi.automatizacion.log'].create(vals)

    def action_ver_log(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Historial'),
            'res_model': 'jjsumi.automatizacion.log',
            'view_mode': 'list,form',
            'domain': [('automatizacion_id', '=', self.id)],
        }


class JjsumiAutomatizacionLog(models.Model):
    _name = 'jjsumi.automatizacion.log'
    _description = 'Historial de automatización'
    _order = 'id desc'

    automatizacion_id = fields.Many2one('jjsumi.automatizacion', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    fecha = fields.Date()
    canal = fields.Selection([('correo', 'Correo'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp')])
    estado = fields.Selection([
        ('enviado', 'Enviado / en cola'),
        ('pendiente_manual', 'Pendiente (enviar manualmente)'),
        ('omitido', 'Omitido'),
    ])
    enlace = fields.Char(string='Enlace WhatsApp')
    detalle = fields.Char()

    def action_abrir_enlace(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_url', 'url': self.enlace, 'target': 'new'}
