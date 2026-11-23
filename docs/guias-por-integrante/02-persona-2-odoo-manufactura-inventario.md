# Persona 2 — Manufactura, Calidad, Mantenimiento e Inventario (Odoo 19)

> **Alcance:** Gestión de planta industrial (Lista de Materiales del yeso), control de calidad, mantenimiento de equipos, control de almacenes/stock y logística de reparto en Odoo 19.

---

## 1. Módulos y Archivos Bajo tu Responsabilidad

| Módulo (`odoo-custom-addons/`) | Qué hace | Archivos clave |
|---|---|---|
| `jjsumi_manufacturing` | Órdenes de manufactura (LdM del yeso), registro de calidad en planta (`calidad.py`) y mantenimiento (`mantenimiento.py`). | `models/mrp.py`, `models/calidad.py`, `models/mantenimiento.py`, `views/manufacturing_views.xml` |
| `jjsumi_quality_ext` | Extensiones para inspecciones y aprobaciones de calidad. | `models/`, `views/` |
| `jjsumi_maintenance_ext` | Extensiones para mantenimiento preventivo/correctivo de equipos y flota. | `models/`, `views/` |
| `jjsumi_catalog_ext` | Carga y estructura de productos, insumos y categorías del catálogo industrial. | `models/catalog_loader.py`, `models/catalog_data.py` |
| `jjsumi_delivery` | Control de vehículos (`vehiculo.py`) y programación/seguimiento de repartos (`reparto.py`). | `models/reparto.py`, `models/vehiculo.py`, `views/delivery_views.xml` |
| `jjsumi_distribution` | Gestión de flota de distribución (`fleet.py`). | `models/fleet.py`, `views/fleet_views.xml` |
| Conexión Stock → BSC / n8n | Al validar movimientos (`stock.picking.button_validate`), se actualizan `K19` (quiebres de stock), `K20` (valorización) y se dispara alerta en n8n si un producto queda `<= 0`. | `jjsumi_bsc_sync/models/bsc_sync.py`, `jjsumi_n8n/models/stock_picking.py` |

---

## 2. Flujos Principales

### Flujo A: Producción de Yeso y Control de Calidad
```
Orden de Producción (mrp.production)
  ──▶ Consumo de materia prima (stock)
  ──▶ Producto terminado
  ──▶ Inspección de Calidad (jjsumi_manufacturing / jjsumi_quality_ext)
  ──▶ Lote aprobado / rechazado
```

### Flujo B: Movimientos de Inventario, Reparto y Alertas
```
Entrega o Recepción (stock.picking) ──▶ [Validar]
  ├─ Actualiza saldos en stock.quant
  ├─ Asigna vehículo / ruta en jjsumi_delivery (reparto.py)
  ├─ Sincroniza con BSC: Quiebres de Stock (K19) y Valorización (K20)
  └─ Si qty_available <= 0 ──▶ Evento inventory.stock.low hacia n8n (alerta por correo)
```

---

## 3. Guion de Presentación (3–5 minutos)

1. **Apertura:** *"Mi módulo cubre toda la cadena operativa: desde la fabricación del yeso, control de calidad y mantenimiento de planta, hasta el control de inventario por sucursal y la logística de reparto."*
2. **Demo 1 — Catálogo e Inventario (`Inventario`):** Muestra los productos almacenables, las ubicaciones por sucursal (Juliaca, Puno, Arequipa, Cusco, Tacna) y el stock disponible (`stock.quant`). Explica que cada movimiento validado recalcula automáticamente la valorización del inventario y detecta quiebres de stock.
3. **Demo 2 — Manufactura y Calidad (`Fabricación`):** Muestra una Lista de Materiales (LdM) / Orden de Producción del yeso y los registros de control de calidad y mantenimiento preventivo.
4. **Demo 3 — Distribución y Reparto (`Reparto / Flota`):** Muestra los vehículos registrados (`jjsumi.vehiculo`) y las órdenes de reparto (`jjsumi.reparto`) con sus zonas de entrega.
5. **Cierre:** *"Cuando un almacén se queda sin stock tras una entrega, Odoo avisa inmediatamente a n8n para enviar una alerta de reposición y actualiza el semáforo de inventario en el BSC."*

---

## 4. Comandos y Verificación Técnica (Servidor y Base de Datos)

### Verificar módulos de operaciones instalados en PostgreSQL (`jjsumi`)
```bash
sudo -u postgres psql -d jjsumi -c "
SELECT name, state, latest_version
FROM ir_module_module
WHERE name IN ('jjsumi_manufacturing','jjsumi_quality_ext','jjsumi_maintenance_ext','jjsumi_delivery','jjsumi_distribution','jjsumi_catalog_ext','stock','mrp')
ORDER BY name;"
```

### Consultar Stock, Valorización y Movimientos en BD (`jjsumi`)
```bash
# Stock disponible por sucursal/compañía en ubicaciones internas
sudo -u postgres psql -d jjsumi -c "
SELECT q.company_id, COUNT(DISTINCT q.product_id) AS productos, ROUND(SUM(q.quantity)::numeric, 2) AS unidades_totales
FROM stock_quant q
JOIN stock_location l ON l.id = q.location_id
WHERE l.usage = 'internal'
GROUP BY q.company_id
ORDER BY q.company_id;"

# Últimos movimientos de almacén validados (stock.picking)
sudo -u postgres psql -d jjsumi -c "
SELECT id, name, state, company_id, scheduled_date
FROM stock_picking
ORDER BY id DESC LIMIT 10;"

# Órdenes de fabricación (mrp.production)
sudo -u postgres psql -d jjsumi -c "
SELECT state, COUNT(*) FROM mrp_production GROUP BY state;"
```

### Prueba rápida en consola Python de Odoo (`odoo-bin shell`)
```bash
sudo -u odoo /opt/odoo19/venv/bin/python /opt/odoo19/odoo/odoo-bin shell -c /etc/odoo19.conf -d jjsumi --no-http << 'EOF'
print("Productos:", env['product.product'].search_count([]))
print("Quants internos:", env['stock.quant'].search_count([('location_id.usage','=','internal')]))
print("Vehículos:", env['jjsumi.vehiculo'].search_count([]) if 'jjsumi.vehiculo' in env else 'N/A')
EOF
```
