{
    'name': 'JJSumi Mantenimiento Ext (contador horas/km)',
    'version': '19.0.1.0.0',
    'summary': 'Mantenimiento preventivo por horas de operación y kilómetros (Odoo solo tiene recurrencia por tiempo)',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['maintenance', 'jjsumi_security'],
    'data': ['data/cron.xml', 'views/maintenance_views.xml'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
