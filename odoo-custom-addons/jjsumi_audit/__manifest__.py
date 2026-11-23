{
    'name': 'JJSUMI Audit',
    'version': '19.0.1.0.0',
    'summary': 'Eventos de auditoría JJSUMI (solo lectura para funcionales)',
    'author': 'JJSUMI',
    'category': 'JJSumi',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/audit_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
