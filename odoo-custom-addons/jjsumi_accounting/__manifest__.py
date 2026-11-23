{
    'name': 'JJSumi Accounting',
    'version': '19.0.1.1.0',
    'summary': 'Área Finanzas: Documentos, Hojas de costos/presupuesto y gastos',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['base', 'jjsumi_base', 'account', 'l10n_pe', 'hr_expense', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/documento_views.xml',
        'views/hoja_esg_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
