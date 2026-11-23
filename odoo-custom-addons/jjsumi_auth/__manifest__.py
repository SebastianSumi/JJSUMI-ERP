{
    'name': 'JJSumi Auth',
    'version': '19.0.1.0.0',
    'summary': 'Login profesional JJSumi — tarjeta premium, 2FA, idioma, listo para SSO',
    'author': 'JJSumi',
    'category': 'JJSumi',
    'depends': ['website', 'auth_signup', 'auth_totp'],
    'data': [
        'views/login_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'jjsumi_auth/static/src/css/jjsumi_login.css',
            'jjsumi_auth/static/src/js/login.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
