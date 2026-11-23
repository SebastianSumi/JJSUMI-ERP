# -*- coding: utf-8 -*-
{
    'name': 'JJSUMI - Consulta RENIEC / SUNAT',
    'version': '19.0.1.1.0',
    'category': 'Sales/CRM',
    'summary': 'Autocompletado de clientes por DNI (RENIEC) y RUC (SUNAT) con API real o modo pruebas',
    'author': 'JJSUMI',
    'license': 'LGPL-3',
    'depends': ['base', 'base_setup', 'l10n_latam_base', 'l10n_pe'],
    'data': [
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}
