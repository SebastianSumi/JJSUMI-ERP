# -*- coding: utf-8 -*-
"""Quita las etiquetas DEMO/supuesto de los registros creados por el seed.

Se ejecuta antes de cargar los datos del módulo, para que el seed encuentre
los nombres nuevos y no cree duplicados.
"""


def migrate(cr, version):
    # Proveedores de materia prima
    renombres = {
        'Cantera de yeso (DEMO)': 'Cantera La Esperanza',
        'Proveedor de combustible reciclado (DEMO)': 'Reciclagas Perú',
        'Proveedor de empaques (DEMO)': 'Empaques del Sur',
    }
    for antes, despues in renombres.items():
        cr.execute("UPDATE res_partner SET name = %s WHERE name = %s", (despues, antes))

    # Equipos: nombre traducible (jsonb)
    cr.execute(
        "UPDATE maintenance_equipment "
        "SET name = replace(name::text, ' (supuesto)', '')::jsonb "
        "WHERE name::text LIKE '%(supuesto)%'"
    )

    # Solicitudes de mantenimiento: preventivos (equipo renombrado) y correctivas [DEMO]
    cr.execute(
        "UPDATE maintenance_request "
        "SET name = replace(name, ' (supuesto)', '') "
        "WHERE name LIKE '%(supuesto)%'"
    )
    cr.execute(
        "UPDATE maintenance_request "
        "SET name = regexp_replace(name, '^\\[DEMO\\] ', '') "
        "WHERE name LIKE '[DEMO] %'"
    )

    # Controles de calidad y cambios PLM
    cr.execute(
        "UPDATE jjsumi_calidad "
        "SET observaciones = regexp_replace(observaciones, '^\\[DEMO\\] ', '') "
        "WHERE observaciones LIKE '[DEMO] %'"
    )
    cr.execute(
        "UPDATE jjsumi_plm_cambio "
        "SET descripcion = regexp_replace(descripcion, '^\\[DEMO\\] ', '') "
        "WHERE descripcion LIKE '[DEMO] %'"
    )
