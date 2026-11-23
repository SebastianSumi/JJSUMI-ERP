# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class JjsumiAccountingSeed(models.AbstractModel):
    _name = 'jjsumi.accounting.seed'
    _description = 'Carga inicial del área Finanzas'

    @api.model
    def _jjsumi_seed(self):
        """Datos iniciales idempotentes. Cada bloque es tolerante a fallos (queda en log)."""
        self._seed_hoja_costos()
        self._seed_gastos()
        return True

    def _seed_hoja_costos(self):
        Hoja = self.env['jjsumi.hoja']
        if Hoja.search_count([('name', '=', 'Carga de 23 kg (referencia)')]):
            return
        try:
            with self.env.cr.savepoint():
                Hoja.create({
                    'name': 'Carga de 23 kg (referencia)',
                    'tipo': 'costos',
                    'line_ids': [
                        (0, 0, {'concepto': 'Piedra de yeso (carga ~14 t)', 'sentido': 'egreso', 'cantidad': 1, 'precio': 1300.0}),
                        (0, 0, {'concepto': 'Combustible reciclado (1 cilindro 108 L)', 'sentido': 'egreso', 'cantidad': 1, 'precio': 180.0}),
                        (0, 0, {'concepto': 'Empaque (bolsas)', 'sentido': 'egreso', 'cantidad': 600, 'precio': 0.40}),
                        (0, 0, {'concepto': 'Venta de bolsas de 23 kg', 'sentido': 'ingreso', 'cantidad': 600, 'precio': 6.0}),
                    ],
                })
        except Exception:  # noqa: BLE001
            _logger.exception('JJSumi: no se pudo crear la hoja de costos de ejemplo')

    def _seed_gastos(self):
        Product = self.env['product.product']
        if 'can_be_expensed' not in Product._fields:
            return
        for nombre in ('Combustible de vehículo', 'Mantenimiento y repuestos', 'Viáticos', 'Alimentación'):
            if Product.with_context(active_test=False).search_count([('name', '=', nombre), ('can_be_expensed', '=', True)]):
                continue
            try:
                with self.env.cr.savepoint():
                    Product.create({'name': nombre, 'type': 'service', 'can_be_expensed': True,
                                    'list_price': 0.0, 'standard_price': 0.0})
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo crear la categoría de gasto %s', nombre)
