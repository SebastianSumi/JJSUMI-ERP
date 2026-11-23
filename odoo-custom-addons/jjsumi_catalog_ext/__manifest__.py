{
    'name': 'JJSumi Catálogo Ext (Fase 2)',
    'version': '19.0.1.0.0',
    'summary': 'Catálogo maestro de productos JJSUMI: categorías, UoM, atributos, variantes, tarifas, proveedores',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': [
        'product', 'uom', 'stock', 'stock_account', 'purchase_stock',
        'mrp', 'account', 'l10n_pe', 'jjsumi_base',
    ],
    'data': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
