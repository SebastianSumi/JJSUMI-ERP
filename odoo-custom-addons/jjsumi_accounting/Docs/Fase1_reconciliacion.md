# Informe de reconciliación — Fase 01 JJSUMI
**Fecha:** 2026-11-17 · **Base:** jjsumi · **Regla:** EMP manda; sede del empleado manda; mapa cargo→rol; sin borrados.

## 1. Responsables de departamento corregidos (6)

| Depto | Original (nombre / EMP citado) | Corregido | Motivo |
|---|---|---|---|
| DEP-006 Auditoría | Luis Fernando / EMP-012 | **Laura Patricia Rojas / EMP-017** | EMP-012 es Analista RRHH; Laura es Auditora Interna (CAR-012) |
| DEP-007 Producción | David Alberto / EMP-019 | **Gabriela Sofia Vargas / EMP-019** | EMP-019 = Gabriela (Jefe de Planta); David = EMP-008 Contador |
| DEP-008 Calidad | Carmen Rosa / EMP-029 | **Francisco Javier Aguilar / EMP-030** | EMP-029 = Diana (Cajero); Carmen = EMP-009 Asistente Contable; Francisco Inspector Calidad |
| DEP-009 Mantenimiento | Pedro Juan / EMP-033 | **Natalia Sofia Espinoza / EMP-033** | EMP-033 = Natalia (Jefe Mantenimiento); Pedro = EMP-010 Asistente |
| DEP-010 Almacenes | Miguel Angel / EMP-038 | **Eduardo Jose Torres / EMP-038** | EMP-038 = Eduardo (Jefe Almacén); Miguel = EMP-006 Gerente Sucursal |
| DEP-011 Compras | Elena Maria / EMP-046 | **Sebastian Luis Huanca / EMP-046** | EMP-046 = Sebastián (Jefe Compras); Elena = EMP-005 Gerente Sucursal |
| DEP-012 Comercial | Jose Luis / EMP-050 | **Tomas Alberto Paredes / EMP-050** | EMP-050 = Tomás (Jefe Comercial); Jose = EMP-016 Soporte |

DEP-001…DEP-005 ya coincidían.

## 2. Responsables de área corregidos (8)

| Área | Original | Corregido | Motivo |
|---|---|---|---|
| ARE-013 | Carmen / EMP-029 | **Beatriz Elena Paredes / EMP-031** | Código EMP equivocado; Beatriz Inspector Calidad |
| ARE-014 | Claudia / EMP-030 | **Francisco Javier Aguilar / EMP-030** | EMP-030 = Francisco; Claudia = EMP-021 Supervisora Producción |
| ARE-015 | Pedro / EMP-033 | **Natalia Sofia Espinoza / EMP-033** | Como DEP-009 |
| ARE-016 | Miguel / EMP-038 | **Eduardo Jose Torres / EMP-038** | Como DEP-010 |
| ARE-017 | Elena / EMP-046 | **Sebastian Luis Huanca / EMP-046** | Como DEP-011 |
| ARE-018 | Jose / EMP-050 | **Tomas Alberto Paredes / EMP-050** | Como DEP-012 |
| ARE-019 | Laura / EMP-054 | **Julian Alberto Mamani / EMP-054** | EMP-054 = Julian (Vendedor SEDE-002); Laura = EMP-017 Auditora |
| ARE-020 | Diego / EMP-043 | **Camila Sofia Delgado / EMP-043** | EMP-043 = Camila (Coord. Distribución); Diego = EMP-022 Cajero |

## 3. Roles vs cargos — mapa cargo→rol aplicado

Se añadieron cargos **CAR-026 Cajero** y **CAR-027 Gerente de Sucursal**.

| Corrección | Detalle |
|---|---|
| Cajeros USR-022…029 | Cargo del empleado → **CAR-026**; rol **ROL-008** coherente |
| Gerentes de sucursal USR-004/005/006 | Cargo → **CAR-027**; rol **ROL-003**; sedes EMP-001/002/003 |
| USR-007 Sofia | **Ya no** Gerente de Sucursal (sede EMP=SEDE-001); rol **ROL-009** por CAR-005 Jefe de Finanzas |
| USR-008 David | **Ya no** Gerente de Sucursal; rol **ROL-009** por CAR-006 Contador |
| USR-009 Carmen (ex Jefe Producción) | Asistente Contable → **sin rol operativo** |
| USR-017/018 (ex Vendedores) | Auditor Interno → **ROL-012** |
| USR-019/020/021 (ex Vendedores) | Producción → **ROL-004** |
| USR-030/031/032 (ex Contador/RRHH/Mant) | Inspector Calidad → **ROL-014** |
| USR-033…037 | Mantenimiento → **ROL-011** |
| USR-038/039/040 (ex Vendedores) | Almacén → **ROL-005** |
| Excepciones documentadas | USR-002 Ana y USR-014 Juan → ROL-001 (soporte gerencia / admin TI) |

## 4. Sedes de usuarios = sedes de empleados (12 correcciones)

| Usuario | Sede USR (antes) | Sede EMP (válida) |
|---|---|---|
| Sofía Medina USR-007 | SEDE-004 | **SEDE-001** |
| David Huanca USR-008 | SEDE-005 | **SEDE-001** |
| Fernando Huanca USR-018 | SEDE-002 | **SEDE-001** |
| Gabriela Vargas USR-019 | SEDE-003 | **SEDE-001** |
| Ricardo Torres USR-020 | SEDE-004 | **SEDE-001** |
| Claudia Aguilar USR-021 | SEDE-005 | **SEDE-001** |
| Verónica USR-023 | SEDE-002 | **SEDE-001** |
| Alejandro USR-024 | SEDE-003 | **SEDE-001** |
| Patricia USR-025 | SEDE-004 | **SEDE-001** |
| Raúl USR-026 | SEDE-005 | **SEDE-001** |
| Héctor USR-028 | SEDE-002 | **SEDE-001** |
| Diana USR-029 | SEDE-003 | **SEDE-001** |

## 5. Gaps documentados (sin inventar datos)

1. **SEDE-004 y SEDE-005 sin Gerente de Sucursal con cuenta** entre los 40 usuarios (sus empleados designados en el doc original tenían sede EMP SEDE-001). Candidatos sin usuario: EMP-058/059 (Cusco), EMP-060/061 (Tacna).
2. **Cajeros todos en SEDE-001** según EMP; los 8 POS por sede se afinan en Fase 8.
3. **Sin usuario con cargo Comprador/Jefe Compras** entre los 40 (EMP-046…049 sin cuenta); ROL-006 no asignado.
4. **Sin usuarios en ROL-007 Vendedor ni ROL-013 Supervisor Comercial** entre los 40 (EMP-050+ sin cuenta). Cubrir en fase comercial con padrón autorizado.
5. Compañía matriz se mantiene como **«JJSumi»** (no se renombra a S.A.C. sin autorización).

## 6. Datos existentes conservados (sin borrado)

- 21 empleados legacy (Ana Sucasaca … Carmen Flores) y 21 usuarios activos (admin + vendedor01…20) **se conservan**.
- Departamento legacy «Administración» (id=1) **se conserva**; se crean DEP-001…012 con código `jjsumi_code`.
- Nuevos registros se añaden sin duplicar logins del padrón Fase 1.

## 7. Validaciones Odoo añadidas (constraints propios)

- Código único DEP/ARE/CAR/EMP/SEDE (`models.Constraint`; en Odoo 19 `_sql_constraints` no se aplica).
- Departamento y cargo obligatorios en empleados con código JJSUMI (también en `hr.version`).
- Sede del empleado coherente con la sede del usuario vinculado, también al cambiar la sucursal del empleado.
- Responsable DEP/ARE con cargo de jefatura compatible.
- `usuario.sede == empleado.sede`.
- Rol asignado ∈ mapa cargo→rol (+ excepciones).
- Cajero exige cargo CAR-026; Gerente Sucursal exige CAR-027.
- No autoaprobación en APR.

## 8. Instalación y verificación (2026-11-19)

- Módulos instalados: `jjsumi_org`, `jjsumi_security`, `jjsumi_audit`, `jjsumi_approvals`, `jjsumi_core`, `jjsumi_home_cards`.
- Carga desde `jjsumi_core/data/padron.json` mediante `jjsumi.seed.load_fase1()` (`data/load_fase1.xml`). Idempotente: una segunda ejecución no cambia conteos.
- Conteos: 5 sucursales, 12 departamentos, 20 áreas, 27 cargos, 15 roles, 65 empleados, 40 usuarios vinculados.
- Pruebas: 42 comprobaciones (estructura, coherencia, restricciones negativas, visibilidad por sucursal, ACL, aprobaciones, auditoría, menús, seguridad de datos, idempotencia). Script: `jjsumi_core/scripts/tests_fase1.py`. Resultado: 42/42.
- Correcciones durante la verificación: restricciones SQL inactivas en Odoo 19; departamento/cargo obligatorios no aplicados vía `hr.version`; cambio de sucursal del empleado sin revalidar al usuario; excepción inexistente `models.UserError` en auditoría; reescritura de `parent_id` en la recarga.
- Operativo: los intentos fallidos dejaron 6 archivos de filestore con propietario `ubuntu`; se eliminaron (no referenciados). La instalación debe ejecutarse como usuario `odoo`.

## 9. Pendientes sin decidir

1. USR-014 (ROL-001 en padrón frente a ROL-005 en la tabla).
2. Grupo de RR. HH. para ROL-010 (USR-031); hoy solo ve `hr.employee.public`.
3. Tarjeta CORE del inicio abre Usuarios, no el menú CORE.
4. 21 empleados heredados visibles para todos los usuarios con la compañía matriz.
5. Contraseñas e invitaciones: no enviadas; los usuarios no pueden ingresar aún.

## 10. Anexo APR v1.2 — Catálogo de aprobaciones (pendiente de aprobación)

Estado: **propuesta v1.2**. No implementada. Requiere aprobación formal antes de cambiar código.

### 10.1 Catálogo

| Código | Solicitud | Aprobadores | Regla |
|---|---|---|---|
| APR-001 | Alta de usuario | RR. HH. (ROL-010, CAR-008) + Administrador ERP (ROL-001) | ALL |
| APR-002 | Cambio de rol/permisos | Administrador ERP (ROL-001) | Simple |
| APR-003 | Alta de empleado | Jefatura de RR. HH. (CAR-008) | Simple |
| APR-004 | Cambio de departamento | RR. HH. (ROL-010) | Simple |
| APR-005 | Cambio de sucursal | Gerente General (ROL-002, CAR-001) | Simple |
| APR-006 | Cambio de cargo | RR. HH. (ROL-010) | Simple |
| APR-007 | Baja de usuario | Administrador ERP (ROL-001) | Simple |
| APR-008 | Desactivación de empleado | RR. HH. (ROL-010) + Gerente General (ROL-002, CAR-001) | ALL |
| APR-009 | Modificación de estructura | Gerente General (ROL-002, CAR-001) | Simple |
| APR-010 | Excepción de acceso multisucursal | Gerente General (ROL-002, CAR-001) + Administrador ERP (ROL-001) | ALL |

"Administrador CORE" equivale a ROL-001 Administrador ERP. "Gerencia" y "Gerencia General" equivalen a ROL-002 Gerente General (CAR-001).

### 10.2 Reglas

1. **Aprobación ALL:** en APR-001, 008 y 010 la solicitud permanece en *En revisión* hasta que ambos aprobadores aprueben. Cada aprobador emite su decisión individual.
2. **Rechazo inmediato:** si cualquier aprobador rechaza, la solicitud pasa a *Rechazada*.
3. **No autoaprobación:** ninguna solicitud puede ser aprobada por su solicitante, en ningún tipo, incluido APR-010.
4. **Solicitante aprobador:** si el solicitante es uno de los aprobadores requeridos, la solicitud queda bloqueada y se escala para designar un aprobador independiente. No se reduce ALL a una sola aprobación.
5. **Ejecución manual:** una solicitud aprobada pasa a *Aprobada*. Una persona autorizada la marca como *Ejecutada*. El cambio de rol o departamento no se aplica automáticamente en Fase 1.
6. **Auditoría:** cada decisión individual, cada cambio de estado y la ejecución quedan registrados en `jjsumi.audit.event`.

### 10.3 Modelo requerido (a implementar tras aprobación)

- Catálogo de 10 códigos APR con aprobadores requeridos por código.
- Tabla de aprobaciones individuales por solicitud: aprobador, decisión, fecha, comentario y orden. Sustituye al campo único `approver_id`.
- Regla ALL y rechazo inmediato.
- Validación de no autoaprobación y de solicitante aprobador.
- Estados: Borrador, Enviada, En revisión, Aprobada, Rechazada, Ejecutada, Cancelada.

### 10.4 Fuera de Fase 1

- Modelo de delegación con sustituto y vigencia (§12 "Delegaciones"; se registra como pendiente).
- Automatización de la ejecución de cambios de rol o departamento.
- Reglas de aprobación configurables desde la interfaz.

### 10.5 Aprobación

- Aprobado por: ____________________  Fecha: __________
