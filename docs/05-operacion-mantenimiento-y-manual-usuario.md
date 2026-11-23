# 05 — Manual de Usuario Final, Operación y Mantenimiento

---

## Parte A: Manual para Usuario Final

### 1. Flujo Diario de Finanzas y Contabilidad
1. **Validar proveedores/clientes (SUNAT/RENIEC):** En Odoo, al crear un contacto con RUC o DNI, hacer clic en **"Consultar RENIEC/SUNAT"** para registrar su estado (`jjsumi_reniec_estado`). Esto garantiza que las facturas no disparen alertas de riesgo de crédito fiscal.
2. **Aprobación de compras:** Las órdenes de compra `> S/ 5,000` requieren aprobación de sucursal/gerencia y `> S/ 20,000` de Gerencia General. Además, las facturas de proveedor con variación `> 5%` respecto a la OC requieren autorización de Contador/Admin.
3. **Monitoreo en el BSC:** Ingresar al BSC desde el acceso directo de Odoo (o `/bsc/`), abrir la pestaña **Finanzas & SUNAT** para revisar:
   - IGV Neto Proyectado del trimestre (`K14`).
   - Cumplimiento RUC Activo/Habido (`K15`).
   - Tasa de Notas de Crédito (`K16`) y Cartera Vencida > 30 días (`K17`).
   - Comparativa inmediata entre Matriz y las 5 sucursales.

### 2. Flujo Diario de Inventario y Almacén
1. Al validar guías de entrada/salida (`stock.picking`) en Odoo, el stock se recalcula automáticamente en el BSC (`K19` quiebres de stock y `K20` valorización).
2. Si un producto llega a saldo `0` o negativo tras una entrega, **n8n envía automáticamente una alerta por correo** para gestionar la reposición.

### 3. Gestión de Alertas en el BSC (Gerencia)
1. Cuando un indicador sincronizado cae en rojo, el BSC crea automáticamente una alerta crítica (`ODOO_SYNC`) y n8n la consolida cada 6 horas.
2. Desde el menú **Alertas** y **Tareas** del BSC, el gerente puede asignar un plan de acción al responsable. Cuando el indicador vuelve a cumplir su meta en Odoo, la tarea asociada se marca automáticamente como `COMPLETADA`.

---

## Parte B: Guía de Operación y Mantenimiento (TI / Desarrollo)

### 1. Gestión de Servicios (`systemd`)
```bash
# Verificar estado de los servicios
systemctl status odoo19.service bsc-backend.service n8n.service nginx.service postgresql@16-main.service

# Reiniciar servicios tras cambios
sudo systemctl restart odoo19.service
sudo systemctl restart bsc-backend.service
sudo systemctl restart n8n.service
```

### 2. Compilar y Desplegar Cambios del BSC
- **Backend (`/home/ubuntu/BSC-TechPeru-main/backend`):**
  ```bash
  npx prisma db push && npx prisma generate
  npm run build
  sudo systemctl restart bsc-backend.service
  ```
- **Frontend (`/home/ubuntu/BSC-TechPeru-main/frontend`):**
  ```bash
  VITE_API_URL=/bsc-api npm run build
  sudo cp -r dist/* /var/www/bsc/
  sudo chown -R www-data:www-data /var/www/bsc
  ```

### 3. Sincronización Manual Odoo → BSC (Consola)
```bash
sudo -u odoo /opt/odoo19/venv/bin/python /opt/odoo19/odoo/odoo-bin shell -c /etc/odoo19.conf -d jjsumi --no-http << 'EOF'
print(env['jjsumi.bsc.sync'].push_realtime('MANUAL_CLI'))
EOF
```

### 4. Importar y Publicar Workflows en n8n
```bash
N8N=/home/ubuntu/.nvm/versions/node/v22.23.5/bin/n8n
$N8N import:workflow --input=/home/ubuntu/JJSUMI-ERP/n8n-workflows/<archivo>.json
$N8N publish:workflow --id=<workflow_id>
sudo systemctl restart n8n.service
```

### 5. Logs y Diagnóstico Rápido
```bash
sudo journalctl -u bsc-backend.service -n 50 --no-pager
sudo journalctl -u odoo19.service -n 50 --no-pager
sudo journalctl -u n8n.service -n 50 --no-pager
sudo tail -n 50 /var/log/nginx/error.log
```
