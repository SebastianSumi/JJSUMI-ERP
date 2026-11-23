# 04 — Automatización y Notificaciones con n8n

**n8n** se ejecuta como servicio `systemd` (`n8n.service`) en el puerto `5678` (accesible en `/` vía Nginx), con zona horaria `America/Lima` y persistencia en `/home/ubuntu/.n8n/database.sqlite`.

Los archivos fuente de los workflows se encuentran versionados en `/home/ubuntu/JJSUMI-ERP/n8n-workflows/`.

---

## Workflows Activos en Producción

### 1. `jjsumiOdooEventos1` — Enrutador de Eventos en Tiempo Real
- **Archivo:** `/home/ubuntu/JJSUMI-ERP/n8n-workflows/jjsumi_odoo_eventos.json`
- **Disparador:** Webhook `POST /webhook/jjsumi-odoo` (invocado por `jjsumi.n8n.dispatcher` en Odoo) + Formulario web de feedback (`On form submission`).
- **Eventos soportados y acciones:**

| Evento (`body.event`) | Origen en Odoo | Acción en n8n |
|---|---|---|
| `sale.order.confirmed` | `sale.order.action_confirm` | Si `amount_total >= 5000`, envía alerta a Gerencia por correo (`Gmail SMTP JJSUMI`) y luego envía correo de confirmación al cliente. |
| `sale.order.discount_approved` | `sale.order.action_jjsumi_aprobar_descuento` | Envía confirmación del pedido al cliente. |
| `crm.lead.created` | `crm.lead.create` | Enruta el nuevo lead (conexión disponible para Google Sheets). |
| `finance.sunat.risk` | `account.move.action_post` (`in_invoice`) | Cuando una factura de compra pertenece a un proveedor sin estado Activo/Habido en `jjsumi_reniec`, envía alerta inmediata **`[RIESGO FISCAL SUNAT]`** indicando el IGV en riesgo. |
| `finance.credit_note.posted` | `account.move.action_post` (`out_refund`) | Envía notificación **`[FINANZAS] Nota de Crédito emitida`** con monto e IGV. |
| `purchase.order.high_amount` | `purchase.order.button_confirm` | Para órdenes de compra `>= S/ 5,000`, envía alerta **`[COMPRAS] Orden >= S/ 5,000 requiere revisión`**. |
| `inventory.stock.low` | `stock.picking.button_validate` | Si un movimiento deja productos con `qty_available <= 0`, envía alerta **`[INVENTARIO] Quiebre de stock detectado`** listando los productos afectados. |

---

### 2. `jjsumiBscCierreDiario1` — Cierre y Resumen Ejecutivo Diario
- **Archivo:** `/home/ubuntu/JJSUMI-ERP/n8n-workflows/jjsumi_bsc_cierre_diario.json`
- **Disparador:** `Schedule Trigger` diario a las **23:00 (`America/Lima`)**.
- **Flujo:**
  1. Consulta `GET http://127.0.0.1:3000/bsc/n8n-resumen` con cabecera `x-jjsumi-secret`.
  2. Consolida en un nodo `Code` los indicadores de todas las sedes (Ventas, Margen, IGV Neto, % RUC Habido, CxC Vencida, Quiebre de Stock e Inventario Valorizado).
  3. Envía el **Resumen Ejecutivo Diario BSC JJSUMI** por correo electrónico a Gerencia.

---

### 3. `jjsumiBscMonitorAlertas1` — Monitor de Alertas Críticas
- **Archivo:** `/home/ubuntu/JJSUMI-ERP/n8n-workflows/jjsumi_bsc_monitor_alertas.json`
- **Disparador:** `Schedule Trigger` cada **6 horas**.
- **Flujo:**
  1. Consulta `GET http://127.0.0.1:3000/bsc/n8n-resumen`.
  2. Evalúa `totalAlertasCriticas > 0`.
  3. Si existen alertas críticas en estado `NUEVA` o `RECONOCIDA`, formatea el listado por sucursal y envía un correo urgente **`[URGENTE BSC] Alertas Críticas Activas`**.
