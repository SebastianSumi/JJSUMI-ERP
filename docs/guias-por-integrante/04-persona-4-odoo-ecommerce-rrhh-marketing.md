# Persona 4 — E-commerce, Recursos Humanos, Marketing y Experiencia Web (Odoo 19)

> **Alcance:** Portal web / E-commerce (`jjsumi_site`), gestión de Recursos Humanos (`jjsumi_hr_ext`), campañas de Marketing (`jjsumi_marketing`), identidad visual y usabilidad en Odoo 19 (`jjsumi_theme`, `jjsumi_auth`, `jjsumi_home_cards`, `jjsumi_menus`).

---

## 1. Módulos y Archivos Bajo tu Responsabilidad

| Módulo (`odoo-custom-addons/`) | Qué hace | Archivos clave |
|---|---|---|
| `jjsumi_site` | Sitio web comercial y portal de clientes (`/my` para ver pedidos, boletas y favoritos). | `controllers/main.py`, `data/templates.xml`, `static/src/css/site.css`, `static/src/js/site.js` |
| `jjsumi_hr_ext` | Extensiones para el área de Recursos Humanos (empleados, estructura). | `models/`, `__manifest__.py` |
| `jjsumi_marketing` | Gestión de campañas y acciones de marketing vinculadas al área comercial. | `models/`, `views/`, `data/` |
| `jjsumi_home_cards` | Panel principal con tarjetas de acceso rápido en Odoo y botón SSO hacia el BSC. | `models/home.py`, `static/src/js/home_dashboard.js` |
| `jjsumi_auth` | Pantalla de login personalizada con identidad corporativa Navy & Gold. | `static/src/css/jjsumi_login.css`, `views/` |
| `jjsumi_theme` | Tema visual corporativo del backend de Odoo (`#101F3A` y `#C9A227`). | `static/src/css/jjsumi.css` |
| `jjsumi_menus` | Organización de menús por área (Ventas, Finanzas, Inventario, RR.HH., Marketing). | `views/menus.xml` |

---

## 2. Flujos Principales

### Flujo A: E-commerce y Portal del Cliente (`jjsumi_site`)
```
Visitante en Web Pública (:8069) ──▶ Catálogo de productos JJSUMI
  ──▶ Registro / Login (/web/login con jjsumi_auth)
  ──▶ Pedido en línea (sale.order) ──▶ Portal /my ("Mis pedidos y boletas")
```

### Flujo B: Experiencia Interna (Home Cards + RR.HH. + Marketing)
```
Login corporativo (jjsumi_auth + jjsumi_theme)
  ──▶ Dashboard de Inicio (jjsumi_home_cards)
  ├─ Acceso a RR.HH. (empleados, asistencia/metas)
  ├─ Acceso a Marketing (campañas y captación)
  └─ Acceso directo SSO al Balanced Scorecard
```

---

## 3. Guion de Presentación (3–5 minutos)

1. **Apertura:** *"Yo estuve a cargo de la cara externa y la experiencia del usuario en Odoo: el portal E-commerce, los módulos de Recursos Humanos y Marketing, y toda la identidad visual corporativa."*
2. **Demo 1 — Identidad Visual y Login (`jjsumi_auth` + `jjsumi_theme`):** Muestra la pantalla de inicio de sesión personalizada (estilo Navy & Gold) y el panel de inicio con **Home Cards** que organiza los accesos por área sin abrumar al usuario.
3. **Demo 2 — E-commerce y Portal (`/my` en `jjsumi_site`):** Abre el sitio web público de Odoo (`http://<IP>:8069/`), muestra el catálogo de productos y la sección **"Mis pedidos y boletas"** (`/my`), explicando cómo un cliente puede consultar sus compras y boletas en línea.
4. **Demo 3 — Marketing y RR.HH.:**
   - Muestra el módulo de **Marketing** (campañas y seguimiento comercial).
   - Muestra el módulo de **Empleados / RR.HH.** integrado con los objetivos de aprendizaje/asistencia del sistema.
5. **Cierre:** *"Con esto cerramos el círculo completo: desde que el cliente compra en el portal web o el equipo opera internamente, hasta que la gerencia ve los resultados en el BSC."*

---

## 4. Comandos y Verificación Técnica (Servidor, Web y Base de Datos)

### Verificar que el portal web y login de Odoo responden HTTP 200
```bash
curl -s -o /dev/null -w "ODOO_WEB:%{http_code}\n" http://127.0.0.1:8069/
curl -s -o /dev/null -w "ODOO_LOGIN:%{http_code}\n" http://127.0.0.1:8069/web/login
```

### Verificar módulos instalados en PostgreSQL (`jjsumi`)
```bash
sudo -u postgres psql -d jjsumi -c "
SELECT name, state, latest_version
FROM ir_module_module
WHERE name IN ('jjsumi_site','jjsumi_hr_ext','jjsumi_marketing','jjsumi_home_cards','jjsumi_auth','jjsumi_theme','jjsumi_menus','website','hr')
ORDER BY name;"
```

### Consultar empleados, usuarios y pedidos web en BD (`jjsumi`)
```bash
# Empleados activos por empresa
sudo -u postgres psql -d jjsumi -c "
SELECT company_id, COUNT(*) AS empleados
FROM hr_employee
WHERE active = true
GROUP BY company_id ORDER BY company_id;"

# Usuarios internos vs portal
sudo -u postgres psql -d jjsumi -c "
SELECT share AS es_usuario_portal, COUNT(*)
FROM res_users
WHERE active = true
GROUP BY share;"
```

### Verificar archivos de estilos y assets estáticos
```bash
ls -lh /opt/odoo19/custom-addons/jjsumi_theme/static/src/css/jjsumi.css \
       /opt/odoo19/custom-addons/jjsumi_auth/static/src/css/jjsumi_login.css \
       /opt/odoo19/custom-addons/jjsumi_site/static/src/css/site.css
```
