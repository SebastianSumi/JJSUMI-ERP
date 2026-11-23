# -*- coding: utf-8 -*-
from odoo import fields, models


class JjsumiDocumento(models.Model):
    _name = 'jjsumi.documento'
    _description = 'Documento JJSumi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'

    name = fields.Char(string='Título', required=True, tracking=True)
    carpeta = fields.Selection([
        ('ventas', 'Ventas'),
        ('compras', 'Compras'),
        ('produccion', 'Producción'),
        ('legal', 'Legal / Tributario'),
        ('laboral', 'Laboral'),
        ('otros', 'Otros'),
    ], string='Carpeta', default='otros', required=True)
    partner_id = fields.Many2one('res.partner', string='Contacto')
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today)
    vencimiento = fields.Date(string='Vencimiento')
    archivo = fields.Binary(string='Archivo', attachment=True)
    archivo_nombre = fields.Char(string='Nombre del archivo')
    notas = fields.Text(string='Notas')
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
