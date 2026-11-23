# Persona 3 — Balanced Scorecard (BSC), n8n y Finanzas SUNAT en el BSC

> **Alcance:** Arquitectura del BSC (NestJS + Prisma + React), Single Sign-On (SSO) desde Odoo, sincronización en tiempo real (`jjsumi_bsc_sync`), tablero **Finanzas & SUNAT** y automatización de alertas/reportes con **n8n**.

---

## 1. Componentes y Archivos Bajo tu Responsabilidad

| Componente | Ruta | Función principal |
|---|---|---|
| **Conector Odoo → BSC** | `odoo-custom-addons/jjsumi_bsc_sync/models/bsc_sync.py` | Calcula métricas del trimestre activo (Ventas, POS, CRM, **IGV Neto**, **% RUC Activo/Habido**, **Notas de Crédito**, **CxC vencida**, **Quiebres de stock**, **Valorización**) y hace `POST /bsc/sync-odoo`. |
| **Emisor Odoo → n8n** | `odoo-custom-addons/jjsumi_n8n/models/` | Emite webhooks en ventas, CRM, facturas (`account_move.py`), compras altas (`purchase_order.py`) y quiebres de stock (`stock_picking.py`). |
| **Backend BSC** | `bsc/backend/src/bsc/bsc.controller.ts` y `bsc.service.ts` | Expone `POST /bsc/sync-odoo`, `GET /bsc/sync-odoo/logs`, `GET /bsc/finanzas-sunat` y `GET /bsc/n8n-resumen`; genera alertas `ODOO_SYNC` automáticas y audita en `SyncOdooLog`. |
| **Frontend BSC** | `bsc/frontend/src/components/FinanzasSunatPanel.tsx`, `KpiCard.tsx`, `useAuth.tsx`, `useBsc.ts` | Interfaz ejecutiva, insignia `Odoo en vivo`, comparativa entre las 6 sedes y flujo SSO sin errores 401. Build desplegado en `/var/www/bsc`. |
| **Workflows n8n** | `n8n-workflows/*.json` | 3 workflows activos: `jjsumiOdooEventos1` (7 rutas), `jjsumiBscCierreDiario1` (23:00 diario) y `jjsumiBscMonitorAlertas1` (cada 6h). |

---

## 2. Flujos Principales

### Flujo A: Sincronización en Tiempo Real Odoo → BSC
```
Evento en Odoo (Venta, POS, Factura, Stock)
  ──▶ jjsumi.bsc.sync.push_realtime()
  ──▶ POST http://127.0.0.1:3000/bsc/sync-odoo (Header: x-jjsumi-secret)
  ──▶ BSC actualiza Kpi + Medicion del trimestre activo
  ├─ Si cumple meta ──▶ Marca tareas vinculadas como COMPLETADA
  ├─ Si estado == critico ──▶ Crea Alerta CRITICA (ODOO_SYNC) sin duplicados
  └─ Registra auditoría en SyncOdooLog
```

### Flujo B: Orquestación y Notificaciones en n8n
```
1. Tiempo real: Odoo ──▶ Webhook /webhook/jjsumi-odoo ──▶ Switch (7 eventos) ──▶ Correo SMTP
   (Ventas >= 5000, Riesgo Fiscal SUNAT, Notas de Crédito, Compras >= 5000, Quiebre de Stock)
2. Diario 23:00: Cron n8n ──▶ GET /bsc/n8n-resumen ──▶ Resumen Ejecutivo 6 sedes por correo
3. Cada 6 horas: Cron n8n ──▶ GET /bsc/n8n-resumen ──▶ Si alertasCriticas > 0 ──▶ Correo urgente
```

---

## 3. Guion de Presentación (3–5 minutos)

1. **Apertura:** *"Yo conecté la operación de Odoo con la capa estratégica y de automatización: el Balanced Scorecard (BSC) y n8n."*
2. **Demo 1 — Acceso SSO desde Odoo al BSC:** Desde el inicio de Odoo, haz clic en el acceso al BSC (`/bsc/?sso=...&empresa=jjsumi`) mostrando que entra autenticado automáticamente sin pedir contraseña.
3. **Demo 2 — Tablero Ejecutivo y Etiqueta `Odoo en vivo`:** En el **Dashboard ejecutivo**, muestra los semáforos de las 4 perspectivas y las tarjetas `KpiCard` con la etiqueta verde **`Odoo en vivo`**. Cambia de sucursal (Juliaca, Puno, Arequipa, Cusco, Tacna) para mostrar la data multi-empresa.
4. **Demo 3 — Pestaña `Finanzas & SUNAT`:** Abre **Análisis → Finanzas & SUNAT** y explica:
   - Los indicadores tributarios/financieros calculados desde `l10n_pe` y `jjsumi_reniec` (`K14` IGV Neto Proyectado, `K15` % RUC Activo/Habido, `K16` Notas de Crédito, `K17` CxC > 30d) y de inventario (`K19` Quiebres, `K20` Valorización).
   - La tabla comparativa de las 6 sedes y la tabla inferior de **Historial de sincronizaciones Odoo → BSC** (`SyncOdooLog`).
5. **Demo 4 — n8n (`http://<IP>/`):** Abre n8n, muestra los 3 workflows publicados/activos (`Eventos Odoo`, `Cierre Diario`, `Monitor de Alertas`) y explica cómo se disparan correos automáticos ante riesgo fiscal SUNAT o quiebre de stock.

---

## 4. Comandos y Verificación Técnica (Servicios, APIs y BD)

### Verificar servicios y proxy Nginx
```bash
systemctl is-active bsc-backend.service n8n.service nginx.service odoo19.service
curl -s -o /dev/null -w "BSC_UI:%{http_code}\n" http://127.0.0.1/bsc/
curl -s -o /dev/null -w "N8N_RESUMEN:%{http_code}\n" -H "x-jjsumi-secret: jjsumi-odoo-bsc-sync-2026" http://127.0.0.1:3000/bsc/n8n-resumen
```

### Verificar workflows publicados en n8n
```bash
/home/ubuntu/.nvm/versions/node/v22.23.5/bin/n8n list:workflow
```

### Forzar sincronización manual Odoo → BSC y ver resultado
```bash
sudo -u odoo /opt/odoo19/venv/bin/python /opt/odoo19/odoo/odoo-bin shell -c /etc/odoo19.conf -d jjsumi --no-http << 'EOF'
print("SYNC_RESULT:", env['jjsumi.bsc.sync'].push_realtime('VERIFICACION_DEMO'))
EOF
```

### Consultar Base de Datos del BSC (`bsc_techperu` en PostgreSQL)
```bash
# Últimos logs de sincronización Odoo -> BSC
sudo -u postgres psql -d bsc_techperu -c "
SELECT id, origen, estado, \"empresasCount\", \"kpisActualizados\", \"alertasGeneradas\", \"createdAt\"
FROM \"SyncOdooLog\"
ORDER BY \"createdAt\" DESC LIMIT 5;"

# Ver valores reales sincronizados de Finanzas SUNAT e Inventario para JJSUMI Matriz
sudo -u postgres psql -d bsc_techperu -c "
SELECT id, nombre, meta, real, unidad, \"origenDatos\", \"ultimaSyncOdoo\"
FROM \"Kpi\"
WHERE \"empresaId\" = 'jjsumi' AND \"origenDatos\" = 'ODOO'
ORDER BY orden;"

# Contar alertas críticas activas generadas por Odoo
sudo -u postgres psql -d bsc_techperu -c "
SELECT tipo, severidad, estado, COUNT(*)
FROM \"Alerta\"
GROUP BY tipo, severidad, estado;"
```
