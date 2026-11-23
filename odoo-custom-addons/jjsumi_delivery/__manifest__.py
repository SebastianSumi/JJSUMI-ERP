{
    'name': 'JJSumi Delivery',
    'version': '19.0.1.2.0',
    'summary': 'Inventario y logística: vehículos y hojas de reparto con control de capacidad (~300 bolsas)',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['base', 'jjsumi_base', 'delivery', 'stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/delivery_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
