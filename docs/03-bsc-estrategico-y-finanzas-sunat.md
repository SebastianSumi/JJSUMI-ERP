# 03 — Balanced Scorecard (BSC) y Tablero Finanzas & SUNAT

El sistema **BSC (`BSC-TechPeru-main`)** es una aplicación full-stack independiente conectada en tiempo real con Odoo 19.

---

## Stack Tecnológico

- **Backend (`/home/ubuntu/BSC-TechPeru-main/backend`):**
  - Framework: **NestJS 12** (TypeScript / ES Modules).
  - ORM y Base de Datos: **Prisma 6** sobre **PostgreSQL 16** (`bsc_techperu`).
  - Seguridad: Autenticación JWT (`passport-jwt`), guards de roles (`ADMIN`, `GERENTE`, `ANALISTA`, `RESPONSABLE`) y secreto dedicado para integración (`ODOO_SYNC_SECRET`).
- **Frontend (`/home/ubuntu/BSC-TechPeru-main/frontend`):**
  - Framework: **React 19** + **Vite 8** + **TypeScript**.
  - Estilos y Gráficos: **Tailwind CSS 4**, `lucide-react` y `recharts`.
  - Build desplegado en `/var/www/bsc` con `VITE_API_URL=/bsc-api`.

---

## Autenticación y Single Sign-On (SSO) desde Odoo

1. **Login tradicional (`POST /auth/login`):** Para acceso directo con email y contraseña.
2. **SSO desde Odoo (`POST /auth/sso`):** Cuando el usuario ingresa desde Odoo (`/bsc/?sso=<JWT>&empresa=<id>`), `AuthProvider` (`useAuth.tsx`) intercambia el token temporal por un `accessToken` de sesión en el BSC y activa automáticamente la sucursal correspondiente.
3. **Protección contra peticiones prematuras:** Los hooks `useEmpresa(!!usuario)` y `useBsc(..., !!usuario)` esperan a que la sesión esté autenticada antes de consultar `/empresas`, `/kpis` o `/resumen`, evitando errores `401` por condiciones de carrera.

---

## Catálogo de KPIs Sincronizados desde Odoo (`K1–K20`)

Cada sede (`jjsumi`, `jjsumi-juliaca`, `jjsumi-puno`, `jjsumi-arequipa`, `jjsumi-cusco`, `jjsumi-tacna`) cuenta con indicadores sincronizados automáticamente (`origenDatos = 'ODOO'`) junto con su fecha de última actualización (`ultimaSyncOdoo`):

### Indicadores Comerciales y de Clientes
- **`K1`:** Margen bruto promedio (`%`) — calculado sobre `sale.order` del trimestre.
- **`K2`:** Ventas B2B confirmadas (`pedidos`).
- **`K3`:** Facturación acumulada (`S/`) — suma de `sale.order` + `pos.order`.
- **`K5`:** Clientes activos en cartera (`res.partner`).
- **`K6`:** Tasa de conversión de cotizaciones CRM (`%`).
- **`K7`:** Órdenes atendidas en POS (`tickets`).

### Indicadores Financieros y Tributarios (SUNAT / RENIEC)
- **`K14` — IGV Neto Proyectado (SUNAT) (`S/`):** Calculado desde `account.move` (`l10n_pe`) como `IGV Ventas (01/03) - IGV Compras - IGV Notas de Crédito (07)`.
- **`K15` — Cumplimiento RUC Activo/Habido (`%`):** Cruza facturas emitidas y recibidas contra `res.partner.jjsumi_reniec_estado`. Alerta si existen operaciones con proveedores/clientes no validados (riesgo de crédito fiscal).
- **`K16` — Tasa de Notas de Crédito (`%`, inverso):** Ratio `out_refund / out_invoice` sobre el total facturado del trimestre.
- **`K17` — Cartera Vencida CxC > 30 días (`%`, inverso):** Saldo residual (`amount_residual`) de facturas vencidas hace más de 30 días respecto al total facturado.
- **`K18` — Desviación en Compras (> 5% sobre OC) (`%`, inverso):** Control de discrepancias en facturas de proveedor (`jjsumi_purchase_ext`).

### Indicadores de Inventario y Operaciones
- **`K19` — Quiebres de Stock (`%`, inverso):** Porcentaje de productos almacenables con saldo `<= 0` en `stock.quant`.
- **`K20` — Valorización de Inventario Activo (`S/`):** Suma de `cantidad * standard_price` en ubicaciones internas.

*(Además, los KPIs `K4`, `K8–K13` completan las perspectivas de Procesos y Aprendizaje).*

---

## Endpoints Clave de Integración y Auditoría

| Método y Ruta | Autenticación | Descripción |
|---|---|---|
| `POST /bsc/sync-odoo` | Header `x-jjsumi-secret` | Recibe métricas por empresa desde Odoo, actualiza `Kpi` y `Medicion` del periodo activo, cierra tareas si se cumple la meta y genera alertas `ODOO_SYNC` (`CRITICA`) si cae en estado crítico. Registra auditoría en `SyncOdooLog`. |
| `GET /bsc/sync-odoo/logs` | JWT (`ADMIN`, `GERENTE`, `ANALISTA`) | Devuelve el historial de sincronizaciones Odoo → BSC. |
| `GET /bsc/finanzas-sunat` | JWT | Devuelve el consolidado y comparativa por sucursal de los KPIs financieros, SUNAT/RENIEC e inventario. |
| `GET /bsc/n8n-resumen` | Header `x-jjsumi-secret` | Resumen ejecutivo + alertas críticas activas consumido por los workflows programados de n8n. |

---

## Módulos del Frontend (Vista Usuario Final)

- **Dashboard ejecutivo:** Resumen global, semáforo por perspectiva, gráfico Meta vs. Real y radar estratégico.
- **Finanzas & SUNAT (`FinanzasSunatPanel.tsx`):** Vista especializada con tarjetas de `K14–K20`, tabla comparativa entre las 6 sedes e historial en vivo de sincronizaciones `SyncOdooLog`.
- **Perspectivas (Financiera, Clientes, Procesos, Aprendizaje):** Tarjetas `KpiCard` con insignia `Odoo en vivo` y modal de detalle (`KpiModal`) para registrar mediciones o revisar acciones sugeridas.
- **Análisis y Gobierno:** Mapa Estratégico, Simulador de escenarios, Comparación entre periodos, Alertas, Desviaciones, Aprobaciones, Evidencias, Compromisos, Tareas, Reportes exportables y Panel de Administración.
