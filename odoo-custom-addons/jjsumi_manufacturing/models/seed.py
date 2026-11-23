# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Rendimiento por carga (1 carga ≈ 14 t de piedra + 1 cilindro de 108 L).
# 23 kg: ~600 bolsas (dato del propietario). 26 y 30 kg: derivados de los mismos ~13 800 kg.
BOMS = [
    # (xmlid del valor, código, bolsas por carga)
    ('jjsumi_base.attribute_value_23kg', 'JJ-YESO-23', 600),
    ('jjsumi_base.attribute_value_26kg', 'JJ-YESO-26', 530),
    ('jjsumi_base.attribute_value_30kg', 'JJ-YESO-30', 460),
]
COSTO_CARGA_PIEDRA = 1300.0
COSTO_CILINDRO = 180.0
COSTO_EMPAQUE = 0.40

# Marca de origen de las órdenes de fabricación cargadas por el seed
ORIGIN_SEED = 'SEED-JJSUMI'

# (código, nombre, costo/hora, eficiencia %, setup min, limpieza min)
CENTROS_TRABAJO = [
    ('WC-HORNO-01', 'Horno / calcinador 1', 80.0, 90.0, 15.0, 10.0),
    ('WC-HORNO-02', 'Horno / calcinador 2', 80.0, 85.0, 15.0, 10.0),
    ('WC-MOLINO-01', 'Molino / trituradora 1', 60.0, 92.0, 10.0, 8.0),
    ('WC-MOLINO-02', 'Molino / trituradora 2', 60.0, 88.0, 10.0, 8.0),
    ('WC-ENVASO-01', 'Línea de envasado 1', 40.0, 95.0, 5.0, 5.0),
    ('WC-ENVASO-02', 'Línea de envasado 2', 40.0, 93.0, 5.0, 5.0),
    ('WC-PALET', 'Paletizado / almacén', 25.0, 97.0, 5.0, 5.0),
]

# (operación, minutos, familia de workcenter)
OPERACIONES = [
    ('Preparación de carga', 30, 'MOLINO'),
    ('Mezclado', 20, 'HORNO'),
    ('Calcinación', 120, 'HORNO'),
    ('Molienda y tamizado', 45, 'MOLINO'),
    ('Envasado', 60, 'ENVASO'),
    ('Paletizado', 25, 'PALET'),
]

# Línea de workcenter por familia y LdM (mixta en 30 kg)
LINEA_POR_BOM = {
    'JJ-YESO-23': {'MOLINO': '01', 'HORNO': '01', 'ENVASO': '01', 'PALET': ''},
    'JJ-YESO-26': {'MOLINO': '02', 'HORNO': '02', 'ENVASO': '02', 'PALET': ''},
    'JJ-YESO-30': {'MOLINO': '02', 'HORNO': '01', 'ENVASO': '01', 'PALET': ''},
}

# Inventario inicial de materias primas (WH/Stock)
INVENTARIO_INICIAL = [
    ('JJ-PIEDRA', 60.0),
    ('JJ-COMBUSTIBLE', 80.0),
    ('JJ-BOLSA', 60000.0),
]

# Equipos de mantenimiento (los 3 primeros ya existen; se omiten por nombre)
EQUIPOS_MANT = [
    ('Horno / calcinador', 'Maquinaria de producción', 30),
    ('Molino / trituradora', 'Maquinaria de producción', 30),
    ('Vehículo de reparto', 'Vehículos', 60),
    ('Horno / calcinador 2', 'Maquinaria de producción', 30),
    ('Molino / trituradora 2', 'Maquinaria de producción', 30),
    ('Línea de envasado 1', 'Maquinaria de producción', 45),
    ('Compresor de aire', 'Equipo auxiliar', 90),
    ('Montacargas eléctrico', 'Equipo auxiliar', 60),
]


class JjsumiManufacturingSeed(models.AbstractModel):
    _name = 'jjsumi.manufacturing.seed'
    _description = 'Carga inicial del área Inventario y fabricación'

    @api.model
    def _jjsumi_seed(self):
        self._seed_materias_primas()
        self._seed_boms()
        self._seed_centros_trabajo()
        self._seed_operaciones_bom()
        self._limpiar_mos_rotas()
        self._seed_inventario_inicial()
        self._seed_ordenes_fabricacion()
        self._seed_calidad()
        self._seed_mantenimiento()
        return True

    # -- materias primas ------------------------------------------------
    def _producto(self, code, name, costo, categ, proveedor, precio_compra):
        Product = self.env['product.product'].with_context(active_test=False)
        prod = Product.search([('default_code', '=', code)], limit=1)
        if prod:
            return prod
        partner = self.env['res.partner'].search([('name', '=', proveedor)], limit=1) or \
            self.env['res.partner'].create({'name': proveedor, 'supplier_rank': 1, 'is_company': True})
        return Product.create({
            'name': name,
            'default_code': code,
            'type': 'consu',
            'is_storable': True,
            'categ_id': categ.id,
            'standard_price': costo,
            'list_price': 0.0,
            'sale_ok': False,
            'purchase_ok': True,
            'seller_ids': [(0, 0, {'partner_id': partner.id, 'min_qty': 1.0, 'price': precio_compra})],
        })

    def _seed_materias_primas(self):
        try:
            with self.env.cr.savepoint():
                categ = self.env['product.category'].search([('name', '=', 'Materias primas JJSumi')], limit=1) or \
                    self.env['product.category'].create({'name': 'Materias primas JJSumi'})
                # Proveedores de materia prima (editables desde Compras > Proveedores)
                self._producto('JJ-PIEDRA', 'Carga de piedra de yeso (~14 t)', COSTO_CARGA_PIEDRA, categ,
                               'Cantera La Esperanza', COSTO_CARGA_PIEDRA)
                self._producto('JJ-COMBUSTIBLE', 'Combustible reciclado (cilindro 108 L)', COSTO_CILINDRO, categ,
                               'Reciclagas Perú', COSTO_CILINDRO)
                self._producto('JJ-BOLSA', 'Bolsa de empaque', COSTO_EMPAQUE, categ,
                               'Empaques del Sur', COSTO_EMPAQUE)
        except Exception:  # noqa: BLE001
            _logger.exception('JJSumi: no se pudieron crear las materias primas')

    # -- listas de materiales ------------------------------------------------
    def _seed_boms(self):
        Bom = self.env['mrp.bom'].with_context(active_test=False)
        tmpl = self.env.ref('jjsumi_base.product_template_yeso', raise_if_not_found=False)
        piedra = self.env['product.product'].search([('default_code', '=', 'JJ-PIEDRA')], limit=1)
        comb = self.env['product.product'].search([('default_code', '=', 'JJ-COMBUSTIBLE')], limit=1)
        bolsa = self.env['product.product'].search([('default_code', '=', 'JJ-BOLSA')], limit=1)
        if not (tmpl and piedra and comb and bolsa):
            _logger.warning('JJSumi: faltan producto Yeso o materias primas; no se crean las LdM')
            return
        for xmlid, code, bolsas in BOMS:
            if Bom.search_count([('code', 'like', code)]):
                continue
            try:
                with self.env.cr.savepoint():
                    valor = self.env.ref(xmlid)
                    variante = tmpl.product_variant_ids.filtered(
                        lambda v: valor in v.product_template_attribute_value_ids.product_attribute_value_id)[:1]
                    if not variante:
                        continue
                    Bom.create({
                        'product_tmpl_id': tmpl.id,
                        'product_id': variante.id,
                        'product_qty': bolsas,
                        'code': code,
                        'jjsumi_version': '1.0',
                        'bom_line_ids': [
                            (0, 0, {'product_id': piedra.id, 'product_qty': 1.0}),
                            (0, 0, {'product_id': comb.id, 'product_qty': 1.0}),
                            (0, 0, {'product_id': bolsa.id, 'product_qty': float(bolsas)}),
                        ],
                    })
                    costo = COSTO_CARGA_PIEDRA + COSTO_CILINDRO + COSTO_EMPAQUE * bolsas
                    variante.standard_price = round(costo / bolsas, 2)
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo crear la LdM %s', code)

    # -- centros de trabajo ------------------------------------------------
    def _seed_centros_trabajo(self):
        Wc = self.env['mrp.workcenter']
        for code, name, costo, eff, setup, stop in CENTROS_TRABAJO:
            if Wc.search_count([('code', '=', code)]):
                continue
            try:
                with self.env.cr.savepoint():
                    Wc.create({
                        'name': name,
                        'code': code,
                        'costs_hour': costo,
                        'time_efficiency': eff,
                        'time_start': setup,
                        'time_stop': stop,
                    })
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo crear el centro %s', code)

    def _wc_por_codigo(self, familia, linea):
        if familia == 'PALET':
            code = 'WC-PALET'
        else:
            code = 'WC-%s-%s' % (familia, linea)
        return self.env['mrp.workcenter'].search([('code', '=', code)], limit=1)

    # -- operaciones en LdM ------------------------------------------------
    def _seed_operaciones_bom(self):
        boms = self.env['mrp.bom'].search([('code', 'like', 'JJ-YESO-%')])
        for bom in boms:
            if bom.operation_ids:
                continue
            lineas = LINEA_POR_BOM.get(bom.code, {})
            vals = []
            for seq, (nombre, minutos, familia) in enumerate(OPERACIONES, start=1):
                wc = self._wc_por_codigo(familia, lineas.get(familia, ''))
                if not wc:
                    continue
                vals.append((0, 0, {
                    'name': nombre,
                    'workcenter_id': wc.id,
                    'sequence': seq * 10,
                    'time_mode': 'manual',
                    'time_cycle_manual': minutos,
                }))
            if not vals:
                continue
            try:
                with self.env.cr.savepoint():
                    bom.write({'operation_ids': vals})
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudieron crear operaciones para %s', bom.code)

    # -- inventario inicial ------------------------------------------------
    def _seed_inventario_inicial(self):
        location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
        if not location:
            location = self.env['stock.location'].search(
                [('usage', '=', 'internal'), ('complete_name', '=', 'WH/Stock')], limit=1)
        if not location:
            _logger.warning('JJSumi: no se encontró WH/Stock; no se carga inventario')
            return
        Quant = self.env['stock.quant']
        for code, qty in INVENTARIO_INICIAL:
            prod = self.env['product.product'].search([('default_code', '=', code)], limit=1)
            if not prod:
                continue
            try:
                with self.env.cr.savepoint():
                    actual = sum(Quant.search([
                        ('product_id', '=', prod.id),
                        ('location_id', '=', location.id),
                    ]).mapped('quantity'))
                    if actual >= qty * 0.9:
                        continue
                    Quant._update_available_quantity(prod, location, qty - actual)
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo cargar inventario de %s', code)

    # -- órdenes de fabricación ------------------------------------------------
    def _limpiar_mos_rotas(self):
        """Borra MOs del seed que quedaron cancel por pre-setear el move finished.

        El bug marcaba el move finished con quantity/picked antes de
        button_mark_done; qty_produced computaba completo, _post_inventory
        dejaba quantity=0 y _action_done cancelaba el move → MO en cancel.
        Esas MOs llevan jjsumi_combustible_real (se escribe tras el done).
        """
        rotas = self.env['mrp.production'].search([
            ('origin', '=', ORIGIN_SEED),
            ('state', '=', 'cancel'),
            ('jjsumi_combustible_real', '!=', False),
        ])
        if not rotas:
            return
        n_ok = 0
        for mo in rotas:
            try:
                with self.env.cr.savepoint():
                    mo.workorder_ids.unlink()
                    mo.unlink()
                    n_ok += 1
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo limpiar MO rota #%s', mo.id)
        _logger.info('JJSumi: limpiadas %s/%s MOs rotas del seed', n_ok, len(rotas))

    def _seed_ordenes_fabricacion(self):
        from collections import Counter
        Mo = self.env['mrp.production']
        existentes = Counter(Mo.search([('origin', '=', ORIGIN_SEED)]).mapped('state'))
        # estado deseado -> cantidad total
        deseado = {'done': 16, 'progress': 4, 'confirmed': 3, 'draft': 2, 'cancel': 1}
        faltan = sum(max(n - existentes.get(e, 0), 0) for e, n in deseado.items())
        if faltan <= 0:
            return
        boms = self.env['mrp.bom'].search([('code', 'like', 'JJ-YESO-%')], order='code')
        if not boms:
            _logger.warning('JJSumi: no hay LdM; no se crean órdenes de fabricación')
            return
        hoy = fields.Date.context_today(self)
        plan = []
        # fechas de las done: índice = cuántas ya existen + nuevas
        idx_done = existentes.get('done', 0)
        for i in range(max(deseado['done'] - idx_done, 0)):
            plan.append(('done', boms[(idx_done + i) % len(boms)],
                         hoy - timedelta(days=5 + (idx_done + i) * 5)))
        for estado, base_offset in (('progress', 0), ('confirmed', 0), ('draft', 0), ('cancel', 0)):
            n_nuevas = max(deseado[estado] - existentes.get(estado, 0), 0)
            ya = existentes.get(estado, 0)
            for i in range(n_nuevas):
                if estado == 'progress':
                    fecha = hoy - timedelta(days=2)
                elif estado == 'confirmed':
                    fecha = hoy
                elif estado == 'draft':
                    fecha = hoy + timedelta(days=7)
                else:  # cancel
                    fecha = hoy - timedelta(days=15)
                plan.append((estado, boms[(ya + i) % len(boms)], fecha))

        for estado, bom, fecha in plan:
            try:
                with self.env.cr.savepoint():
                    self._crear_mo(estado, bom, fecha)
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo crear MO %s / %s', estado, bom.code)

    def _crear_mo(self, estado, bom, fecha):
        Mo = self.env['mrp.production']
        product = bom.product_id
        if not product:
            product = bom.product_tmpl_id.product_variant_ids[:1]
        fecha_dt = fields.Datetime.to_datetime(fecha) + timedelta(hours=8)
        mo = Mo.create({
            'product_id': product.id,
            'bom_id': bom.id,
            'product_qty': bom.product_qty,
            'date_start': fecha_dt,
            'origin': ORIGIN_SEED,
        })
        if estado == 'draft':
            return mo
        mo.action_confirm()
        if estado == 'cancel':
            mo.action_cancel()
            return mo
        if estado == 'confirmed':
            return mo
        if estado == 'progress':
            mo.qty_producing = mo.product_qty * 0.4
            return mo
        if estado == 'done':
            for move in mo.move_raw_ids:
                move.write({'quantity': move.product_uom_qty, 'picked': True})
            # No pre-setear move_finished: qty_produced se computa desde sus
            # picks; si va completo, _post_inventory deja quantity=0 y
            # _action_done cancela el move (MO termina en cancel).
            mo.qty_producing = mo.product_qty
            mo.with_context(skip_consumption=True, skip_backorder=True).button_mark_done()
            if mo.state != 'done':
                raise RuntimeError('button_mark_done no dejó la MO en done (state=%s)' % mo.state)
            mo.write({
                'jjsumi_combustible_real': 1.0 + (mo.id % 2),
                'jjsumi_merma_bolsas': mo.id % 9,
            })
            # force_date: Odoo bloquea mover fechas de una MO done/cancel
            mo.with_context(force_date=True).write({
                'date_start': fecha_dt,
                'date_finished': fecha_dt + timedelta(hours=2),
            })
        return mo

    # -- controles de calidad ------------------------------------------------
    def _seed_calidad(self):
        Cal = self.env['jjsumi.calidad']
        # Idempotencia: el seed crea 18 controles; si ya existen, no se repite
        if Cal.search_count([]) >= 18:
            return
        mos_done = self.env['mrp.production'].search([
            ('origin', '=', ORIGIN_SEED),
            ('state', '=', 'done'),
        ], order='date_finished')
        if not mos_done:
            _logger.warning('JJSumi: no hay MOs terminadas; no se crean controles de calidad')
            return
        # peso nominal por variante (kg)
        nominal = {1: 30.0, 2: 26.0, 3: 23.0}
        # (índice de MO, peso medido, humedad, fraguado, obs) — None = sin vincular
        casos = [
            (0, 22.8, 0.5, 42.0, 'Lote conforme'),
            (1, 26.2, 0.6, 38.0, 'Lote conforme'),
            (2, 29.8, 0.4, 45.0, 'Lote conforme'),
            (3, 23.1, 0.7, 40.0, 'Lote conforme'),
            (4, 20.5, 0.5, 50.0, 'Rechazado: peso fuera de tolerancia'),
            (5, 26.0, 1.4, 36.0, 'Rechazado: exceso de humedad en báscula 2'),
            (6, 30.3, 0.6, 41.0, 'Lote conforme'),
            (7, 22.6, 0.8, 44.0, 'Lote conforme'),
            (8, 26.4, 0.5, 39.0, 'Lote conforme'),
            (9, 29.5, 0.9, 47.0, 'Lote conforme'),
            (10, 23.4, 1.6, 43.0, 'Rechazado: exceso de humedad'),
            (11, 25.8, 0.4, 37.0, 'Lote conforme'),
            (12, 30.8, 0.7, 46.0, 'Lote conforme'),
            (13, 21.0, 0.6, 48.0, 'Rechazado: peso fuera de tolerancia'),
            (14, 23.0, 0.5, 40.0, 'Lote conforme'),
            (15, 26.1, 0.8, 42.0, 'Lote conforme'),
            (None, 0.0, 0.0, 0.0, 'Pendiente de báscula — material de entrada'),
            (None, 0.0, 0.0, 0.0, 'Pendiente de muestreo en almacén'),
        ]
        inspector = self.env.user
        for idx, peso, hum, frag, obs in casos:
            try:
                with self.env.cr.savepoint():
                    mo = mos_done[idx] if idx is not None else None
                    product = mo.product_id if mo else None
                    if not product:
                        product = self.env['product.product'].search([
                            ('product_tmpl_id', '=', self.env.ref('jjsumi_base.product_template_yeso').id),
                        ], limit=1)
                    nom = nominal.get(product.id, 23.0)
                    Cal.create({
                        'production_id': mo.id if mo else False,
                        'product_id': product.id,
                        'fecha': mo.date_finished.date() if mo and mo.date_finished else fields.Date.context_today(self),
                        'inspector_id': inspector.id,
                        'peso_nominal': nom,
                        'peso_medido': peso,
                        'humedad': hum,
                        'tiempo_fraguado': frag,
                        'observaciones': obs,
                    })
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se pudo crear control de calidad #%s', idx)

    # -- mantenimiento ------------------------------------------------------
    def _seed_mantenimiento(self):
        if 'maintenance.equipment' not in self.env:
            return
        Cat = self.env['maintenance.equipment.category']
        Eq = self.env['maintenance.equipment']
        Req = self.env['maintenance.request']
        Stage = self.env['maintenance.stage']
        stage_new = Stage.search([], order='sequence', limit=1)
        stage_done = Stage.search([('done', '=', True)], order='sequence', limit=1)
        stage_progress = Stage.search([('done', '=', False), ('sequence', '>', stage_new.sequence)],
                                      order='sequence', limit=1) if stage_new else stage_new

        equipos = {}
        for nombre, categoria, periodo in EQUIPOS_MANT:
            equipo = Eq.search([('name', '=', nombre)], limit=1)
            if not equipo:
                try:
                    with self.env.cr.savepoint():
                        cat = Cat.search([('name', '=', categoria)], limit=1) or Cat.create({'name': categoria})
                        equipo = Eq.create({'name': nombre, 'category_id': cat.id})
                except Exception:  # noqa: BLE001
                    _logger.exception('JJSumi: no se pudo crear el equipo %s', nombre)
                    continue
            equipos[nombre] = (equipo, periodo)

        # Preventivas recurrentes (una por equipo; las existentes se omiten por nombre)
        for nombre, (equipo, periodo) in equipos.items():
            prev_name = 'Mantenimiento preventivo - %s' % nombre
            if Req.search_count([('name', '=', prev_name)]):
                continue
            try:
                with self.env.cr.savepoint():
                    Req.create({
                        'name': prev_name,
                        'equipment_id': equipo.id,
                        'maintenance_type': 'preventive',
                        'schedule_date': fields.Datetime.now() + timedelta(days=periodo),
                        'recurring_maintenance': True,
                        'repeat_interval': periodo,
                        'repeat_unit': 'day',
                        'repeat_type': 'forever',
                    })
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se creó preventiva para %s', nombre)

        # Correctivas pasadas (Repaired) y abiertas; idempotentes por nombre
        correctivas = [
            # (nombre, equipo, días atrás, hecho, etapa)
            ('Fuga de gas en horno — sellado de quemador', 'Horno / calcinador', 45, True, None),
            ('Cambio de rodamientos del molino', 'Molino / trituradora', 30, True, None),
            ('Reparación de suspensión del vehículo', 'Vehículo de reparto', 20, True, None),
            ('Ruptura de correa — línea de envasado', 'Línea de envasado 1', 3, False, 'new'),
            ('Fuga de aire en compresor', 'Compresor de aire', 1, False, 'progress'),
            ('Batería del montacargas no carga', 'Montacargas eléctrico', -2, False, 'new'),
        ]
        hoy = fields.Date.context_today(self)
        for nombre, eq_name, dias, hecho, abierto in correctivas:
            if Req.search_count([('name', '=', nombre)]):
                continue
            equipo, _p = equipos.get(eq_name, (False, 0))
            if not equipo:
                continue
            try:
                with self.env.cr.savepoint():
                    fecha = fields.Datetime.now() - timedelta(days=dias)
                    if hecho:
                        Req.create({
                            'name': nombre,
                            'equipment_id': equipo.id,
                            'maintenance_type': 'corrective',
                            'schedule_date': fecha,
                            'stage_id': stage_done.id if stage_done else False,
                            'close_date': hoy - timedelta(days=max(dias - 2, 1)),
                        })
                    else:
                        Req.create({
                            'name': nombre,
                            'equipment_id': equipo.id,
                            'maintenance_type': 'corrective',
                            'schedule_date': fecha,
                            'stage_id': (stage_progress if abierto == 'progress' and stage_progress else stage_new).id
                            if (stage_progress or stage_new) else False,
                        })
            except Exception:  # noqa: BLE001
                _logger.exception('JJSumi: no se creó correctiva %s', nombre)
