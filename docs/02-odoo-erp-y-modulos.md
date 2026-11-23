# 02 — Odoo 19 ERP y Módulos Personalizados (`jjsumi_*`)

La instancia de Odoo 19 Community utiliza la base de datos PostgreSQL `jjsumi` y se extiende mediante **26 módulos personalizados** ubicados en `/opt/odoo19/custom-addons`.

---

## Estructura Multi-Sucursal

El sistema opera con una empresa matriz y cinco sucursales mapeadas directamente con el BSC:

| ID Compañía Odoo | ID Empresa BSC | Nombre |
|---|---|---|
| Consolidado / Matriz | `jjsumi` | JJSUMI (Consolidado) |
| `7` | `jjsumi-juliaca` | Sucursal Juliaca |
| `8` | `jjsumi-puno` | Sucursal Puno |
| `9` | `jjsumi-arequipa` | Sucursal Arequipa |
| `10` | `jjsumi-cusco` | Sucursal Cusco |
| `11` | `jjsumi-tacna` | Sucursal Tacna |

---

## Catálogo de Módulos Personalizados

### 1. Finanzas, Compras y Cumplimiento Tributario (Perú)
- **`jjsumi_accounting`**: Extiende la contabilidad peruana (`account`, `l10n_pe`, `hr_expense`) con dos modelos propios:
  - `jjsumi.documento` (`models/documento.py`): Repositorio documental por carpetas (`ventas`, `compras`, `produccion`, `legal`, `laboral`, `otros`) con adjuntos y fecha de vencimiento.
  - `jjsumi.hoja` y `jjsumi.hoja.linea` (`models/hoja.py`): Hojas de cálculo internas para costos de producción, presupuestos y flujo de caja con cálculo automático de ingresos, egresos, resultado y margen.
- **`jjsumi_purchase_ext`**: Control interno y validación de 3 vías en compras (`models/purchase_order.py`):
  - Impide que un usuario apruebe una orden de compra creada por él mismo.
  - Exige aprobación de jefe de sucursal o gerencia para órdenes `> S/ 5,000` y exclusivamente del Gerente General/Admin para órdenes `> S/ 20,000`.
  - Al publicar facturas de proveedor (`account.move`), bloquea desviaciones de precio `> 5%` frente a la orden de compra salvo autorización de Contador o Administrador.
- **`jjsumi_reniec`**: Integración de validación de identidad tributaria (`l10n_pe`, `l10n_latam_base`):
  - Valida el dígito verificador de RUC (11 dígitos) y DNI (8 dígitos).
  - Consulta API externa (`apis.net.pe`) o caché/modo pruebas determinístico, almacenando el resultado en `res.partner.jjsumi_reniec_estado` (ej. `"Verificado SUNAT - Activo / Habido"`).

### 2. Inventario, Producción, Calidad y Logística
- **`jjsumi_manufacturing`**: Gestión de producción (LdM del yeso), calidad (`calidad.py`) y mantenimiento (`mantenimiento.py`).
- **`jjsumi_quality_ext`**: Extensiones de control de calidad en planta.
- **`jjsumi_maintenance_ext`**: Extensiones de mantenimiento preventivo de planta y equipos.
- **`jjsumi_delivery`**: Gestión de vehículos (`vehiculo.py`) y repartos (`reparto.py`).
- **`jjsumi_distribution`**: Gestión de flota de distribución (`fleet.py`).
- **`jjsumi_catalog_ext`**: Carga y validación de catálogo de productos y proveedores con RUC válido SUNAT.

### 3. Ventas, POS y CRM Operacional
- **`jjsumi_sales`**: Extiende ventas y el **CRM Operacional** nativo de Odoo (`crm.lead`):
  - En `crm_lead.py` agrega `bolsas_estimadas` y `delivery_zone` (`local` / `intercity`).
  - Gestiona lógica de márgenes (`profit`), bonificaciones y aprobaciones de descuentos en `sale.order`.
- **`jjsumi_pos_ext`**: Extensiones para órdenes de Punto de Venta (`pos.order`).
- **`jjsumi_site`**: Portal web comercial y consulta de pedidos/boletas para clientes.

### 4. Integración, Seguridad y Experiencia de Usuario
- **`jjsumi_bsc_sync`**: Conector en tiempo real hacia el BSC (`models/bsc_sync.py`).
  - Lee URL (`jjsumi_bsc.sync_url`) y secreto (`jjsumi_bsc.sync_secret`) desde `ir.config_parameter`.
  - Calcula métricas del trimestre activo (ventas B2B, POS, CRM, Finanzas SUNAT/RENIEC e Inventario) y las envía vía `POST /bsc/sync-odoo` al confirmarse/cancelarse ventas, crearse tickets POS/clientes/leads, contabilizarse facturas (`account.move.action_post`) o validarse movimientos de inventario (`stock.picking.button_validate`).
- **`jjsumi_n8n`**: Despachador de webhooks hacia n8n (`models/n8n_dispatcher.py`).
  - Emite eventos desde `sale_order.py`, `crm_lead.py`, `account_move.py`, `purchase_order.py` y `stock_picking.py`.
- **`jjsumi_home_cards`**: Dashboard inicial en Odoo con botón de **Single Sign-On (SSO)** hacia `/bsc/` (`get_bsc_sso_url()`), firmando un JWT HS256 de 5 minutos con la empresa activa del usuario.
- **`jjsumi_security`**, **`jjsumi_approvals`**, **`jjsumi_audit`**, **`jjsumi_auth`**, **`jjsumi_base`**, **`jjsumi_core`**, **`jjsumi_hr_ext`**, **`jjsumi_marketing`**, **`jjsumi_menus`**, **`jjsumi_theme`**: Módulos transversales de roles, permisos, auditoría, menús, parámetros base y apariencia.
