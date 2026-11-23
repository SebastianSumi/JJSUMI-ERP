{
    "name": "JJSUMI - Inicio por tarjetas",
    "summary": "Pantalla de inicio JJSUMI por tarjetas, conservando las aplicaciones nativas de Odoo",
    "version": "19.0.1.0.1",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "JJSUMI",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/home_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "jjsumi_home_cards/static/src/js/home_dashboard.js",
            "jjsumi_home_cards/static/src/xml/home_dashboard.xml",
            "jjsumi_home_cards/static/src/scss/home_dashboard.scss",
        ],
    },
    "application": True,
    "installable": True,
}
