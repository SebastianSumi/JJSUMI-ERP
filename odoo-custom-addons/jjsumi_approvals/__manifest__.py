{
    'name': 'JJSUMI Approvals',
    'version': '19.0.1.0.0',
    'summary': 'Solicitudes de aprobación CORE (APR) sin autoaprobación',
    'author': 'JJSUMI',
    'category': 'JJSumi',
    'depends': ['base', 'mail', 'jjsumi_security', 'jjsumi_audit'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/approval_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
