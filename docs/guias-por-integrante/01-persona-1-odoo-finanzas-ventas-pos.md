# Persona 1 — Finanzas, Ventas B2B y Punto de Venta (Odoo 19)

> **Alcance:** Gestión financiera y tributaria peruana (`l10n_pe`), control interno de compras, validación SUNAT/RENIEC, ciclo de ventas B2B y Punto de Venta (POS) en Odoo 19.

---

## 1. Módulos y Archivos Bajo tu Responsabilidad

| Módulo (`odoo-custom-addons/`) | Qué hace | Archivos clave |
|---|---|---|
| `jjsumi_accounting` | Documentos financieros por carpetas (`jjsumi.documento`) y hojas de costos/presupuestos/flujo (`jjsumi.hoja`) sobre `account` y `l10n_pe`. | `models/documento.py`, `models/hoja.py`, `views/` |
| `jjsumi_purchase_ext` | Reglas de aprobación en compras (`> S/ 5,000` jefe/gerencia, `> S/ 20,000` Gerente General, prohíbe auto-aprobación) y **validación de 3 vías** (bloquea facturas de proveedor con desviación `> 5%` sobre la OC). | `models/purchase_order.py` |
| `jjsumi_reniec` | Validación de dígito verificador RUC (11 dígitos) / DNI (8 dígitos) y consulta SUNAT/RENIEC (`apis.net.pe` o caché/modo pruebas), guardando `jjsumi_reniec_estado`. | `models/res_partner.py`, `models/res_config_settings.py` |
| `jjsumi_sales` | Ventas B2B (`sale.order`), zonas de entrega (`local` / `intercity`), control de bolsas bonificadas, márgenes (`profit`) y aprobaciones de descuentos. | `models/sale_order.py`, `models/jjsumi_ext.py` |
| `jjsumi_pos_ext` | Extensiones operativas para órdenes de mostrador en Punto de Venta (`pos.order`). | `models/pos_order.py` |
| `jjsumi_approvals` | Flujos transversales de aprobación. | `models/`, `views/` |

---

## 2. Flujos Principales

### Flujo A: Venta B2B + Validación SUNAT/RENIEC + Facturación (`l10n_pe`)
```
Cliente (RUC/DNI) ──▶ [Botón Consultar RENIEC/SUNAT] ──▶ Estado "Activo / Habido"
        │
        ▼
Cotización / Pedido B2B (sale.order) ──▶ [Confirmar] ──▶ Dispara sync al BSC + evento n8n
        │
        ▼
Factura Electrónica (account.move / l10n_pe) ──▶ [Publicar] ──▶ Calcula IGV (K14) y % RUC Habido (K15)
```

### Flujo B: Compra con Control Interno de 3 Vías
```
Orden de Compra (purchase.order)
  ├─ Creador intenta aprobar su propia OC ──▶ BLOQUEADO
  ├─ Monto > S/ 5,000  ──▶ Requiere Jefe de Sucursal / Gerencia
  └─ Monto > S/ 20,000 ──▶ Requiere Gerente General / Admin
        │
        ▼
Factura de Proveedor (account.move: in_invoice)
  ├─ Precio difiere > 5% de la OC ──▶ BLOQUEADO salvo Contador/Admin
  └─ Proveedor sin RUC Activo/Habido ──▶ Alerta Riesgo Fiscal SUNAT en n8n y BSC
```

### Flujo C: Punto de Venta (POS)
```
Apertura de Sesión POS ──▶ Venta en mostrador (pos.order) ──▶ Pago / Boleta
        │
        ▼
Al crearse pos.order ──▶ jjsumi_bsc_sync actualiza Facturación (K3) y Órdenes POS (K7)
```

---

## 3. Guion de Presentación (3–5 minutos)

1. **Apertura (Contexto):** *"Yo estuve a cargo del núcleo comercial y financiero en Odoo 19: Facturación peruana (`l10n_pe`), validación de identidad con SUNAT/RENIEC, control de compras, ventas B2B y Punto de Venta."*
2. **Demo 1 — RENIEC / SUNAT (`Contactos`):** Abre un cliente o proveedor, muestra el campo **RUC/DNI** y haz clic en **"Consultar RENIEC/SUNAT"**. Explica que esto alimenta el campo `Estado RENIEC/SUNAT` y evita perder crédito fiscal del IGV.
3. **Demo 2 — Ventas B2B y POS (`Ventas` / `Punto de Venta`):** Muestra un pedido confirmado en `Ventas` (con sucursal, zona de entrega y margen) y una orden en `Punto de Venta`, explicando que al confirmar/cobrar se actualizan en vivo los KPIs del BSC.
4. **Demo 3 — Finanzas y Control de Compras (`Contabilidad` / `Compras`):**
   - Muestra una factura en `Contabilidad` (`l10n_pe` con IGV 18% y tipo de comprobante 01 Factura / 03 Boleta / 07 Nota de Crédito).
   - Muestra en `jjsumi_accounting` las **Hojas de Costos/Presupuesto (`jjsumi.hoja`)** y **Documentos (`jjsumi.documento`)**.
   - Explica la regla de **validación de 3 vías** en compras (desviación > 5% y topes de S/ 5,000 y S/ 20,000).
5. **Cierre (Pase a Persona 2 o 3):** *"Todo lo que facturamos, vendemos o compramos aquí alimenta automáticamente los tableros de inventario/producción y el Balanced Scorecard."*

---

## 4. Comandos y Verificación Técnica (Servidor y Base de Datos)

### Verificar servicio Odoo 19 y puerto
```bash
systemctl status odoo19.service --no-pager
ss -tulpn | grep 8069
sudo journalctl -u odoo19.service -n 30 --no-pager
```

### Verificar módulos instalados en PostgreSQL (`jjsumi`)
```bash
sudo -u postgres psql -d jjsumi -c "
SELECT name, state, latest_version
FROM ir_module_module
WHERE name IN ('jjsumi_accounting','jjsumi_purchase_ext','jjsumi_reniec','jjsumi_sales','jjsumi_pos_ext','l10n_pe')
ORDER BY name;"
```

### Consultar registros reales de Finanzas, Ventas y POS en BD
```bash
# Resumen de facturas contabilizadas por tipo (01/03/07) y empresa
sudo -u postgres psql -d jjsumi -c "
SELECT company_id, move_type, COUNT(*) AS cantidad, ROUND(SUM(amount_total)::numeric, 2) AS total, ROUND(SUM(amount_tax)::numeric, 2) AS igv
FROM account_move
WHERE state = 'posted' AND move_type IN ('out_invoice','in_invoice','out_refund')
GROUP BY company_id, move_type
ORDER BY company_id, move_type;"

# Ventas B2B confirmadas y órdenes POS
sudo -u postgres psql -d jjsumi -c "
SELECT 'sale.order' AS origen, COUNT(*) AS cantidad, ROUND(SUM(amount_total)::numeric, 2) AS total FROM sale_order WHERE state = 'sale'
UNION ALL
SELECT 'pos.order' AS origen, COUNT(*) AS cantidad, ROUND(SUM(amount_total)::numeric, 2) AS total FROM pos_order WHERE state IN ('paid','done','invoiced');"

# Contactos verificados con RENIEC/SUNAT
sudo -u postgres psql -d jjsumi -c "
SELECT COALESCE(jjsumi_reniec_estado, 'Sin verificar') AS estado, COUNT(*)
FROM res_partner
GROUP BY 1 ORDER BY 2 DESC LIMIT 10;"
```

### Prueba rápida en consola Python de Odoo (`odoo-bin shell`)
```bash
sudo -u odoo /opt/odoo19/venv/bin/python /opt/odoo19/odoo/odoo-bin shell -c /etc/odoo19.conf -d jjsumi --no-http << 'EOF'
print("Facturas publicadas:", env['account.move'].search_count([('state','=','posted')]))
print("Hojas financieras:", env['jjsumi.hoja'].search_count([]))
print("Documentos:", env['jjsumi.documento'].search_count([]))
EOF
```
