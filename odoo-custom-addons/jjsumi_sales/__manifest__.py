{
    'name': 'JJSumi Sales',
    'version': '19.0.1.1.0',
    'summary': 'Área Ventas: CRM, Ventas (bonificación 200+3, mínimos, transporte, ganancia), Punto de venta',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['base', 'jjsumi_base', 'sale_management', 'crm', 'sale_crm', 'point_of_sale', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/crm_lead_views.xml',
        'views/jjsumi_ext_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
