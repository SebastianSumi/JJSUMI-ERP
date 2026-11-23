# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

MAINT_ROOT_ID = 405  # menú raíz "Mantenimiento" (sin XML ID en Odoo 19)


def post_init_hook(env):
    env = api.Environment(env.cr, SUPERUSER_ID, {})
    root = env['ir.ui.menu'].browse(MAINT_ROOT_ID)
    if root.exists():
        act = lambda xid: env.ref(xid).id
        parent = env['ir.ui.menu'].search([('parent_id', '=', root.id), ('name', '=', 'JJSUMI')], limit=1)
        if not parent:
            parent = env['ir.ui.menu'].create({'name': 'JJSUMI', 'parent_id': root.id, 'sequence': 90})
        items = [
            ('Equipos JJSUMI', 'jjsumi_menus.action_jjsumi_equipos', 10),
            ('Preventivos (horas / km)', 'jjsumi_menus.action_jjsumi_preventivos', 20),
            ('Equipos de mantenimiento', 'maintenance.maintenance_team_action_settings', 30),
            ('Categorías de equipo', 'maintenance.hr_equipment_category_action', 40),
        ]
        for name, xid, seq in items:
            if not env['ir.ui.menu'].search([('parent_id', '=', parent.id), ('name', '=', name)], limit=1):
                env['ir.ui.menu'].create({'name': name, 'parent_id': parent.id, 'sequence': seq,
                                          'action': 'ir.actions.act_window,%s' % act(xid)})
    # Menús de la app JJSumi que quedaron vacíos (módulos desinstalados) se archivan
    for name in ('Marketing', 'Ventas'):
        vacio = env['ir.ui.menu'].search([('name', '=', name), ('parent_id.name', '=', 'JJSumi')])
        for m in vacio:
            if not m.child_id.filtered('active'):
                m.active = False
