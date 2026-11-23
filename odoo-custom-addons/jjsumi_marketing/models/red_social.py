# -*- coding: utf-8 -*-
from urllib.parse import quote

from odoo import fields, models, api


class JjsumiRedPublicacion(models.Model):
    _name = 'jjsumi.red.publicacion'
    _description = 'Publicación en redes sociales JJSumi'
    _inherit = ['mail.thread']
    _order = 'fecha_programada desc, id desc'

    name = fields.Char(string='Título interno', required=True)
    red = fields.Selection([
        ('facebook', 'Facebook'),
        ('whatsapp', 'WhatsApp'),
        ('ambas', 'Facebook y WhatsApp'),
    ], default='ambas', required=True)
    mensaje = fields.Text(required=True)
    imagen = fields.Image(max_width=1024, max_height=1024)
    enlace_destino = fields.Char(string='Enlace a compartir',
                                 help='Normalmente la web de JJSumi o una página de producto.')
    fecha_programada = fields.Datetime(string='Fecha programada')
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('programado', 'Programado'),
        ('publicado', 'Publicado'),
    ], default='borrador', tracking=True)
    enlace_facebook = fields.Char(compute='_compute_enlaces')
    enlace_whatsapp = fields.Char(compute='_compute_enlaces')

    @api.depends('mensaje', 'enlace_destino')
    def _compute_enlaces(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for rec in self:
            url = rec.enlace_destino or base
            texto = ((rec.mensaje or '') + ' ' + url).strip()
            rec.enlace_facebook = 'https://www.facebook.com/sharer/sharer.php?u=%s&quote=%s' % (
                quote(url, safe=''), quote(rec.mensaje or ''))
            rec.enlace_whatsapp = 'https://api.whatsapp.com/send?text=%s' % quote(texto)

    def action_programar(self):
        self.write({'state': 'programado'})

    def action_publicado(self):
        self.write({'state': 'publicado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})

    def action_abrir_facebook(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_url', 'url': self.enlace_facebook, 'target': 'new'}

    def action_abrir_whatsapp(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_url', 'url': self.enlace_whatsapp, 'target': 'new'}
