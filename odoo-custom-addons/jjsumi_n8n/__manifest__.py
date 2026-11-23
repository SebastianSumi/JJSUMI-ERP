# -*- coding: utf-8 -*-
{
    'name': 'JJSUMI - Integración n8n (Webhooks)',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Envía eventos en tiempo real desde Odoo (Ventas, Finanzas SUNAT, Compras, Inventario, CRM) hacia n8n',
    'author': 'JJSUMI',
    'license': 'LGPL-3',
    'depends': ['base', 'base_setup', 'sale_management', 'crm', 'account', 'purchase', 'stock', 'jjsumi_sales', 'jjsumi_reniec'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}
