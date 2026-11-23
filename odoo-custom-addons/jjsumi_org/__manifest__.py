{
    'name': 'JJSUMI Org',
    'version': '19.0.1.0.0',
    'summary': 'Áreas JJSUMI, códigos DEP/CAR/EMP y validaciones de estructura',
    'author': 'JJSUMI',
    'category': 'JJSumi',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/area_views.xml',
        'views/hr_ext_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
