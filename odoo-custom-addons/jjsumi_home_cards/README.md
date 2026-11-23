# JJSUMI Home Cards — Odoo 19 Community

Addon de navegación para añadir una aplicación **JJSUMI** con una pantalla de inicio basada en tarjetas.

## Principios

- No reemplaza el web client ni la barra de navegación de Odoo.
- No modifica archivos originales de Odoo.
- No crea CRM, ventas, inventario ni otros sistemas paralelos.
- Las tarjetas abren modelos y vistas nativas cuando el módulo correspondiente está instalado.
- Los módulos opcionales no se instalan automáticamente: si una aplicación no está disponible, se muestra un aviso.
- Los permisos de acceso a los datos siguen siendo los permisos nativos de Odoo.

## Tarjetas incluidas

CORE, CRM, Ventas, Inventario, Compras, Fabricación, Calidad, Mantenimiento, Punto de venta, Finanzas, RR. HH. y Reportes.

## Instalación controlada

1. Respaldar la base de datos y el filestore.
2. Confirmar la ruta real de `addons_path` y la base de datos de destino.
3. Copiar la carpeta `jjsumi_home_cards` a una ruta incluida en `addons_path`.
4. Reiniciar Odoo.
5. Actualizar la lista de aplicaciones.
6. Instalar **JJSUMI - Inicio por tarjetas** desde Aplicaciones.
7. Probar primero con un usuario administrador y luego con usuarios de cada grupo.

No ejecutar la instalación directamente en producción sin respaldo y prueba previa.

## Nota sobre las tarjetas

Las tarjetas Calidad y Mantenimiento requieren que existan los modelos `quality.check` y `maintenance.request` en esa base. La tarjeta POS intenta abrir la acción nativa del POS; si no está disponible, abre la configuración de puntos de venta. La tarjeta Reportes es un punto de entrada básico a los reportes registrados en Odoo; su organización funcional se definirá en una extensión posterior.

## Compatibilidad

Preparado como addon para Odoo 19. Debe validarse en la instalación exacta de JJSUMI antes de producción, especialmente las acciones especializadas del POS y la disponibilidad de los módulos opcionales.
