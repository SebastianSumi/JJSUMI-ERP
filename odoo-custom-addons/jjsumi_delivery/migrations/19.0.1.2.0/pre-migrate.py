# -*- coding: utf-8 -*-
"""Renombra el vehículo DEMO a su nombre definitivo y conserva su xmlid."""


def migrate(cr, version):
    cr.execute(
        "UPDATE ir_model_data SET name = 'vehiculo_reparto' "
        "WHERE module = 'jjsumi_delivery' AND name = 'vehiculo_demo'"
    )
    cr.execute(
        "UPDATE jjsumi_vehiculo SET name = 'Camión de reparto' "
        "WHERE name = 'Camión de reparto (DEMO)'"
    )
