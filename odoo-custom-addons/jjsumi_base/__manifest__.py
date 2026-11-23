{
    'name': 'JJSumi Base',
    'version': '19.0.1.1.0',
    'summary': 'Empresa, producto Yeso (30/26/23 kg), precios, parámetros y menú raíz JJSumi',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'data/company.xml',
        'data/params.xml',
        'data/products.xml',
        'data/setup.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
