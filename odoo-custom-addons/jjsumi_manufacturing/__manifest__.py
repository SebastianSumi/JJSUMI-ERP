{
    'name': 'JJSumi Manufacturing',
    'version': '19.0.1.2.0',
    'summary': 'Área Inventario y fabricación: Manufactura (LdM del yeso), Compras, Mantenimiento y Calidad',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['base', 'jjsumi_base', 'stock', 'mrp', 'purchase', 'purchase_requisition', 'maintenance', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/manufacturing_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
