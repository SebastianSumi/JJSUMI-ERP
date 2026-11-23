# JJSUMI ERP — FASE 02 v2.3: CATÁLOGO MAESTRO DE PRODUCTOS

**Plataforma:** Odoo 19 Community · **Base:** `jjsumi` (protegida)
**Fecha:** 19 de noviembre de 2026
**Estado:** Pendiente de aprobación. No autoriza cambios en la base hasta aprobarse.
**Sustituye a:** v2.1 (`Fase 2 principio.txt`) y v2.2 (`Fase 2 Contraste ODOO.txt`).
**Fuentes:** v2.1 para los datos del catálogo; v2.2 solo para los puntos que se verificaron en código y base.

---

## 0. Decisiones cerradas

| # | Tema | Decisión |
|---|---|---|
| D1 | Template "Yeso" (`jjsumi_base.product_template_yeso`) | Legado. Precio oficial **S/ 6 / 7 / 8** (23 / 26 / 30 kg), según `_jjsumi_setup_precios`. No se modifica, no se archiva, no se borra. Fuera del catálogo nuevo. |
| D2 | Precios del catálogo YES-001 a MAT-020 | Los del documento v2.1 (p. ej. YES-001 S/ 28.00, YES-002 S/ 35.00). |
| D3 | Códigos de barras (`barcode`) | No se importan. Campo vacío. Quedan fuera de las pruebas. |
| D4 | Almacenes y ubicaciones | Fuera de Fase 2. Se definen en Fase 3. Fase 2 no crea ni asigna almacenes, ubicaciones ni reglas de reposición. |
| D5 | Imágenes | `image_1920` vacío. Ninguna ruta de placeholder. |
| D6 | Presentación de saco | UoM de peso (kg). Un UoM por presentación. |
| D7 | Lotes | Por categoría (ver sección 4). |
| D8 | Localización | Impuestos nativos de `l10n_pe` de la compañía. Sin cuentas inventadas. |
| D9 | Datos faltantes | Completar con datos de prueba, marcados como demo (ver sección 9). |
| D10 | Variantes | Solo las 25 variantes explícitas y los templates sin variantes. Las 145 del v2.1 no se generan. |

---

## 1. Hallazgos de la base (consulta de solo lectura, 19/11/2026)

| Hallazgo | Dato | Consecuencia en Fase 2 |
|---|---|---|
| Template "Yeso" | `list_price` = 6.0, `type` = consu, `is_storable` = t, activo | Coincide con D1. |
| Movimientos del "Yeso" | 27 `stock_move`, 0 líneas de venta, cantidad en stock = 0 | Confirma que no puede borrarse. Se mantiene como legado. |
| Códigos de producto existentes | 40 `default_code`: `COMM`, `FURN_*`, `E-COM*`, `Delivery_*`, `JJ-PIEDRA`, `JJ-COMBUSTIBLE`, `JJ-BOLSA`, etc. | No hay colisión con `YES-`, `PLA-`, `DEC-`, `MAS-`, `MAT-`, `HER-`. |
| Solapamiento con `JJ-*` | `JJ-PIEDRA` (Carga de piedra de yeso), `JJ-BOLSA` (Bolsa de empaque), `JJ-COMBUSTIBLE` | Pueden corresponder a MAT-001, MAT-007 o MAT-005. **Pendiente de decisión** (sección 10). No se fusionan automáticamente. |
| Categoría raíz "All" | El XML ID `product.product_category_all` no existe en esta base | Las 6 categorías se crean como raíz (sin padre). |
| Categorías existentes | `Goods`, `Expenses`, `Services`, `Home Construction`, `Furniture`, `Office`, `Outdoor`, `Food`, `Yeso` (`jjsumi_base`), y una categoría id 7 sin XML ID | La categoría id 7 se usa por `JJ-*`. Sin mapear. |
| Moneda | PEN activa | OK. |
| Impuestos de compañía 1 | `18%` venta (id 1), `18%` compra (id 2), `0% Exports` (3), `0% Imports` (4), `IGV 18% incluido` (5, `price_include_override = tax_included`) | Ver D8 y sección 6. |
| Módulos | `l10n_pe`, `stock`, `purchase`, `sale_management`, `point_of_sale`, `mrp`, `account`, `uom`, `product` instalados | OK. |
| Compañías | JJSumi (id 1) y 5 hijas: Sucursal Juliaca (7), Puno (8), Arequipa (9), Cusco (10), Tacna (11) | Los productos van a la compañía 1. |
| Almacenes | `WH` (matriz) y `JS2` ("JJSumi Sucursal Juliaca 2") | No se toca en Fase 2. JS2 se decide en Fase 3. |
| Proveedores (`supplier_rank > 0`) | 3 | Hay que crear 35 proveedores. Ninguno coincide con los RUC del documento. |
| Etiquetas (`product.tag`) | 0 | Se crean las 10 del catálogo. |

---

## 2. Correcciones respecto a v2.2

Cada corrección se comprobó en el código de Odoo 19 (`/opt/odoo19/odoo/addons`) salvo donde se indica "pendiente de verificar".

| # | v2.2 decía | Odoo 19 real | Verificado en |
|---|---|---|---|
| 1 | `product_type` = consu/product/service | Campo `type` = `consu` / `service` / `combo`. "Almacenable" = `is_storable = True` | `product/models/product_template.py`, `stock/models/product.py` |
| 2 | `create_variant` = always/option/no_variant/no_variants | `always` / `dynamic` / `no_variant` | `product/models/product_attribute.py` |
| 3 | `display_type` = dropdown | `radio`, `pills`, `select`, `color`, `multi`, `image` | `product/models/product_attribute.py` |
| 4 | UoM con `factor` y `factor_inv` escritos | Se escribe `relative_factor` + `relative_uom_id`. `factor` es calculado. No existe `factor_inv` | `uom/models/uom_uom.py` |
| 5 | Precio por variante en `product.product.list_price` | `list_price` es del template. Variante: `price_extra` en `product.template.attribute.value`. `lst_price` es calculado | `product/models/product_template_attribute_value.py` |
| 6 | Pricelist con `compute_price` fixed/percentage/formula | Correcto. `applied_on`: `3_global`, `2_product_category`, `1_product`, `0_product_variant` | `product/models/product_pricelist_item.py` |
| 7 | Cuentas 401111, 401112, 401113 | No existen. Se usan los impuestos nativos de `l10n_pe` (sección 6) | Consulta a base |
| 8 | Barcode EAN-13 `7750000000011` | Dígito de control incorrecto. Campo no se usa (D3) | Cálculo |
| 9 | Ruta "Reponer" (ROUTE-REPL) | No es una ruta. Las reglas de reposición son `stock.warehouse.orderpoint` y dependen de almacén (Fase 3) | Pendiente de Fase 3 |
| 10 | Imagen con ruta `/web/static/img/placeholder.png` | Campo binario. Se deja vacío (D5) | Modelo |

Los XML IDs de rutas (`stock.route_warehouse0_buy`, `mrp.route_warehouse0_manufacture`, `stock.route_warehouse0_mto`) están **pendientes de verificar** en la base antes de usarlos.

---

## 3. Categorías de producto (6)

Todas en la compañía JJSumi (id 1), raíz (sin padre), con `removal_strategy = fifo`.

| Código | Nombre | Método de costo | Lote | Rutas | Tipo |
|---|---|---|---|---|---|
| CAT-YES | Yesos de Construcción | average | Sí | Buy, Manufacture | almacenable |
| CAT-PLA | Placas y Derivados | average | No | Buy | almacenable |
| CAT-DEC | Productos Decorativos | standard | No | Buy | almacenable |
| CAT-MAS | Masillas y Mezclas | average | Sí | Buy, Manufacture | almacenable |
| CAT-MAT | Materias Primas | average | Sí | Buy | almacenable |
| CAT-HER | Herramientas y Accesorios | standard | No | Buy | consumible |

Notas:
- El código CAT-* no es campo de `product.category`. Se guarda como XML ID (`jjsumi_catalog.categ_yes`, etc.).
- `cost_method` y `valuation` por categoría: **pendiente de verificar** los nombres exactos de campo en el módulo `product` y `stock` de Odoo 19 antes de escribir el XML.

---

## 4. Tipo de producto y seguimiento

- **Almacenable:** `type = consu`, `is_storable = True`.
- **Consumible (CAT-HER):** `type = consu`, `is_storable = False`.
- **Servicio:** ninguno en esta fase. El título del v2.1 habla de servicios, pero el catálogo no define ninguno.
- **Seguimiento (D7):**
  - CAT-YES, CAT-MAS, CAT-MAT: seguimiento por lote. Incluye MAT-001 a MAT-020 (corrige la tabla del v2.1, que marcaba MAT-006 a MAT-020 como "Sin seguimiento").
  - CAT-PLA, CAT-DEC, CAT-HER: sin seguimiento.
- **Valor del campo:** `tracking = lot` / `none`. **Pendiente de verificar** en `stock/models`.

---

## 5. Unidades de medida

Decisión D6: cada presentación de peso es su propio UoM. Así la conversión es exacta y no se reutiliza una UoM genérica "Saco" con factor distinto.

### 5.1 UoM nativas (no se crean)

| Uso | UoM nativa | XML ID | Relación |
|---|---|---|---|
| Kilogramo | kg | `uom.product_uom_kgm` | referencia de peso |
| Tonelada | Ton | `uom.product_uom_ton` | 1000 kg |
| Unidades | Units | `uom.product_uom_unit` | referencia de unidad |
| Litro | L | `uom.product_uom_litre` | referencia de volumen |
| Metro | m | `uom.product_uom_meter` | referencia de longitud |

### 5.2 UoM a crear

| Nombre | Categoría | Relativa a | `relative_factor` | Uso |
|---|---|---|---|---|
| Saco 5 kg | Peso | kg | 5 | YES-021 (variante) |
| Saco 10 kg | Peso | kg | 10 | YES-006, YES-017 (variantes) |
| Saco 20 kg | Peso | kg | 20 | YES-006, YES-014, MAS-006 |
| Saco 25 kg | Peso | kg | 25 | YES-001, YES-003, YES-004 y otros |
| Saco 30 kg | Peso | kg | 30 | YES-005, YES-011, YES-016 |
| Saco 40 kg | Peso | kg | 40 | YES-002, YES-007, YES-020 |
| Saco 50 kg | Peso | kg | 50 | YES-008 |
| Paquete x10 | Unidad | Units | 10 | PLA-015, HER-006 y otros paquetes |

Notas:
- `relative_factor` es el número de kg (o unidades) que contiene la UoM. La relación ya se comprobó con el módulo nativo: `product_uom_ton` tiene `relative_factor = 1000` relativo a kg.
- Los sacos de 20, 30, 40 kg aparecen en el v2.1 con un peso fijo. Si una presentación se vende en varios pesos, va como variante del atributo "Peso del saco", no como UoM distinta.
- "Saco" y "Paquete" del v2.1 quedan reemplazados por las UoM de esta tabla. El número de UoM no es 8 sino 13 (5 nativas usadas + 8 creadas). El v2.1 tenía un conteo inconsistente.
- Tabla completa de asignación producto → UoM: se genera desde el catálogo al cargar (sección 9).

---

## 6. Impuestos (localización peruana)

Según D8 y lo que hay en la base:

| Uso | Impuesto a usar | ID en base | Motivo |
|---|---|---|---|
| Venta (precio sin IGV) | `18%` (sale) | 1 | Precio sin impuesto incluido, como pide el documento |
| Compra | `18%` (purchase) | 2 | Igual |
| Exonerado | **No se crea** | — | No hay exonerado en `l10n_pe` de la base. `0% Exports` no es lo mismo. Pendiente de decisión (sección 10) |

**No usar** `IGV 18% incluido` (id 5): tiene precio incluido y el documento fija precios sin impuestos.

Los XML IDs de esos impuestos no son `l10n_pe` directos (aparecen como `account.1_sale_tax_template`). Se referencian por ID o por búsqueda de nombre dentro de la compañía, no por XML ID inventado.

---

## 7. Atributos y valores

| Código | Nombre | `create_variant` | `display_type` | Valores |
|---|---|---|---|---|
| ATT-PRE | Presentación | dynamic | radio | Saco, Granel, Unidad, Paquete |
| ATT-PES | Peso del saco | dynamic | radio | 5, 10, 20, 25, 30, 40, 50 kg |
| ATT-DIM | Dimensión | dynamic | radio | 1.2 x 2.4 m, 60 x 60 cm, 50 x 50 cm, 9.5 mm, 12.5 mm, 15 mm |
| ATT-COL | Color | always | color | Blanco #FFFFFF, Beige #F5F5DC, Gris #808080 |

Notas:
- **Obligatorio:** el v2.1 lo pedía como campo del atributo. Odoo no tiene ese campo en `product.attribute`. Se configura por línea de atributo del template, no por atributo. No se implementa como campo.
- **Atributo existente:** `jjsumi_base.attribute_peso` ("Peso": 23/26/30 kg) pertenece al template legado. **No se reutiliza ni se modifica.** Se crea ATT-PES con su propio XML ID.
- Valores de dimensión de 9.5, 12.5 y 15 mm: se añaden a ATT-DIM porque las placas los usan como variante (PLA-001, PLA-002).
- Campo `html_color` del valor: **pendiente de verificar** en `product/models/product_attribute.py`.

---

## 8. Etiquetas (10)

`product.tag` con `name` y `color` (entero). Sin cambios respecto al v2.1 salvo el color entero: el nombre de color del v2.1 no es un entero de Odoo, así que se asigna número de paleta (1 a 11) según la tabla.

| Código | Nombre | Color (entero) |
|---|---|---|
| TAG-NEW | Nuevo Producto | 10 |
| TAG-PROMO | En Promoción | 1 |
| TAG-ECO | Ecológico | 5 |
| TAG-PREM | Premium | 3 |
| TAG-IND | Industrial | 11 |
| TAG-RES | Resistente | 4 |
| TAG-RAP | Fraguado Rápido | 2 |
| TAG-IGN | Ignífugo | 13 |
| TAG-ACO | Acústico | 7 |
| TAG-IMP | Impermeable | 9 |

---

## 9. Productos (120 templates, 25 variantes explícitas)

### 9.1 Fuente y reglas

- La fuente de datos son las tablas por producto de `Fase 2 principio.txt` (sección 11). Los 120 SKU, nombres, costos, barcodes del v2.1 se reemplazan por: SKU y nombre del v2.1, precio y costo del v2.1, sin barcode.
- Margen comercial = (precio − costo) / precio. Se calcula en la carga, no se copia. Ejemplo: YES-001 (28.00 − 18.50) / 28.00 = **33.93 %** (el v2.1 decía 33.87 %).
- `default_code` = SKU. Es la clave de idempotencia.
- `company_id` = JJSumi (id 1).
- `active` = True.
- `image_1920` = vacío.
- `sale_ok` = True, salvo MAT-*, que son `False` (materias primas).
- `purchase_ok` = True.
- `taxes_id` = 18% venta (id 1). `supplier_taxes_id` = 18% compra (id 2). MAT-* sin `taxes_id` de venta.

### 9.2 Conteo

| Categoría | Templates | Templates con variantes explícitas | Variantes explícitas |
|---|---|---|---|
| CAT-YES | 25 | YES-001, YES-002, YES-003, YES-004, YES-006, YES-021 | 10 |
| CAT-PLA | 20 | PLA-001, PLA-002, PLA-003 | 7 |
| CAT-DEC | 20 | DEC-004, DEC-009 | 4 |
| CAT-MAS | 15 | MAS-001, MAS-005 | 4 |
| CAT-MAT | 20 | ninguno | 0 |
| CAT-HER | 20 | ninguno | 0 |
| **Total** | **120** | **13** | **25** |

Las 25 variantes explícitas (v2.1 sección 12, líneas 960 a 984) se mantienen. Para cada una:
- Presentación, peso o dimensión se mapean a los valores de la sección 7.
- Precio final de la variante se logra con `price_extra` = precio_variante − precio_template. Ejemplo: YES-001-40 (38.50) sobre YES-001 (28.00) = `price_extra` 10.50.
- Costo por variante se guarda en `standard_price` de `product.product`.
- **Diferidas (2):** DEC-004-50 y DEC-004-80. Sus medidas "50 cm" y "80 cm" no están en ATT-DIM. Se generan solo si se añaden esos valores al atributo (decisión pendiente).
- Los barcodes de la sección 12 del v2.1 no se cargan (D3).

### 9.3 Datos que faltan (D9, marcados como demo)

Para los productos sin proveedor, regla de reposición o variante definida:
- Proveedor: uno de la lista de 35 proveedores del v2.1, según la columna "Categoría principal". Se marca en `supplierinfo` con nota "DEMO".
- Precio de compra: igual al costo del producto. Cantidad mínima: 1. Plazo: 7 días.
- Ningún valor se marca como real. Se reemplazan al entregar datos de JJSUMI.

### 9.4 Proveedores (35)

- Se crean como `res.partner` de tipo proveedor, `supplier_rank = 1`, país Perú, ciudad según el v2.1.
- **RUC:** el v2.1 trae RUC ficticios (p. ej. `20100112345`). La Fase 1 (regla 9) prohíbe inventar RUC. **No se cargan.** Campo `vat` vacío. Pendiente de decisión (sección 10).
- Teléfonos y correos del v2.1: se cargan como demo. Pendiente de decisión.
- Plazo de pago 15 o 30 días: `property_supplier_payment_term_id` por proveedor. **Pendiente de verificar** nombre de campo y de términos de pago existentes.

---

## 10. Listas de precios (5)

| Código | Nombre | Moneda | Venta | Selectable | Regla | Aplicación |
|---|---|---|---|---|---|---|
| PRICELIST-001 | Lista Pública PEN | PEN | sí | sí | list_price sin descuento | todos |
| PRICELIST-002 | Lista Mayorista PEN | PEN | sí | sí | list_price − 10 %, mínimo 10 unidades | sin cliente asignado (ver nota) |
| PRICELIST-003 | Lista Distribuidor PEN | PEN | sí | sí | list_price − 18 %, mínimo 50 unidades | sin cliente asignado |
| PRICELIST-004 | Lista Corporativa PEN | PEN | sí | sí | list_price − 15 %, mínimo 20 unidades | sin cliente asignado |
| PRICELIST-005 | Lista Promocional PEN | PEN | sí | no | list_price − 5 % | productos seleccionados |

Notas:
- **Asignación a clientes:** las listas 002 a 004 dependen de "condición de cliente" (Mayorista, Distribuidor, Corporativo). Odoo asigna la lista en el cliente (`property_product_pricelist`). No existe esa condición en `res.partner`. **Fase 2 crea las listas y sus reglas. No asigna clientes.** La segmentación pasa a Fase 5 (CRM y ventas).
- **Promoción:** Odoo no filtra reglas de tarifa por etiqueta. TAG-PROMO no se usa en la regla. La lista 005 se aplica a una lista de productos definida en Fase 5.
- **Vigencia de 30 días (005):** las fechas `date_start`/`date_end` se fijan al activar la promoción, no al cargar.
- **Redondeo y `discount_policy`:** `without_discount`, como el v2.2.
- Activación previa: ajustes de Ventas → listas de precios (ruta verificada en v2.2, pendiente de confirmar en la instancia).

---

## 11. Proveedores asociados (`product.supplierinfo`)

- Cada template de venta debe tener al menos un proveedor (T14).
- Filas del v2.1 cuando estén completas (p. ej. YES-001: PROV-001 a 18.50 / 100 sacos / 5 días; PROV-002 a 19.00 / 50 sacos / 7 días).
- Resto de productos: proveedor DEMO (9.3).
- `product_tmpl_id` siempre; `product_id` solo para variantes explícitas.
- Campos: `partner_id`, `product_tmpl_id`, `product_id`, `price`, `min_qty`, `delay`, `currency_id` (PEN), `date_start`, `date_end` (31/12/2026 del v2.1).

---

## 12. Lo que queda fuera de Fase 2

| Elemento | Motivo | Fase |
|---|---|---|
| Almacenes (WH-JUL, WH-PUN, WH-AQP, WH-CUS, WH-TAC) y JS2 | Decisión D4 | 3 |
| Ubicaciones (45) | Dependen de almacén | 3 |
| Reglas de reposición (orderpoints) | Dependen de almacén | 3 |
| Códigos de barras | Decisión D3 | — |
| Imágenes | Decisión D5 | Posterior |
| Template "Yeso" (legado) | Decisión D1 | — |
| Clientes y asignación de listas | No hay condición de cliente aún | 5 |
| Exonerado (TAX-EXON) | No está en `l10n_pe` de la base | Pendiente |
| Servicios | El catálogo no define ninguno | — |
| SUNAT, RENIEC, BSC | Fuera de alcance del proyecto | — |

---

## 13. Pruebas de aceptación (T01–T20)

| ID | Prueba | Resultado esperado |
|---|---|---|
| T01 | Crear YES-001 | `type = consu`, `is_storable = True`, `tracking = lot`, categoría CAT-YES |
| T02 | Crear producto con SKU duplicado | Error por `default_code` duplicado |
| T03 | Cambiar `barcode` | No aplica (D3). Se elimina de la prueba |
| T04 | Verificar MAT-001 | `tracking = lot`, UoM `Ton` |
| T05 | Aplicar PRICELIST-002 a YES-001 | Precio = S/ 25.20 |
| T06 | Escaneo en POS | No aplica (D3). Se elimina |
| T07 | Importar 10 productos de prueba | 10 creados sin duplicados |
| T08 | Archivar HER-005 | `active = False`, sale de vistas activas |
| T09 | MAT-001 `uom_id` y `uom_po_id` | `Ton` |
| T10 | Ficha MAT-003 con PROV-018 | Proveedor con precio S/ 8.00 |
| T11 | Ficha YES-001 sin imagen | `image_1920` vacío |
| T12 | Variantes de PLA-001 (9.5 / 12.5 / 15 mm) | 3 `product.product` |
| T13 | Impuesto 18% venta a YES-001 | Precio con IGV = S/ 33.04 (28.00 × 1.18) |
| T14 | Productos de venta con proveedor | Todos con ≥ 1 `supplierinfo` |
| T15 | Método de costo por categoría | CAT-YES `average`, CAT-DEC `standard`, CAT-HER `standard` |
| T16 | Listas de precios | 5 listas con sus reglas |
| T17 | Importar 120 templates | 120 con `type`, `tracking` y `default_code` correctos |
| T18 | Ruta Buy en MAT-001 | `route_ids` incluye la ruta Buy (XML ID pendiente de verificar) |
| T19 | Valoración de categorías | Según sección 3 |
| T20 | Removal strategy | `fifo` en todas |
| T21 | Idempotencia | Ejecutar la carga dos veces no duplica registros |
| T22 | EAN-13 | No aplica (D3) |
| T23 | Template "Yeso" intacto | `list_price` = 6.0, 27 movimientos de stock sin cambio |

---

## 14. Criterios de aceptación

- [ ] 6 categorías con `cost_method`, `removal_strategy` y rutas según la sección 3.
- [ ] 13 UoM (5 nativas usadas + 8 creadas) con `relative_factor` correcto.
- [ ] 4 atributos con sus valores (sección 7).
- [ ] 10 etiquetas.
- [ ] 35 proveedores sin RUC inventados.
- [ ] 5 listas de precios con sus reglas.
- [ ] 120 templates con SKU, categoría, tipo, lote y precio del documento.
- [ ] 25 variantes explícitas generadas, con precio correcto.
- [ ] Un proveedor por producto de venta (DEMO donde falten datos).
- [ ] Imagen vacía en todos.
- [ ] Ninguna modificación del template "Yeso" ni de sus movimientos.
- [ ] Pruebas T01–T23 aprobadas.
- [ ] Carga idempotente (T21).

---

## 15. Pendiente de verificar antes de escribir el addon

1. Nombres de campo `cost_method` / `valuation` (categoría) y `tracking` (producto) en Odoo 19 Community.
2. XML IDs de rutas: `stock.route_warehouse0_buy`, `mrp.route_warehouse0_manufacture` (existen en el código; confirmar en la base).
3. Campo `html_color` de `product.attribute.value`.
4. Nombre de campo y existencia de términos de pago para proveedores.
5. Categoría id 7 (usada por JJ-PIEDRA, JJ-BOLSA, JJ-COMBUSTIBLE): qué es y si MAT-001, MAT-007 o MAT-005 la reemplazan.

---

## 16. Decisiones que necesito de ti antes de ejecutar

1. **JJ-PIEDRA, JJ-BOLSA, JJ-COMBUSTIBLE:** ¿se reemplazan por MAT-001, MAT-007 y MAT-005, se mantienen aparte, o se archivan? No se decide sin tu respuesta.
2. **RUC de proveedores:** el v2.1 los trae ficticios. ¿Los dejamos vacíos (recomendado, por la regla 9 de Fase 1) o los autorizas como demo?
3. **Exonerado:** ¿creamos un impuesto 0 % "Exonerado" propio, o no usamos exonerado en Fase 2?
4. **Categorías:** ¿confirmas las 6 como raíz (sin "All / Todos los productos", que no existe en la base)?

---

**Documento v2.3 — Pendiente de aprobación.** No autoriza cambios en la base de datos.
