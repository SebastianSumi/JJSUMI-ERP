# Plan maestro: ERP empresarial para una empresa de yesería en Odoo 19

Vamos a planificar el proyecto como si estuviéramos implementando un ERP
para una empresa con operaciones en varias ciudades, fábrica propia,
almacenes, vendedores, cajeros, distribuidores y administración central.

**La prioridad es construir todo el ecosistema empresarial dentro de
Odoo.** No vamos a empezar programando módulos al azar. Primero
definiremos la arquitectura, los módulos, los datos, los permisos, los
procesos y las reglas de negocio. Después implementaremos cada parte y
probaremos que funcione antes de avanzar.

------------------------------------------------------------------------

# 1. Alcance que queda establecido

# JJSUMI

## ERP ODOO 19

Proyecto empresarial · Perú · AWS Cloud

  Indicador              Alcance inicial
  -------------------- -----------------
  Productos                         120+
  Sucursales                           5
  Puntos de venta                      8
  Almacenes                            5
  Clientes ficticios                 250
  Proveedores                         35
  Empleados                           65
  Usuarios previstos                  40

**Plataforma:** Odoo 19 Community\
**SUNAT:** fuera de alcance por ahora\
**RENIEC:** fuera de alcance por ahora\
**BSC Enterprise:** fase futura independiente

Por tanto, las reglas son:

1.  Más de 100 productos registrados en Odoo.
2.  Múltiples sucursales y almacenes.
3.  Ocho puntos de venta operativos.
4.  Fabricación industrial de yeso.
5.  Compras, ventas, inventarios y logística.
6.  Contabilidad y gestión administrativa dentro de las posibilidades de
    Community y sus complementos.
7.  Usuarios, roles y permisos empresariales.
8.  Información ficticia para poblar y probar el ERP.
9.  Nada de BSC ni integraciones externas en esta etapa.
10. No modificar ni poner en riesgo la instalación que ya tenemos.

## Decisión fundamental sobre Odoo nativo

**Mantendremos las aplicaciones nativas de Odoo. No vamos a
reconstruirlas desde cero.**

La estrategia será:

-   Conservar las aplicaciones y modelos nativos de Odoo siempre que
    resuelvan correctamente la necesidad.
-   Registrar la información propia de JJSUMI en esos modelos nativos.
-   Configurar las aplicaciones para las operaciones reales de la
    empresa.
-   Añadir campos, reglas, menús, vistas, botones, permisos y reportes
    complementarios únicamente cuando sean necesarios.
-   Crear modelos propios solo para información o procesos que Odoo no
    contemple.
-   No duplicar entidades que ya existen en Odoo.
-   No modificar directamente el código fuente original de Odoo; las
    personalizaciones se realizarán mediante addons propios y mecanismos
    de extensión.

Por ejemplo, CRM seguirá siendo la aplicación CRM de Odoo. La
personalizaremos para que gestione las oportunidades, actividades,
equipos, vendedores y procesos comerciales de JJSUMI. No construiremos
otro CRM paralelo.

Esto significa que **sí agregaremos información y configuración de
JJSUMI**, pero no se limita a cargar datos: también podremos ampliar las
pantallas y procesos nativos cuando la operación empresarial lo
requiera. La aplicación base seguirá siendo la nativa.

# 2. Estructura de la empresa

Proponemos una sola empresa legal, con cinco sucursales operativas.

Esto es importante: no vamos a crear cinco empresas independientes solo
para representar cinco tiendas. Las sucursales serán unidades operativas
dentro de la misma compañía, salvo que exista una necesidad legal de
separar entidades.

## Sedes propuestas

  Código     Sucursal   Función
  ---------- ---------- --------------------------
  SEDE-001   Juliaca    Administración y fábrica
  SEDE-002   Puno       Comercial y distribución
  SEDE-003   Arequipa   Comercial y distribución
  SEDE-004   Cusco      Comercial y distribución
  SEDE-005   Tacna      Comercial y distribución

Las sedes y nombres comerciales son propuestas ficticias y podrán
modificarse. Se utilizará la funcionalidad de sucursales de Odoo cuando
sea compatible con la arquitectura de una sola compañía y con las reglas
de seguridad requeridas.

## Distribución de los ocho puntos de venta

  Sucursal   Punto de venta      Código
  ---------- ------------------- ---------
  Juliaca    Tienda principal    POS-001
  Juliaca    Tienda industrial   POS-002
  Puno       Tienda centro       POS-003
  Puno       Tienda norte        POS-004
  Arequipa   Tienda principal    POS-005
  Arequipa   Tienda secundaria   POS-006
  Cusco      Tienda comercial    POS-007
  Tacna      Tienda comercial    POS-008

Cada punto de venta tendrá:

-   Nombre y código.
-   Sucursal responsable.
-   Almacén de origen.
-   Cajeros asignados.
-   Métodos de pago.
-   Diario de caja correspondiente, según las posibilidades de
    configuración de Odoo.
-   Configuración de precios.
-   Configuración de impuestos para el escenario interno.
-   Secuencia de operaciones.
-   Control de apertura y cierre.
-   Reportes independientes.

Cada POS se configurará individualmente. Se validará en la instalación
real cómo se relacionan las sesiones, diarios, ubicaciones y almacenes,
sin asumir que todas las opciones están disponibles de la misma forma en
Community.

# 3. Catálogo de módulos: todo lo que tendrá nuestro Odoo

Dividiremos el ERP en 15 bloques funcionales. Esto no significa que
debamos programar 15 aplicaciones desde cero: aprovecharemos las
aplicaciones nativas de Odoo y crearemos módulos propios para las
funcionalidades que realmente necesite JJSUMI.

## Bloque A. Administración y estructura empresarial

**Fundacional**

  Módulo / entidad        Funciones
  ----------------------- -------------------------------------------------------
  Gestión empresarial     Datos generales y configuración de la compañía
  Sucursales              Registro y administración de las cinco sedes
  Departamentos           Producción, ventas, compras, administración, etc.
  Áreas                   Organización interna de cada sede
  Usuarios                Cuentas de acceso
  Roles                   Administrador, gerente, supervisor, vendedor, etc.
  Permisos                Control de lectura, escritura, creación y eliminación
  Auditoría               Historial de operaciones sensibles
  Configuración general   Moneda, unidades, secuencias y parámetros

Jerarquía empresarial propuesta:

``` text
JJSUMI
│
├── GERENCIA GENERAL
│   ├── Administración
│   ├── Finanzas
│   ├── Recursos Humanos
│   └── Auditoría
│
├── PLANTA JULIACA
│   ├── Producción
│   ├── Control de Calidad
│   ├── Mantenimiento
│   └── Almacén Central
│
├── SUCURSAL PUNO
│   ├── Ventas
│   ├── Almacén
│   └── POS
│
├── SUCURSAL AREQUIPA
│   ├── Ventas
│   ├── Almacén
│   └── POS
│
├── SUCURSAL CUSCO
│   └── Ventas, Almacén y POS
│
└── SUCURSAL TACNA
    └── Ventas, Almacén y POS
```

## Bloque B. Gestión comercial

  -----------------------------------------------------------------------
  Aplicación / módulo                 Funciones
  ----------------------------------- -----------------------------------
  CRM                                 Clientes potenciales y
                                      oportunidades

  Contactos                           Clientes y contactos empresariales

  Ventas                              Cotizaciones y pedidos

  Tarifas                             Precios por tipo de cliente

  Descuentos                          Descuentos autorizados

  Comisiones                          Comisiones de vendedores, si se
                                      habilita la solución adecuada

  Contratos                           Acuerdos comerciales y documentos
                                      asociados

  Devoluciones                        Devolución de productos vinculada a
                                      operaciones originales

  Reclamos                            Registro y seguimiento

  Crédito comercial                   Límites y condiciones de pago,
                                      sujeto a la solución contable
                                      disponible
  -----------------------------------------------------------------------

### Flujo comercial

``` text
Cliente potencial
      ↓
Registro / identificación del cliente
      ↓
Oportunidad comercial
      ↓
Cotización
      ↓
Confirmación del pedido
      ↓
Reserva y preparación de inventario
      ↓
Entrega
      ↓
Documento comercial / factura interna
      ↓
Cobro o seguimiento de deuda
```

Un cliente podrá tener varias direcciones, contactos, historial de
compras, saldo pendiente y condiciones comerciales.

## Bloque C. Catálogo y productos

Este bloque tendrá como mínimo 120 productos.

  Categoría                     Cantidad inicial
  --------------------------- ------------------
  Yesos de construcción                       25
  Placas y derivados                          20
  Productos decorativos                       20
  Masillas y mezclas                          15
  Materias primas                             20
  Herramientas y accesorios                   20
  **Total**                              **120**

Cada producto tendrá, según corresponda:

-   Código interno SKU.
-   Código de barras.
-   Nombre comercial.
-   Descripción técnica.
-   Categoría.
-   Imagen.
-   Unidad de medida.
-   Precio de compra.
-   Precio de venta.
-   Costo.
-   Margen comercial.
-   Proveedores.
-   Impuestos configurados para el escenario.
-   Seguimiento de existencias.
-   Lotes, cuando corresponda.
-   Reglas de reposición.
-   Ubicación por almacén.

También manejaremos variantes de presentación: saco de 20 kg, saco de 25
kg, saco de 40 kg, unidad, paquete y tonelada.

No crearemos productos duplicados para representar cada presentación
cuando corresponda utilizar variantes o unidades de medida de Odoo. Se
decidirá por producto si corresponde una variante, una unidad de medida
o un producto independiente.

## Bloque D. Inventario y almacenes

**Crítico para la empresa.** Se utilizará Inventory y las funciones de
códigos de barras que estén disponibles y sean compatibles con la
instalación Community.

Tendremos cinco almacenes principales:

  Código   Almacén    Función
  -------- ---------- ---------------------------
  WH-JUL   Juliaca    Fábrica y almacén central
  WH-PUN   Puno       Distribución
  WH-AQP   Arequipa   Distribución
  WH-CUS   Cusco      Distribución
  WH-TAC   Tacna      Distribución

En Juliaca crearemos ubicaciones internas:

``` text
WH-JUL
│
├── Recepción
├── Materia prima
├── Producción
├── Control de calidad
├── Productos terminados
├── Empaquetado
├── Despacho
├── Devoluciones
└── Productos defectuosos
```

Funciones:

1.  Entradas de mercadería.
2.  Salidas de mercadería.
3.  Transferencias internas.
4.  Transferencias entre sucursales.
5.  Inventario físico.
6.  Ajustes autorizados.
7.  Control de lotes.
8.  Control de productos dañados.
9.  Inventario mínimo y máximo.
10. Reposición automática.
11. Trazabilidad.
12. Valoración de inventarios.

Odoo ya contempla rutas de recepción, despacho, reabastecimiento,
almacenamiento y valoración. Aprovecharemos esos mecanismos en vez de
duplicarlos con código propio. Las opciones concretas se comprobarán en
Odoo 19 Community y en la configuración instalada.

## Bloque E. Compras y abastecimiento

  -----------------------------------------------------------------------
  Módulo                              Funciones
  ----------------------------------- -----------------------------------
  Proveedores                         Registro y clasificación

  Solicitudes de compra               Requerimientos internos

  Cotizaciones                        Solicitud y comparación de
                                      proveedores

  Órdenes de compra                   Autorización y emisión

  Recepción                           Registro de mercadería

  Control de calidad                  Inspección de entradas

  Facturas de proveedor               Registro de obligaciones, según
                                      disponibilidad contable

  Cuentas por pagar                   Control de vencimientos y pagos

  Reabastecimiento                    Necesidades de inventario

  Evaluación                          Desempeño de proveedores
  -----------------------------------------------------------------------

### Flujo de compras

``` text
Necesidad de abastecimiento
          ↓
Solicitud de compra
          ↓
Aprobación del responsable
          ↓
Cotizaciones de proveedores
          ↓
Comparación y selección
          ↓
Orden de compra
          ↓
Recepción de mercadería
          ↓
Control de calidad
          ↓
Ingreso al almacén
          ↓
Registro de factura y pago
```

Incorporaremos niveles de aprobación según el importe de compra. Por
ejemplo, una compra pequeña puede aprobarla el jefe de área, mientras
que una compra industrial importante necesitará autorización de
gerencia.

## Bloque F. Fabricación industrial de yeso

**Uno de los módulos centrales.** Se utilizará Manufacturing y se
integrará con inventario, calidad y mantenimiento según la
disponibilidad real de cada aplicación.

Procesos industriales:

1.  Recepción de piedra de yeso.
2.  Pesaje y registro.
3.  Trituración.
4.  Calcinación.
5.  Molienda.
6.  Clasificación.
7.  Mezclado de aditivos.
8.  Control de calidad.
9.  Envasado.
10. Almacenamiento de producto terminado.

### Configuración de fabricación

  Elemento            Ejemplo
  ------------------- ----------------------
  Materia prima       Piedra de yeso
  Insumo              Aditivo industrial
  Insumo              Material de envasado
  Producto final      Yeso fino 25 kg
  Centro de trabajo   Trituración
  Centro de trabajo   Calcinación
  Centro de trabajo   Molienda
  Centro de trabajo   Envasado

Crearemos listas de materiales (BOM) con consumos de referencia,
operaciones, centros de trabajo y tiempos estándar.

Cada orden de producción registrará:

-   Producto fabricado.
-   Cantidad planificada.
-   Cantidad producida.
-   Materias primas consumidas.
-   Operarios responsables.
-   Tiempo de operación.
-   Lote de fabricación.
-   Merma.
-   Rechazos.
-   Costo de producción, de acuerdo con la configuración disponible.
-   Resultado de calidad.

También contemplaremos subproductos, reprocesos y órdenes de fabricación
parciales cuando corresponda.

**Importante:** las fórmulas industriales iniciales serán ficticias para
pruebas. No las trataremos como recetas técnicas reales sin validación
de la empresa.

## Bloque G. Control de calidad

Tendremos controles en tres momentos:

  Momento              Control
  -------------------- ------------------------------------------------
  Recepción            Calidad de materias primas
  Producción           Temperatura, molienda, granulometría y humedad
  Producto terminado   Peso, presentación y calidad

Se registrarán:

-   Inspecciones.
-   Resultados.
-   Tolerancias.
-   Responsable.
-   Fecha.
-   Lote.
-   Aprobación o rechazo.
-   Acciones correctivas.

La disponibilidad de la aplicación Quality se verificará expresamente en
la edición Community instalada. Si no está disponible, se evaluará un
complemento compatible o una extensión propia sin duplicar
innecesariamente los modelos de inventario y fabricación.

## Bloque H. Mantenimiento industrial

Gestionaremos los equipos de la fábrica:

-   Trituradora.
-   Horno o calcinador.
-   Molino.
-   Mezcladora.
-   Envasadora.
-   Básculas.
-   Montacargas.
-   Vehículos de distribución.

Tendremos mantenimiento preventivo y correctivo, calendario, órdenes de
trabajo, repuestos, tiempos de parada y costos.

La disponibilidad de Maintenance en la edición instalada se verificará
antes de decidir si se utiliza la aplicación nativa, un complemento
compatible o una extensión.

## Bloque I. Puntos de venta

**Ocho POS.**

Cada sucursal tendrá su propia configuración comercial y sus cajeros.

Funciones:

-   Venta rápida.
-   Búsqueda por SKU.
-   Escaneo de códigos de barras, si está disponible.
-   Selección de clientes.
-   Descuentos autorizados.
-   Diferentes medios de pago.
-   Impresión de recibos internos.
-   Devoluciones.
-   Apertura y cierre de caja.
-   Control de efectivo.
-   Historial de ventas.
-   Reportes por cajero y sede.

### Flujo de caja

``` text
Cajero inicia sesión
        ↓
Abre caja con saldo inicial
        ↓
Realiza ventas
        ↓
Registra medios de pago
        ↓
Controla efectivo y movimientos
        ↓
Realiza cierre de caja
        ↓
Compara efectivo esperado y real
        ↓
Supervisor valida diferencias
        ↓
Cierre de sesión
```

No permitiremos que cualquier cajero modifique precios, elimine
operaciones o aplique descuentos extraordinarios sin autorización.

## Bloque J. Finanzas y administración contable

Debemos distinguir las funciones disponibles en Community de aquellas
que necesitan complementos adicionales o desarrollo propio.

Planificaremos:

-   Facturas de clientes y proveedores.
-   Cuentas por cobrar.
-   Cuentas por pagar.
-   Registro de pagos.
-   Caja y bancos.
-   Diarios contables.
-   Gastos.
-   Costos de fabricación.
-   Valoración de inventarios.
-   Reportes financieros disponibles.
-   Control de presupuestos, si la solución instalada lo permite.

No activaremos ninguna conexión tributaria externa. La facturación y
contabilidad serán de uso interno y de demostración hasta definir una
implementación fiscal real.

La valoración podrá configurarse con costo estándar, promedio o FIFO,
según el tipo de producto y la política empresarial y las opciones
soportadas por la instalación.

## Bloque K. Recursos humanos

  Módulo / entidad   Funciones
  ------------------ ---------------------------------------
  Empleados          Expedientes
  Departamentos      Organización
  Asistencia         Entradas y salidas
  Vacaciones         Solicitudes y aprobación
  Reclutamiento      Postulantes, si está disponible
  Evaluación         Desempeño
  Capacitación       Cursos y registros
  Contratos          Información laboral
  Nómina             Evaluación de una solución compatible

La nómina peruana completa se evaluará por separado porque requiere
localización y complementos específicos. No vamos a asumir que Odoo
Community trae todo lo necesario.

## Bloque L. Transporte y distribución

-   Gestión de vehículos.
-   Conductores.
-   Asignación de entregas.
-   Despachos por sede.
-   Registro de viajes.
-   Costos de transporte.
-   Entregas completas y parciales.
-   Devoluciones de mercadería.
-   Incidencias.
-   Seguimiento de entregas.

Se utilizará Fleet si está disponible y cubre las necesidades; los
procesos específicos de distribución se resolverán mediante
configuración o extensiones.

## Bloque M. Gestión documental

-   Documentos de proveedores.
-   Contratos.
-   Documentos internos.
-   Archivos de producción.
-   Certificados de calidad.
-   Manuales de maquinaria.
-   Documentos de empleados.
-   Adjuntos por operación.

La aplicación Documents se comprobará en la edición instalada. Si no
forma parte de Community, se evaluará una alternativa compatible o el
uso de adjuntos nativos de Odoo.

## Bloque N. Seguridad y auditoría

-   Roles empresariales.
-   Permisos por aplicación.
-   Restricciones por sucursal.
-   Control de almacenes.
-   Aprobaciones.
-   Registro de modificaciones.
-   Historial de operaciones.
-   Protección de información sensible.
-   Control de accesos.

La seguridad se aplicará en el servidor mediante grupos, ACL y reglas de
registro, no solamente ocultando menús.

## Bloque O. Reportes administrativos internos

Sin BSC y sin dashboards estratégicos externos.

Utilizaremos los reportes operativos disponibles y, cuando haga falta,
reportes complementarios propios:

-   Ventas por producto.
-   Ventas por sucursal.
-   Ventas por vendedor.
-   Inventario disponible.
-   Productos con baja existencia.
-   Compras por proveedor.
-   Costos de producción.
-   Mermas.
-   Calidad.
-   Cajas.
-   Cuentas pendientes.
-   Gastos.
-   Entregas.

# 4. Los flujos empresariales completos

Los módulos no pueden trabajar aislados: deben compartir información y
generar operaciones conectadas. Diseñaremos diez grandes flujos.

## Flujo 1. Abastecimiento de materia prima

``` text
Almacén detecta falta de materia prima
              ↓
Solicitud de abastecimiento
              ↓
Compras solicita cotizaciones
              ↓
Comparación de proveedores
              ↓
Aprobación de compra
              ↓
Orden de compra
              ↓
Recepción de materia prima
              ↓
Inspección de calidad
              ↓
Registro de lote
              ↓
Ingreso al almacén
              ↓
Actualización de inventario
              ↓
Registro de obligación al proveedor
```

**Resultado:** la empresa sabe qué compró, a quién, cuánto pagó, qué
recibió, dónde lo almacenó y qué cantidad tiene disponible.

## Flujo 2. Producción industrial

``` text
Planificación de producción
           ↓
Verificación de inventario
           ↓
Disponibilidad de materia prima
           ↓
Generación de orden de fabricación
           ↓
Reserva de componentes
           ↓
Preparación de materiales
           ↓
Trituración
           ↓
Calcinación
           ↓
Molienda
           ↓
Mezclado
           ↓
Control de calidad
           ↓
Envasado
           ↓
Registro de producto terminado
           ↓
Ingreso al almacén
```

**Resultado:** trazabilidad desde la materia prima hasta el saco de yeso
que se vende.

## Flujo 3. Distribución entre sucursales

``` text
Gerencia revisa existencias
          ↓
Sucursal solicita mercadería
          ↓
Almacén central verifica disponibilidad
          ↓
Se aprueba transferencia
          ↓
Preparación de productos
          ↓
Despacho
          ↓
Transporte
          ↓
Recepción en sucursal
          ↓
Validación de cantidades
          ↓
Actualización de inventario
```

La transferencia no se considerará completada simplemente porque salió
un camión. Debemos controlar su salida, tránsito, recepción y
diferencias.

## Flujo 4. Venta comercial

``` text
Cliente solicita productos
          ↓
Vendedor crea cotización
          ↓
Se revisa disponibilidad
          ↓
Se valida precio y descuento
          ↓
Se confirma pedido
          ↓
Se prepara mercadería
          ↓
Se entrega al cliente
          ↓
Se genera documento comercial interno
          ↓
Se registra pago o deuda
```

## Flujo 5. Venta en punto de venta

``` text
Cajero abre caja
       ↓
Busca producto o escanea código
       ↓
Registra cantidades
       ↓
Identifica cliente (si corresponde)
       ↓
Aplica descuentos autorizados
       ↓
Registra pago
       ↓
Confirma operación
       ↓
Actualiza inventario
       ↓
Emite recibo interno
       ↓
Finaliza venta
       ↓
Cierre de caja
```

## Flujo 6. Devoluciones y reclamos

``` text
Cliente solicita devolución
           ↓
Se identifica venta original
           ↓
Se revisa motivo
           ↓
Supervisor autoriza
           ↓
Se recibe el producto
           ↓
Control de calidad
           ↓
Producto reutilizable o defectuoso
           ↓
Reingreso o descarte
           ↓
Ajuste comercial y financiero
```

## Flujo 7. Mantenimiento industrial

``` text
Equipo registra horas de operación
           ↓
Se aproxima mantenimiento preventivo
           ↓
Se genera orden de mantenimiento
           ↓
Se asigna técnico
           ↓
Se registran repuestos y trabajos
           ↓
Se realiza mantenimiento
           ↓
Se valida funcionamiento
           ↓
Se cierra orden
```

## Flujo 8. Control de calidad

``` text
Recepción / producción / despacho
                 ↓
             Inspección
                 ↓
        Registro de resultados
                 ↓
           ¿Cumple calidad?
             /       \
           Sí         No
           ↓           ↓
     Aprobación     Cuarentena
           ↓           ↓
     Continuación    Evaluación
           ↓           ↓
        Inventario   Reproceso,
                     rechazo o descarte
```

## Flujo 9. Cobranza y cuentas por pagar

``` text
Operación comercial o compra
             ↓
Registro de documento interno
             ↓
Cuenta por cobrar / pagar
             ↓
Control de vencimiento
             ↓
Registro de abono o pago
             ↓
Conciliación y seguimiento
             ↓
Cierre administrativo
```

## Flujo 10. Cierre de operaciones diarias

Al final del día:

-   Los cajeros cierran sus sesiones.
-   Los supervisores revisan diferencias de caja.
-   Los almaceneros revisan movimientos pendientes.
-   Los vendedores verifican pedidos.
-   Producción informa cantidades y mermas.
-   Compras revisa recepciones pendientes.
-   Administración revisa documentos y pagos.

La gerencia podrá consultar el estado de las cinco sucursales desde un
mismo sistema, respetando los permisos.

# 5. Organización de los datos ficticios

No basta con crear 120 productos. Necesitamos datos relacionados entre
sí.

  Entidad                   Cantidad inicial propuesta
  ----------------------- ----------------------------
  Productos                                        120
  Categorías                                         6
  Clientes                                         250
  Proveedores                                       35
  Empleados                                         65
  Usuarios                                          40
  Sucursales                                         5
  Almacenes                                          5
  Puntos de venta                                    8
  Centros de trabajo                                 6
  Máquinas industriales                             12
  Vehículos                                          8
  Listas de materiales                              20
  Lotes iniciales                                   50
  Tarifas comerciales                                5
  Métodos de pago                                    4

Estos datos deben ser coherentes entre sí.

Por ejemplo:

-   Un proveedor vende piedra de yeso.
-   La piedra ingresa al almacén de Juliaca.
-   Producción consume esa piedra.
-   Se fabrica yeso fino.
-   El producto terminado recibe un lote.
-   El almacén central transfiere sacos a Puno.
-   La tienda de Puno vende esos sacos.
-   La caja registra el cobro.
-   El inventario se reduce.
-   El movimiento queda registrado.

Así podremos demostrar el ciclo completo del ERP.

Los registros de prueba serán ficticios y se identificarán como datos de
demostración. No se inventarán RUC, DNI u otros identificadores legales
que puedan confundirse con datos reales. Cuando se soliciten catálogos
completos, se definirán todos los registros y campos requeridos, sin
dejar valores genéricos como "pendiente de confirmar".

## Catálogo de productos de ejemplo

  -----------------------------------------------------------------------------
  Código        Producto      Presentación   Tipo             Precio de ejemplo
  ------------- ------------- -------------- ---------------- -----------------
  YES-001       Yeso Extra    Saco de 25 kg  Fabricado                 S/ 28.00
                Fino Andino                                   

  YES-002       Yeso          Saco de 40 kg  Fabricado                 S/ 35.00
                Industrial                                    

  PLA-001       Placa         Unidad         Comercializado            S/ 42.00
                estándar                                      

  DEC-001       Cornisa       Unidad         Comercializado            S/ 18.00
                decorativa                                    

  MAT-001       Piedra de     Tonelada       Materia prima            S/ 180.00
                yeso                                          
  -----------------------------------------------------------------------------

Los precios son únicamente ilustrativos; se establecerán los costos y
márgenes definitivos al cargar los datos.

# 6. Usuarios, roles y seguridad

Este punto es fundamental para que realmente parezca un ERP empresarial.

  Rol                        Acceso principal
  -------------------------- ------------------------------
  Administrador general      Configuración completa
  Gerente general            Visión de toda la empresa
  Gerente de sucursal        Operaciones de su sede
  Jefe de producción         Fabricación y calidad
  Supervisor de almacén      Inventarios y transferencias
  Comprador                  Compras y proveedores
  Vendedor                   CRM y ventas
  Cajero                     Su punto de venta
  Contador                   Información contable
  Responsable de RR. HH.     Personal
  Técnico de mantenimiento   Equipos y mantenimiento
  Auditor                    Consultas y trazabilidad

### Ejemplo de restricciones: cajero de Puno

-   Puede vender en su POS autorizado.
-   Puede consultar productos disponibles para su operación.
-   No puede modificar los costos de compra.
-   No puede cambiar inventarios manualmente.
-   No puede visualizar las operaciones privadas de la caja de Tacna.
-   No puede crear usuarios.
-   No puede eliminar ventas confirmadas.

Un gerente general podrá visualizar todas las sedes.

**Implementación técnica:** utilizaremos grupos, ACL, reglas de
registro, compañías, sucursales, almacenes y permisos propios donde sea
necesario. No basta con ocultar menús: las restricciones también deben
aplicarse en el servidor.

Las operaciones históricas confirmadas ---ventas, movimientos validados,
órdenes ejecutadas y auditoría--- no se borrarán físicamente. Se
utilizarán cancelaciones, reversas, devoluciones, correcciones trazables
o archivado según el tipo de registro.

# 7. Arquitectura de módulos: nativos y personalizados

No crearemos un módulo personalizado para algo que Odoo ya resuelve
correctamente.

## Estrategia

### Aplicaciones nativas de Odoo

Se conservarán las aplicaciones nativas que correspondan y estén
disponibles en la edición instalada:

-   Contacts.
-   CRM.
-   Sales.
-   Purchase.
-   Inventory.
-   Manufacturing.
-   Point of Sale.
-   Employees.
-   Fleet.
-   Invoicing y funciones contables disponibles.
-   Otras aplicaciones compatibles que se validen durante la auditoría.

La disponibilidad de Quality, Maintenance, Documents, Barcode y otras
aplicaciones debe verificarse contra Odoo 19 Community y el repositorio
instalado. No se asumirá que una función documentada para Enterprise
está incluida en Community.

### Personalizaciones propias de JJSUMI

Se crearán addons propios únicamente para complementar procesos que no
estén resueltos por Odoo nativo. La lista inicial de candidatos es:

``` text
jjsumi_core
jjsumi_branches_ext
jjsumi_security
jjsumi_approvals
jjsumi_catalog_ext
jjsumi_inventory_ext
jjsumi_purchase_ext
jjsumi_crm_ext
jjsumi_sales_ext
jjsumi_production_ext
jjsumi_quality_ext
jjsumi_maintenance_ext
jjsumi_pos_ext
jjsumi_distribution
jjsumi_hr_ext
jjsumi_accounting_ext
jjsumi_documents_ext
jjsumi_audit
jjsumi_reports
```

Esta lista es preliminar: cada addon tendrá dependencias explícitas y
solo se desarrollará si aporta funcionalidad real.

## Regla para personalizar las aplicaciones

La aplicación nativa seguirá siendo la base. Por ejemplo:

-   CRM utilizará los modelos nativos de oportunidades, clientes
    potenciales y actividades.
-   Contactos utilizará los contactos y empresas nativos.
-   Ventas utilizará cotizaciones, pedidos y líneas de venta nativas.
-   Inventario utilizará productos, ubicaciones, almacenes,
    transferencias y movimientos nativos.
-   Compras utilizará proveedores, solicitudes de cotización y órdenes
    de compra nativas.
-   Fabricación utilizará órdenes de fabricación, listas de materiales y
    operaciones nativas.
-   POS utilizará sesiones, pedidos y pagos nativos.
-   Empleados utilizará los registros nativos de empleados.

Se podrán añadir campos específicos, reglas de negocio, menús,
formularios, filtros, botones, reportes y permisos. No se crearán tablas
paralelas para duplicar entidades nativas.

## Ejemplo: experiencia CRM de JJSUMI

Al entrar a CRM se utilizará la aplicación CRM nativa, configurada y
extendida para los procesos comerciales de JJSUMI.

La interfaz podrá organizarse con menús y vistas de JJSUMI para:

-   Clientes potenciales.
-   Oportunidades.
-   Pipeline comercial.
-   Actividades.
-   Equipos de ventas.
-   Vendedores.
-   Seguimiento por sucursal.
-   Motivos de pérdida.
-   Reportes de oportunidades.

El formulario de oportunidad podrá incorporar, cuando se justifique:

-   Cliente o contacto.
-   Sucursal responsable.
-   Equipo comercial.
-   Vendedor.
-   Tipo de cliente.
-   Canal de captación.
-   Volumen estimado.
-   Importe estimado.
-   Probabilidad.
-   Fecha prevista de cierre.
-   Actividades y próximos pasos.
-   Observaciones.

Estos campos complementarios se añadirán al modelo nativo
correspondiente, no a un CRM independiente.

## Estructura técnica propuesta

``` text
/opt/odoo19/custom-addons/
│
├── jjsumi_core/
├── jjsumi_branches_ext/
├── jjsumi_security/
├── jjsumi_approvals/
├── jjsumi_catalog_ext/
├── jjsumi_inventory_ext/
├── jjsumi_purchase_ext/
├── jjsumi_crm_ext/
├── jjsumi_sales_ext/
├── jjsumi_production_ext/
├── jjsumi_quality_ext/
├── jjsumi_maintenance_ext/
├── jjsumi_pos_ext/
├── jjsumi_distribution/
├── jjsumi_hr_ext/
├── jjsumi_accounting_ext/
├── jjsumi_documents_ext/
├── jjsumi_audit/
└── jjsumi_reports/
```

No se modificarán directamente los archivos originales de Odoo. Se
utilizarán herencia de modelos, herencia de vistas, datos XML, seguridad
y mecanismos oficiales de extensión.

# 8. Plan de implementación por 11 fases

No desarrollaremos todos los módulos a la vez. Estableceremos
dependencias y criterios de aceptación. Cada fase debe especificarse,
aprobarse, implementarse y probarse antes de avanzar.

## Fase 01. CORE empresarial y gobierno corporativo

**Objetivo:** establecer la estructura organizativa, usuarios, seguridad
y reglas generales de JJSUMI.

Alcance:

-   Datos generales de la compañía.
-   Sucursales.
-   Departamentos.
-   Áreas.
-   Cargos y puestos.
-   Usuarios.
-   Roles y grupos de seguridad.
-   Permisos de acceso.
-   Restricciones por sucursal.
-   Responsables y jerarquías.
-   Aprobaciones generales.
-   Auditoría de operaciones sensibles.
-   Parámetros generales.
-   Secuencias y nomenclaturas.

Entregable: estructura empresarial y seguridad base operativas.

## Fase 02. Catálogo maestro de productos y servicios

**Objetivo:** disponer de un catálogo único y coherente para ventas,
compras, inventario y fabricación.

Alcance:

-   120 productos iniciales.
-   Seis categorías.
-   SKU y códigos de barras.
-   Productos almacenables, consumibles y servicios.
-   Variantes y presentaciones.
-   Unidades de medida.
-   Costos y precios.
-   Tarifas comerciales.
-   Proveedores asociados.
-   Impuestos internos de prueba.
-   Fichas técnicas e imágenes.
-   Reglas de seguimiento por lote cuando corresponda.

Entregable: catálogo maestro poblado y validado, usando los modelos
nativos de productos de Odoo.

## Fase 03. Inventario y almacenes

**Objetivo:** controlar existencias y movimientos de las cinco sedes.

Alcance:

-   Cinco almacenes.
-   Ubicaciones internas.
-   Recepciones.
-   Despachos.
-   Transferencias internas.
-   Transferencias entre sucursales.
-   Lotes y trazabilidad.
-   Inventarios físicos.
-   Ajustes autorizados.
-   Reposición.
-   Productos dañados y devoluciones.
-   Valoración de inventario según configuración disponible.

Entregable: inventario multisede funcional y trazable.

## Fase 04. Compras y abastecimiento

**Objetivo:** controlar las necesidades de compra y la relación con
proveedores.

Alcance:

-   35 proveedores de prueba.
-   Solicitudes internas.
-   Solicitudes de cotización.
-   Comparación de ofertas.
-   Aprobaciones por importe.
-   Órdenes de compra.
-   Recepciones.
-   Inspección de entrada.
-   Incidencias con proveedores.
-   Facturas y cuentas por pagar, según las capacidades contables
    disponibles.
-   Evaluación de proveedores.

Entregable: ciclo de compras completo.

## Fase 05. CRM y ventas

**Objetivo:** gestionar el proceso comercial desde el contacto inicial
hasta la entrega.

Alcance:

-   Clientes y contactos.
-   Clientes potenciales.
-   Oportunidades.
-   Pipeline.
-   Actividades.
-   Equipos y vendedores.
-   Cotizaciones.
-   Pedidos.
-   Tarifas.
-   Descuentos y aprobaciones.
-   Comisiones, si se confirma la solución compatible.
-   Entregas.
-   Devoluciones.
-   Reclamos.
-   Seguimiento comercial.

Entregable: ciclo comercial integrado con inventario y facturación
interna.

## Fase 06. Fabricación industrial

**Objetivo:** controlar la transformación de materias primas en
productos terminados.

Alcance:

-   20 listas de materiales iniciales.
-   Seis centros de trabajo.
-   Doce máquinas industriales.
-   Rutas y operaciones.
-   Órdenes de fabricación.
-   Planificación.
-   Reserva de componentes.
-   Consumos reales.
-   Producción parcial.
-   Lotes.
-   Mermas.
-   Reprocesos.
-   Subproductos, si corresponde.
-   Costos de fabricación según configuración soportada.

Entregable: producción trazable desde materias primas hasta producto
terminado.

## Fase 07. Calidad y mantenimiento

**Objetivo:** controlar la calidad de materiales y productos, y la
disponibilidad de equipos.

Alcance de calidad:

-   Controles de recepción.
-   Controles durante producción.
-   Controles de producto terminado.
-   Parámetros y tolerancias.
-   Inspecciones.
-   Aprobaciones y rechazos.
-   Cuarentena.
-   No conformidades.
-   Acciones correctivas.
-   Reprocesos.

Alcance de mantenimiento:

-   Equipos y máquinas.
-   Mantenimiento preventivo.
-   Mantenimiento correctivo.
-   Solicitudes y órdenes de trabajo.
-   Técnicos responsables.
-   Repuestos.
-   Costos.
-   Paradas de máquina.
-   Historial por equipo.

Entregable: calidad y mantenimiento integrados con fabricación e
inventario. La aplicación nativa o alternativa se elegirá tras verificar
disponibilidad Community.

## Fase 08. Ocho puntos de venta

**Objetivo:** operar los ocho puntos de venta con control de caja y
existencias.

Alcance:

-   Ocho configuraciones POS.
-   Cajeros y supervisores.
-   Sesiones.
-   Apertura y cierre.
-   Métodos de pago.
-   Ventas.
-   Descuentos autorizados.
-   Devoluciones.
-   Control de efectivo.
-   Diferencias de caja.
-   Reportes por tienda y cajero.
-   Integración con inventario y clientes.

Entregable: ocho POS configurados y probados.

## Fase 09. Finanzas y administración económica

**Objetivo:** disponer de control financiero interno conectado con
compras, ventas, inventario y producción.

Alcance:

-   Cuentas por cobrar.
-   Cuentas por pagar.
-   Registro de pagos.
-   Caja y bancos.
-   Diarios.
-   Gastos.
-   Facturas internas.
-   Costos.
-   Valoración de inventario.
-   Conciliaciones, si están disponibles.
-   Reportes financieros soportados.
-   Presupuestos, si se confirma una solución compatible.

No se implementará SUNAT en esta etapa.

Entregable: administración financiera interna operativa dentro de las
capacidades verificadas de Odoo Community y complementos aprobados.

## Fase 10. Recursos humanos y logística empresarial

**Objetivo:** administrar al personal y las operaciones de transporte y
distribución.

Alcance de RR. HH.:

-   65 empleados ficticios.
-   Departamentos y responsables.
-   Expedientes.
-   Asistencia.
-   Ausencias y vacaciones.
-   Contratos y documentos.
-   Reclutamiento y capacitación, si se dispone de las aplicaciones
    adecuadas.
-   Nómina peruana: fuera de alcance hasta evaluar localización y
    complementos.

Alcance de logística:

-   Ocho vehículos.
-   Conductores.
-   Asignación de entregas.
-   Viajes.
-   Despachos.
-   Entregas completas y parciales.
-   Incidencias.
-   Devoluciones.
-   Costos de transporte.

Entregable: gestión del personal y transporte integrada.

## Fase 11. Integración, pruebas y puesta en producción

**Objetivo:** validar el ERP completo y prepararlo para evaluación
empresarial.

Alcance:

-   Pruebas integrales de los diez flujos empresariales.
-   Pruebas de permisos.
-   Pruebas por sucursal.
-   Pruebas de concurrencia.
-   Pruebas de rendimiento.
-   Validación de integridad de datos.
-   Auditoría.
-   Backups.
-   Restauración.
-   Documentación técnica.
-   Manuales de usuario.
-   Capacitación.
-   Procedimientos de despliegue y actualización.

Entregable: ERP integrado, documentado, probado y preparado para
evaluación y despliegue controlado.

# 9. Infraestructura para trabajar a escala empresarial

Mantendremos AWS como alojamiento, pero comprobaremos la capacidad real
antes de definir cuántos trabajadores simultáneos podrá soportar.

Arquitectura objetivo:

``` text
USUARIOS EMPRESARIALES
Administración · Fábrica · Sucursales · POS
                  │
                  ▼
             NGINX / HTTPS
       Dominio · Certificados · Proxy
                  │
                  ▼
                ODOO 19
       Workers · Aplicaciones · Cron
                  │
                  ▼
              POSTGRESQL
       Base empresarial · Transacciones
                  │
          ┌───────┴────────┐
          ▼                ▼
       BACKUPS            LOGS
     Recuperación       Monitoreo
```

Antes de definir workers y conexiones simultáneas necesitamos conocer:

-   Tipo y tamaño de instancia EC2.
-   CPU.
-   Memoria RAM.
-   Almacenamiento.
-   Versión y configuración de PostgreSQL.
-   Número esperado de usuarios concurrentes.
-   Uso previsto de POS y operaciones de fábrica.
-   Política de respaldos y recuperación.

No asignaremos una configuración de producción a ciegas.

# 10. Pruebas de aceptación del ERP

Cada módulo debe demostrar que funciona dentro de un proceso
empresarial.

  -----------------------------------------------------------------------
  Prueba                              Resultado esperado
  ----------------------------------- -----------------------------------
  Crear producto                      Se registra correctamente en el
                                      catálogo nativo

  Registrar compra                    Se genera una orden de compra

  Recibir mercadería                  Aumenta el inventario en la
                                      ubicación correcta

  Crear producción                    Se reserva y consume materia prima
                                      según la orden

  Terminar producción                 Se registra producto terminado y su
                                      lote

  Transferir a Puno                   Se mueve stock entre almacenes con
                                      trazabilidad

  Vender en Puno                      Se reduce el inventario
                                      correspondiente

  Vender en POS                       Se registra pedido y pago

  Cerrar caja                         Se obtiene balance de caja y
                                      diferencias

  Devolver producto                   Se procesa la devolución vinculada
                                      a la operación original

  Consultar desde Juliaca             Gerencia visualiza las cinco sedes
                                      según permisos

  Acceso de cajero                    No accede a funciones
                                      administrativas no autorizadas

  Registrar mantenimiento             Se genera historial del equipo

  Revisar auditoría                   Se identifica quién realizó una
                                      operación sensible
  -----------------------------------------------------------------------

Además, realizaremos pruebas de concurrencia: por ejemplo, varios
cajeros vendiendo simultáneamente el mismo producto mientras los
almacenes reciben y transfieren mercadería.

# 11. Documentación que mantendremos durante el proyecto

Crearemos una documentación organizada:

``` text
JJSUMI-ODOO-ENTERPRISE/
│
├── 01-ARQUITECTURA/
│   ├── arquitectura-general.md
│   ├── arquitectura-odoo.md
│   └── infraestructura-aws.md
│
├── 02-REQUERIMIENTOS/
│   ├── requerimientos-funcionales.md
│   ├── requerimientos-no-funcionales.md
│   └── reglas-negocio.md
│
├── 03-MODULOS/
│   ├── core.md
│   ├── inventario.md
│   ├── compras.md
│   ├── ventas.md
│   ├── fabricacion.md
│   ├── calidad.md
│   ├── mantenimiento.md
│   ├── pos.md
│   ├── finanzas.md
│   ├── recursos-humanos.md
│   └── logistica.md
│
├── 04-FLUJOS/
│   ├── compras.md
│   ├── ventas.md
│   ├── produccion.md
│   ├── transferencias.md
│   └── pos.md
│
├── 05-SEGURIDAD/
│   ├── roles.md
│   ├── permisos.md
│   └── auditoria.md
│
├── 06-DATOS/
│   ├── catalogos.md
│   ├── datos-maestros.md
│   └── datos-prueba.md
│
├── 07-PRUEBAS/
│   ├── casos-prueba.md
│   └── resultados.md
│
└── 08-DESPLIEGUE/
    ├── instalacion.md
    ├── actualizacion.md
    └── respaldos.md
```

Esta documentación será nuestra referencia para trabajar con OpenCode,
implementar los módulos y evitar que se pierdan decisiones de
arquitectura.

# 12. Decisiones que debemos cerrar antes de programar

La propuesta inicial contempla estas decisiones empresariales:

  Tema                     Propuesta
  ------------------------ --------------------------------------------------
  Estructura empresarial   Una empresa con cinco sucursales
  Sucursales               Juliaca, Puno, Arequipa, Cusco y Tacna
  Fabricación              Industrial completa
  Puntos de venta          Ocho, distribuidos en las cinco sedes
  Datos iniciales          Datos ficticios realistas, relacionados entre sí
  Plataforma               Odoo 19 Community
  Aplicaciones             Nativas de Odoo, según disponibilidad
  Personalización          Extensiones complementarias propias

Los datos y cantidades anteriores constituyen el escenario inicial de
planificación. Los registros completos se especificarán antes de
cargarlos. No se crearán empresas, bases de datos ni registros en
producción sin autorización.

# 13. Cómo se desarrollará cada fase

Para evitar que el proyecto termine siendo una colección de módulos
instalados sin integración, todas las fases seguirán el mismo
procedimiento.

1.  **Especificación funcional:** definir qué necesita JJSUMI, quién lo
    utilizará, qué información manejará y qué operaciones podrá
    realizar.
2.  **Revisión de Odoo nativo:** identificar qué resuelve Odoo sin
    cambios, qué requiere configuración y qué necesita una extensión
    propia.
3.  **Diseño de datos:** definir modelos, campos, relaciones, catálogos,
    estados y registros completos de prueba.
4.  **Diseño de interfaz:** especificar menús, formularios, listas,
    Kanban, botones, filtros, acciones y reportes.
5.  **Diseño de seguridad:** definir grupos, permisos CRUD,
    restricciones por sucursal y aprobaciones.
6.  **Implementación:** configurar Odoo y desarrollar únicamente las
    extensiones necesarias.
7.  **Carga de datos:** incorporar los registros aprobados, evitando
    duplicados y protegiendo los datos existentes.
8.  **Pruebas:** ejecutar los casos de prueba funcionales, de seguridad
    y de integración.
9.  **Aprobación:** documentar los resultados y comprobar los criterios
    de aceptación antes de avanzar.

Cada fase tendrá una ficha técnica con:

-   Objetivo y alcance.
-   Aplicaciones nativas involucradas.
-   Módulos técnicos y dependencias.
-   Funcionalidades nativas que se conservarán.
-   Configuraciones que se realizarán.
-   Extensiones propias justificadas.
-   Modelos y campos.
-   Registros de prueba completos.
-   Formularios y vistas.
-   Menús y botones.
-   Reglas de negocio.
-   CRUD y permisos.
-   Procesos y automatizaciones.
-   Reportes.
-   Pruebas y criterios de aceptación.

No pasaremos automáticamente a la fase siguiente porque el código
compile: deberá funcionar y superar sus pruebas.

# 14. Qué queda fuera del alcance

  Elemento                                           Decisión
  -------------------------------------------------- -------------------------------
  Integración SUNAT                                  No implementar ahora
  Integración RENIEC                                 No implementar ahora
  BSC Enterprise                                     Proyecto independiente futuro
  Reconstrucción de CRM                              No realizar
  Reconstrucción de Ventas                           No realizar
  Reconstrucción de Inventario                       No realizar
  Sustitución del POS nativo                         No realizar
  Modificación directa del código original de Odoo   No realizar
  Eliminación de información existente               No realizar
  Creación de una base nueva sin autorización        No realizar

Si una aplicación nativa no está disponible en Community, primero
evaluaremos una alternativa compatible, un complemento OCA o un
desarrollo propio. No asumiremos que una función Enterprise está
incluida en Community.

# 15. Decisiones definitivas de arquitectura

  -----------------------------------------------------------------------
  Tema                                Decisión
  ----------------------------------- -----------------------------------
  Empresa                             JJSUMI

  ERP                                 Odoo 19 Community

  Arquitectura empresarial            Una compañía principal con cinco
                                      sucursales propuestas

  Aplicaciones                        Nativas de Odoo

  Personalización                     Extensiones complementarias propias

  Código original                     Se conserva sin modificaciones
                                      directas

  Datos                               Información de JJSUMI y datos
                                      ficticios de prueba

  Puntos de venta                     Ocho

  Almacenes                           Cinco propuestos

  Productos iniciales                 120

  Clientes de prueba                  250

  Proveedores de prueba               35

  Empleados de prueba                 65

  Usuarios previstos                  40

  SUNAT y RENIEC                      Excluidos

  BSC                                 Excluido

  Base existente `jjsumi`             Se conserva y protege

  Implementación                      Once fases aprobadas
                                      individualmente
  -----------------------------------------------------------------------

## La diferencia fundamental respecto a un Odoo estándar

No buscamos instalar Odoo y dejarlo tal como viene.

Buscamos utilizar sus aplicaciones nativas, pero configurar y ampliar
sus operaciones para que representen los procesos reales de JJSUMI.

Por ejemplo:

-   Al entrar a CRM, se gestionarán las oportunidades y actividades
    comerciales de JJSUMI.
-   Al entrar a Inventario, se administrarán sus cinco almacenes y sus
    movimientos.
-   Al entrar a Compras, se gestionarán sus proveedores, solicitudes,
    aprobaciones y recepciones.
-   Al entrar a Fabricación, se controlarán las órdenes y procesos de
    producción.
-   Al entrar a POS, se administrarán sus ocho puntos de venta.
-   Al entrar a Empleados, se consultará la estructura del personal y
    sus relaciones empresariales.

Todo estará conectado mediante los modelos y procesos de Odoo, con las
extensiones necesarias.

**La regla acordada es conservar lo nativo y agregar la información,
configuración y extensiones específicas de JJSUMI.** No construiremos
aplicaciones paralelas ni duplicaremos los modelos existentes.

# 16. Primer trabajo antes de comenzar la Fase 01

Antes de diseñar los formularios y registros definitivos del CORE,
debemos auditar lo que ya está instalado en AWS.

La auditoría no modificará datos. Su propósito será conocer qué tenemos,
qué está instalado, qué existe en la base `jjsumi` y qué se puede
reutilizar.

Revisaremos:

1.  Versión exacta de Odoo.
2.  Estado de `odoo19.service`.
3.  Versión de PostgreSQL.
4.  Existencia y estado de la base `jjsumi`.
5.  Empresa o empresas registradas.
6.  Aplicaciones nativas instaladas.
7.  Addons personalizados existentes.
8.  Estado y propósito de `jjsumi_accounting`.
9.  Configuración de `addons_path`.
10. Usuarios y permisos existentes.
11. Configuración de sucursales y almacenes.
12. Recursos de la instancia EC2.
13. Respaldos y posibilidades de restauración.

**No instalaremos, actualizaremos, eliminaremos ni modificaremos nada
durante esa auditoría.**

# 17. Orden de trabajo acordado

El orden correcto es:

1.  Auditar la instalación actual, sin modificar la base ni los módulos
    existentes.
2.  Cerrar la arquitectura técnica, confirmando aplicaciones Community,
    dependencias y extensiones.
3.  Especificar completamente la Fase 01: todos los registros, campos,
    formularios, permisos y procesos.
4.  Implementar y probar la Fase 01 únicamente después de aprobar su
    especificación.
5.  Continuar ordenadamente hasta la Fase 11, sin saltar etapas ni
    duplicar funcionalidades nativas.

## Objetivo final

La meta es que JJSUMI tenga un ERP empresarial integrado sobre Odoo 19,
conservando su tecnología nativa y ampliándola de forma ordenada, segura
y mantenible.

Una operación iniciada en cualquiera de las cinco sucursales debe poder
seguirse hasta su resultado final dentro del mismo Odoo. Esa será
nuestra medida de un ERP empresarial realmente integrado.

------------------------------------------------------------------------

## Referencias técnicas oficiales

La documentación oficial de Odoo 19 será la referencia para validar las
funciones nativas, la arquitectura de módulos, la seguridad y los
procesos:

-   [Documentación de Inventario Odoo
    19](https://www.odoo.com/documentation/19.0/es/applications/inventory_and_mrp/inventory.html)
-   [Documentación de Fabricación y cadena de suministro Odoo
    19](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp.html)
-   [Documentación de Punto de Venta Odoo
    19](https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/use.html)
-   [Documentación de desarrollo de módulos Odoo
    19](https://www.odoo.com/documentation/19.0/developer/tutorials.html)
-   [Documentación de seguridad y control de acceso Odoo
    19](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)

La disponibilidad y alcance de cada aplicación se contrastarán con la
edición Community y los addons presentes en el servidor.

------------------------------------------------------------------------

**Documento maestro de planificación de JJSUMI ERP --- Odoo 19
Community.**

**Estado:** planificación general. No autoriza por sí misma cambios en
la instalación, base de datos o información existente.
