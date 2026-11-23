{
    'name': 'JJSUMI Core',
    'version': '19.0.1.0.0',
    'summary': 'Parámetros, secuencias CORE, carga idempotente Fase 1 y menú CORE',
    'author': 'JJSUMI',
    'category': 'JJSumi',
    'depends': [
        'base', 'hr', 'mail', 'web',
        'jjsumi_org', 'jjsumi_security', 'jjsumi_audit', 'jjsumi_approvals',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/params.xml',
        'data/load_fase1.xml',
        'views/core_menus.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
