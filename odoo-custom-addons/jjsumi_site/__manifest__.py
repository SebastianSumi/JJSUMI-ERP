{
    'name': 'JJSumi Site',
    'version': '19.0.1.1.0',
    'summary': 'Landing marketera de JJSumi integrada con Tienda, Portal de Clientes, CRM y n8n',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['website', 'website_sale', 'crm'],
    'data': [
        'data/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'jjsumi_site/static/src/css/site.css',
            'jjsumi_site/static/src/js/site.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
