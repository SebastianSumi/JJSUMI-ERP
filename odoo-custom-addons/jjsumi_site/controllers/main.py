# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class JjsumiSiteController(http.Controller):

    @http.route('/jjsumi/cotizar', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def jjsumi_cotizar(self, **post):
        nombre = (post.get('name') or '').strip()
        telefono = (post.get('phone') or '').strip()
        correo = (post.get('email') or '').strip()
        sucursal = (post.get('sucursal') or 'Juliaca').strip()
        cantidad = (post.get('cantidad') or '').strip()
        mensaje = (post.get('mensaje') or '').strip()

        if nombre:
            team = request.env['crm.team'].sudo().search([('name', 'ilike', sucursal)], limit=1)
            request.env['crm.lead'].sudo().create({
                'name': f'Cotización Web: {nombre} ({sucursal})',
                'contact_name': nombre,
                'phone': telefono,
                'email_from': correo,
                'team_id': team.id if team else False,
                'description': (
                    f"Solicitud desde la página web JJSUMI\n"
                    f"Sucursal: {sucursal}\n"
                    f"Cantidad estimada: {cantidad or 'No especificada'}\n"
                    f"Mensaje: {mensaje}"
                ),
            })
            if correo and '@' in correo:
                Lista = request.env['mailing.list'].sudo()
                Contacto = request.env['mailing.contact'].sudo()
                lista = Lista.search([('name', '=', 'Clientes JJSUMI (General)')], limit=1)
                if lista and not Contacto.search([('email', '=', correo)], limit=1):
                    Contacto.create({
                        'name': nombre,
                        'email': correo,
                        'list_ids': [(4, lista.id)],
                    })
        return request.redirect('/?cotizado=1#cotizar')
