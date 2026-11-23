{
    'name': 'JJSumi Marketing',
    'version': '19.0.1.0.0',
    'summary': 'Área Marketing: Automatización, Correo, SMS, Redes sociales (Facebook/WhatsApp), Eventos y Encuestas',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['base', 'jjsumi_base', 'sale_management', 'mass_mailing', 'mass_mailing_sms',
                'event', 'event_sale', 'survey', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/marketing_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
