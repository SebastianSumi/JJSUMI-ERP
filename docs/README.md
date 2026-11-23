# Documentación Oficial — Ecosistema JJSUMI (Odoo 19 + BSC + n8n)

> **Audiencia:** Equipo de Desarrollo, Operaciones TI y Usuarios Finales (Gerencia, Finanzas, Compras y Almacén).  
> **Entorno:** Servidor AWS Linux (Ubuntu 24.04) con servicios nativos gestionados por `systemd`.

---

## Resumen Ejecutivo (Para Público Final)

El ecosistema **JJSUMI** integra tres plataformas en tiempo real para gestionar la operación diaria, el cumplimiento tributario (SUNAT/RENIEC) y el control estratégico de la empresa y sus 5 sucursales (**Juliaca, Puno, Arequipa, Cusco y Tacna**):

1. **Odoo 19 Community (ERP Operativo):** Centraliza ventas B2B, punto de venta (POS), compras con validación de 3 vías, facturación electrónica peruana (`l10n_pe`), consulta automática de RUC/DNI (`jjsumi_reniec`), manufactura, calidad, inventario y repartos.
2. **Balanced Scorecard — BSC (`BSC-TechPeru-main`):** Tablero estratégico ejecutivo conectado en tiempo real con Odoo. Mide el desempeño en 4 perspectivas (Financiera, Clientes, Procesos Internos y Aprendizaje) y cuenta con un módulo dedicado de **Finanzas & SUNAT** (proyección de IGV neto, riesgo fiscal por RUC, notas de crédito, cartera vencida y quiebres de stock).
3. **n8n (Automatización y Alertas):** Motor de flujos que recibe eventos de Odoo y consulta periódicamente al BSC para enviar notificaciones automáticas por correo electrónico (ventas altas, compras observadas, riesgo fiscal SUNAT, quiebres de stock y resúmenes ejecutivos diarios).

---

## Accesos Principales

| Sistema | URL de Acceso | Puerto Interno | Proxy Nginx |
|---|---|---|---|
| **Odoo 19 ERP** | `http://<IP-SERVIDOR>:8069` | `8069` | Directo |
| **BSC (Interfaz Web)** | `http://<IP-SERVIDOR>/bsc/` | Estático (`/var/www/bsc`) | `/bsc/` |
| **BSC (API Backend)** | `http://<IP-SERVIDOR>/bsc-api/` | `3000` | `/bsc-api/` |
| **n8n (Automatización)** | `http://<IP-SERVIDOR>/` | `5678` | `/` |

> **Nota:** Los usuarios autenticados en Odoo pueden ingresar al **BSC sin volver a iniciar sesión** mediante el botón de acceso directo (SSO) desde el panel principal de Odoo (`jjsumi_home_cards`).

---

## Índice de Documentación

| Documento | Contenido | Audiencia Principal |
|---|---|---|
| [01-arquitectura-e-infraestructura.md](./01-arquitectura-e-infraestructura.md) | Mapa de servidores, puertos, `systemd`, Nginx, PostgreSQL, SQLite, Node.js y backups. | Desarrollo / DevOps |
| [02-odoo-erp-y-modulos.md](./02-odoo-erp-y-modulos.md) | Catálogo completo de los 26 módulos `jjsumi_*`, Finanzas, Compras, RENIEC/SUNAT, Inventario, CRM y conectores. | Desarrollo / Consultores ERP |
| [03-bsc-estrategico-y-finanzas-sunat.md](./03-bsc-estrategico-y-finanzas-sunat.md) | Arquitectura NestJS + Prisma + React, SSO, modelo de datos, KPIs `K1–K20` y tablero Finanzas & SUNAT. | Desarrollo / Analistas |
| [04-n8n-automatizacion-y-notificaciones.md](./04-n8n-automatizacion-y-notificaciones.md) | Detalle de los 3 workflows activos, webhook de eventos Odoo, resúmenes diarios y alertas críticas. | Desarrollo / Operaciones |
| [05-operacion-mantenimiento-y-manual-usuario.md](./05-operacion-mantenimiento-y-manual-usuario.md) | Guía paso a paso para usuarios finales, comandos de administración, despliegues y respaldo. | Público Final / Soporte TI |
| [06-guia-visual-y-recursos.md](./06-guia-visual-y-recursos.md) | Paleta corporativa, hojas de estilo consolidadas, íconos y diagramas visuales. | Diseño / Desarrollo / Público Final |
