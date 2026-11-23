# Pruebas Fase 01 JJSUMI. No se importa desde el módulo (no es un test de Odoo).
# Ejecución (como usuario odoo):
#   echo "exec(open('/opt/odoo19/custom-addons/jjsumi_core/scripts/tests_fase1.py').read())" | sudo -u odoo /opt/odoo19/venv/bin/python /opt/odoo19/odoo/odoo-bin shell -c /etc/odoo19.conf -d jjsumi --no-http --log-level=warn

import json
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.modules.module import get_module_path
from odoo.addons.jjsumi_security.models.res_users import CARGO_ROLES, EXCEPCIONES, ROLE_XML

_path = get_module_path('jjsumi_core') + '/data/padron.json'
PAD = json.load(open(_path, encoding='utf-8'))
RESULTS = []


def rec(code, label, ok, detail=''):
    RESULTS.append((code, label, bool(ok), detail))
    print('%s %s %s %s' % ('PASS' if ok else 'FAIL', code, label, detail))


class _Sentinel(Exception):
    pass


def U(login):
    return env['res.users'].search([('login', '=', login)], limit=1)


def E(code):
    return env['hr.employee'].search([('jjsumi_code', '=', code)], limit=1)


def SEDE(code):
    return env['res.company'].search([('jjsumi_code', '=', code)], limit=1)


def DEP(code):
    return env['hr.department'].search([('jjsumi_code', '=', code)], limit=1)


def ARE(code):
    return env['jjsumi.area'].search([('code', '=', code)], limit=1)


def expect_raise(code, label, fn):
    """Ejecuta fn dentro de savepoint; debe lanzar excepción. Siempre revierte."""
    outcome = None
    try:
        with env.cr.savepoint():
            fn()
            raise _Sentinel()
    except _Sentinel:
        outcome = (False, 'no lanzó excepción')
    except Exception as exc:  # noqa
        outcome = (True, type(exc).__name__)
    env.invalidate_all()
    rec(code, label, outcome[0], outcome[1])


def in_rollback(fn):
    """Ejecuta fn y devuelve su resultado; revierte todos los cambios."""
    box = {}
    try:
        with env.cr.savepoint():
            box['r'] = fn()
            raise _Sentinel()
    except _Sentinel:
        pass
    except Exception as exc:  # noqa
        box['err'] = '%s: %s' % (type(exc).__name__, str(exc)[:160])
    env.invalidate_all()
    return box.get('r')


# ---------------------------------------------------------------- ESTRUCTURA
sedes_pad = PAD['sedes']
main = env.ref('base.main_company')
sedes_db = env['res.company'].search([('jjsumi_code', 'like', 'SEDE-')])
rec('S01', 'Sucursales: 5 compañías hijas de la matriz',
    len(sedes_db) == len(sedes_pad) == 5 and all(s.parent_id == main for s in sedes_db),
    'n=%d' % len(sedes_db))
rec('S02', 'Sucursales: nombre, calle, ciudad y país según padrón',
    all(SEDE(r[0]).name == r[1] and SEDE(r[0]).city == r[2] and SEDE(r[0]).country_id == env.ref('base.pe') for r in sedes_pad))
rec('S03', 'Departamentos: 12, jerarquía coincide con padrón',
    env['hr.department'].search_count([('jjsumi_code', 'like', 'DEP-')]) == len(PAD['deps']) == 12
    and all((DEP(r[0]).parent_id.jjsumi_code or None) == r[2] for r in PAD['deps']))
rec('S04', 'Áreas: 20, departamento asignado según padrón',
    env['jjsumi.area'].search_count([]) == len(PAD['areas']) == 20
    and all(ARE(r[0]).department_id.jjsumi_code == r[2] for r in PAD['areas']))
rec('S05', 'Cargos: 27 (25 de la especificación + CAR-026 y CAR-027)',
    env['hr.job'].search_count([('jjsumi_code', 'like', 'CAR-')]) == len(PAD['jobs']) == 27)
rec('S06', 'Roles: 15 grupos JJSUMI',
    env['res.groups'].search_count([('privilege_id.name', '=', 'JJSUMI Roles')]) == 15)

emp_ok = True
for r in PAD['emps']:
    e = E(r[0])
    if not (e and e.name == r[1] and e.department_id.jjsumi_code == r[2]
            and e.jjsumi_area_id.code == r[3] and e.job_id.jjsumi_code == r[4]
            and e.company_id.jjsumi_code == r[5]):
        emp_ok = False
        print('   mismatch', r[0])
rec('E01', 'Empleados: 65 con dept/área/cargo/sede según padrón', emp_ok and env['hr.employee'].search_count([('jjsumi_code', 'like', 'EMP-')]) == 65)

usr_ok = True
for r in PAD['usrs']:
    u = U(r[2])
    if not (u and u.name == r[1] and u.email == r[3] and E(r[4]).user_id == u):
        usr_ok = False
        print('   mismatch', r[0])
rec('E02', 'Usuarios: 40 con login, nombre, correo y empleado vinculado (1:1)', usr_ok and len(PAD['usrs']) == 40)

rec('E03', 'Jerarquía: solo EMP-001 sin responsable',
    env['hr.employee'].search_count([('jjsumi_code', 'like', 'EMP-'), ('parent_id', '=', False)]) == 1
    and not E('EMP-001').parent_id)

dep_mgr_ok = all((DEP(r[0]).manager_id.jjsumi_code or None) == r[4] for r in PAD['deps'])
are_mgr_ok = all((ARE(r[0]).manager_employee_id.jjsumi_code or None) == r[4] for r in PAD['areas'])
rec('E04', 'Responsables de departamento y área según padrón', dep_mgr_ok and are_mgr_ok)

# ------------------------------------------------------------- COHERENCIA
sede_match = all(U(r[2]).jjsumi_sede_id.jjsumi_code == E(r[4]).company_id.jjsumi_code for r in PAD['usrs'])
rec('C01', 'Sede del usuario = sede del empleado (40/40)', sede_match)

grp_ok = True
for r in PAD['usrs']:
    u = U(r[2])
    need = {env.ref(ROLE_XML[c]).id for c in r[5]} | {env.ref('base.group_user').id}
    if not need <= set(u.group_ids.ids):
        grp_ok = False
        print('   grupos faltan', r[2])
rec('C02', 'Grupos de rol y base.group_user aplicados a los 40 usuarios', grp_ok)

cargo_ok = True
for r in PAD['usrs']:
    job = E(r[4]).job_id.jjsumi_code
    allowed = CARGO_ROLES.get(job, set())
    for code in r[5]:
        if code not in allowed and (r[2], code) not in EXCEPCIONES:
            cargo_ok = False
            print('   rol no permitido', r[2], code, job)
rec('C03', 'Mapa cargo→rol respetado (+ excepciones documentadas)', cargo_ok)

cashier_ok = all(E(r[4]).job_id.jjsumi_code == 'CAR-026' for r in PAD['usrs'] if 'ROL-008' in r[5])
rec('C04', 'Rol Cajero solo con CAR-026', cashier_ok)

scope_ok = True
all_ids = set(env['res.company'].search([('jjsumi_code', 'like', 'SEDE-')]).ids + [main.id])
for r in PAD['usrs']:
    u = U(r[2])
    sede_id = SEDE(E(r[4]).company_id.jjsumi_code).id
    if set(r[5]) & {'ROL-001', 'ROL-002'}:
        exp = all_ids
    else:
        exp = {main.id, sede_id}
    if set(u.company_ids.ids) != exp:
        scope_ok = False
        print('   alcance', r[2])
rec('C05', 'Alcance de compañías: ROL-001/002 todas; resto matriz + sede', scope_ok)

rec('C06', 'Admin ve las 6 compañías', set(U('admin').company_ids.ids) >= all_ids if U('admin') else
    set(env.ref('base.user_admin').company_ids.ids) >= all_ids)

# ------------------------------------------------------- RESTRICCIONES (negativas)
e4 = E('EMP-004')
u4 = U('jorge.sanchez')
expect_raise('N01', 'Sede de usuario distinta a la del empleado → rechaza',
             lambda: u4.write({'jjsumi_sede_id': SEDE('SEDE-002').id}))
expect_raise('N02', 'Rol fuera del mapa de cargo (CAR-004 + ROL-001) → rechaza',
             lambda: u4.write({'jjsumi_role_codes': 'ROL-001'}))
expect_raise('N03', 'Rol Cajero a cargo distinto de CAR-026 → rechaza',
             lambda: u4.write({'jjsumi_role_codes': 'ROL-008'}))
expect_raise('N04', 'Responsable de área sin jefatura (CAR-002) → rechaza',
             lambda: ARE('ARE-001').write({'manager_employee_id': E('EMP-002').id}))
expect_raise('N05', 'Responsable de departamento con CAR-009 (no jefatura) → rechaza',
             lambda: DEP('DEP-004').write({'manager_id': E('EMP-012').id}))
expect_raise('N06', 'Empleado con código JJSUMI sin departamento → rechaza',
             lambda: e4.write({'department_id': False}))
expect_raise('N07', 'Código de compañía duplicado → rechaza',
             lambda: env['res.company'].create({'name': 'Dup', 'parent_id': main.id, 'jjsumi_code': 'SEDE-001'}))
expect_raise('N08', 'Cambiar sucursal del empleado con usuario desalineado → rechaza',
             lambda: e4.write({'company_id': SEDE('SEDE-002').id}))
expect_raise('N09', 'Departamento de área duplicado por código → rechaza',
             lambda: env['jjsumi.area'].create({'code': 'ARE-001', 'name': 'Dup', 'department_id': DEP('DEP-001').id}))

# ------------------------------------------------------- VISIBILIDAD (con usuario)
elena = U('elena.lopez')
visible_cos = in_rollback(lambda: set(env['res.company'].with_user(elena).search([]).ids))
rec('V01', 'Usuario SEDE-002 ve solo matriz y su sede', visible_cos == {main.id, SEDE('SEDE-002').id},
    'ids=%s' % sorted(visible_cos or []))
gerente = U('roberto.condori')
gen_cos = in_rollback(lambda: set(env['res.company'].with_user(gerente).search([]).ids))
rec('V02', 'Gerente General (ROL-002) ve las 6 compañías', gen_cos == all_ids)


def _emp_public_names(user):
    # Usuarios sin grupo RR. HH. solo leen hr.employee.public (Odoo nativo)
    return set(env['hr.employee.public'].with_user(user).search([]).mapped('name'))


allowed_names = set(env['hr.employee'].search([
    ('company_id', 'in', [main.id, SEDE('SEDE-002').id])]).mapped('name'))
other_names = set(env['hr.employee'].search([
    ('jjsumi_code', 'like', 'EMP-'), ('company_id', '!=', SEDE('SEDE-002').id)]).mapped('name'))
vis_elena = in_rollback(lambda: _emp_public_names(elena))
rec('V03', 'Empleados por sucursal: USR SEDE-002 no ve empleados de otras sedes',
    isinstance(vis_elena, set) and vis_elena <= allowed_names and not (vis_elena & other_names),
    'visibles=%s' % (len(vis_elena) if isinstance(vis_elena, set) else vis_elena))

# ------------------------------------------------------- ACL
area_user = U('elena.lopez')


def _write_area():
    ARE('ARE-002').with_user(area_user).write({'name': 'X'})


expect_raise('A01', 'Usuario funcional no puede modificar áreas', _write_area)


def _create_company():
    env['res.company'].with_user(area_user).create({'name': 'Hack'})


expect_raise('A02', 'Usuario funcional no puede crear compañías', _create_company)

# ------------------------------------------------------- APROBACIONES
req_user = U('elena.lopez')
apr_dir = env['jjsumi.approval.request']


def _approval_flow():
    r = apr_dir.with_user(req_user).create({
        'request_type': 'employee_org', 'description': 'Cambio de sede de prueba'})
    r.with_user(req_user).action_send()
    r.with_user(req_user).action_review()
    return r


def _check_seq():
    r = _approval_flow()
    return r.name.startswith('APR/')


rec('P01', 'Secuencia de aprobaciones APR/ asignada', bool(in_rollback(_check_seq)))


def _self_approve():
    r = _approval_flow()
    r.with_user(req_user).action_approve()


expect_raise('P02', 'Autoaprobación bloqueada', _self_approve)


def _other_approve():
    r = _approval_flow()
    r.with_user(gerente).action_approve()
    return r.state


rec('P03', 'Aprobación por otro usuario válida', in_rollback(_other_approve) == 'approved')

# ------------------------------------------------------- AUDITORÍA
def _audit_immutable():
    ev = env['jjsumi.audit.event'].sudo().create({
        'summary': 'prueba', 'operation': 'config', 'model_name': 'x', 'res_id': 0})
    ev.with_user(req_user).write({'summary': 'cambio'})


expect_raise('G01', 'Eventos de auditoría no editables por usuario funcional', _audit_immutable)


def _audit_unlink():
    ev = env['jjsumi.audit.event'].sudo().create({
        'summary': 'prueba', 'operation': 'config', 'model_name': 'x', 'res_id': 0})
    ev.with_user(req_user).unlink()


expect_raise('G02', 'Eventos de auditoría no eliminables por usuario funcional', _audit_unlink)

# ------------------------------------------------------- MENÚS
tops = env['ir.ui.menu'].search([('parent_id', '=', False)]).mapped('name')
rec('M01', 'Sin raíces duplicadas (Auditoría/Gobierno/JJSUMI sueltas)',
    'Auditoría' not in tops and 'Gobierno' not in tops and 'JJSUMI' not in tops,
    'raíces=%s' % sorted(tops))
rec('M02', 'Raíces Inicio, CORE y JJSumi presentes', {'Inicio', 'CORE', 'JJSumi'} <= set(tops))
core = env.ref('jjsumi_core.menu_jjsumi_core_root')
rec('M03', 'Menú CORE con 6 secciones',
    sorted(core.child_id.mapped('name')) == sorted(['Organización', 'Personal', 'Accesos', 'Gobierno', 'Auditoría', 'Parámetros']),
    str(core.child_id.mapped('name')))

# ------------------------------------------------------- SEGURIDAD DE DATOS
rec('X01', 'Ningún usuario del padrón tiene contraseña almacenada',
    all(not U(r[2]).password for r in PAD['usrs']))
legacy_users = env['res.users'].search_count([('login', 'not in', [r[2] for r in PAD['usrs']])])  # solo activos
legacy_emps = env['hr.employee'].search_count([('jjsumi_code', '=', False)])
rec('X02', 'Datos heredados intactos (21 usuarios, 21 empleados sin código)',
    legacy_users == 21 and legacy_emps == 21, 'usuarios=%d empleados=%d' % (legacy_users, legacy_emps))
rec('X03', 'Matriz JJSumi sin cambios de identidad',
    main.name == 'JJSumi' and main.currency_id.name == 'PEN' and not main.parent_id)

# ------------------------------------------------------- IDEMPOTENCIA
def _rerun():
    before = (env['res.company'].search_count([]), env['hr.department'].search_count([]),
              env['hr.job'].search_count([]), env['jjsumi.area'].search_count([]),
              env['hr.employee'].search_count([]), env['res.users'].search_count([]))
    env['jjsumi.seed'].load_fase1()
    after = (env['res.company'].search_count([]), env['hr.department'].search_count([]),
             env['hr.job'].search_count([]), env['jjsumi.area'].search_count([]),
             env['hr.employee'].search_count([]), env['res.users'].search_count([]))
    return before == after, before


ok_idem, counts = in_rollback(_rerun) or (False, None)
rec('I01', 'Segunda ejecución de la carga no duplica registros', ok_idem, 'conteos=%s' % (counts,))

passed = sum(1 for r in RESULTS if r[2])
print('RESUMEN: %d/%d pruebas OK' % (passed, len(RESULTS)))
