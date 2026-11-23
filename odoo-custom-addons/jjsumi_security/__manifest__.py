{
    'name': 'JJSUMI Security',
    'version': '19.0.1.0.0',
    'summary': '15 roles JJSUMI, sede de usuario, mapa cargo→rol y reglas',
    'author': 'JJSUMI',
    'category': 'JJSumi',
    'depends': ['base', 'hr', 'jjsumi_org'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/user_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
