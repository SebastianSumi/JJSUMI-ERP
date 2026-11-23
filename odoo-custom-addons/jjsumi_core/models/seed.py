# -*- coding: utf-8 -*-
"""Carga idempotente de la Fase 01 (padrón JJSUMI) desde data/padron.json.

Orden: sucursales -> departamentos -> cargos -> áreas -> empleados ->
usuarios -> vínculo empleado/usuario -> validación (reescritura de sede y
roles) -> grupos -> jerarquía (parent_id) -> responsables de departamento y
de área. Cada paso busca por clave natural antes de crear, por lo que puede
ejecutarse varias veces sin duplicar registros.
"""
import json
import logging
import os

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)

ALL_BRANCH_ROLES = {"ROL-001", "ROL-002"}  # Alcance: todas las sucursales


class JjsumiSeed(models.AbstractModel):
    _name = "jjsumi.seed"
    _description = "Carga idempotente Fase 1 (padrón JJSUMI)"

    @api.model
    def _jjsumi_read_padron(self):
        module_path = get_module_path("jjsumi_core")
        path = os.path.join(module_path, "data", "padron.json") if module_path else None
        if not path or not os.path.isfile(path):
            raise UserError(_("No se encontró data/padron.json en jjsumi_core."))
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    @api.model
    def load_fase1(self):
        pad = self._jjsumi_read_padron()
        env = self.env
        main = env.ref("base.main_company")
        country_pe = env.ref("base.pe")
        Company = env["res.company"].sudo()
        Dept = env["hr.department"].sudo()
        Job = env["hr.job"].sudo()
        Area = env["jjsumi.area"].sudo()
        Emp = env["hr.employee"].sudo()
        User = env["res.users"].sudo()

        # 1. Sucursales (compañías hijas de la matriz)
        sede_ids = {}
        for code, name, city, _province, _region, zip_, street, phone, email in pad["sedes"]:
            vals = {
                "name": name,
                "parent_id": main.id,
                "street": street,
                "zip": zip_,
                "city": city,
                "country_id": country_pe.id,
                "phone": phone,
                "email": email,
                "jjsumi_code": code,
            }
            rec = Company.search([("jjsumi_code", "=", code)], limit=1)
            if rec:
                # Odoo prohíbe reescribir parent_id de una compañía existente
                rec.write({k: v for k, v in vals.items() if k != "parent_id"})
            else:
                rec = Company.create(vals)
            sede_ids[code] = rec.id
        sedes = Company.browse(list(sede_ids.values()))
        all_company_ids = [main.id] + sedes.ids

        # 2. Departamentos (sin responsable todavía)
        dep_ids = {}
        for code, name, parent, sede, _manager in pad["deps"]:
            vals = {"name": name, "jjsumi_code": code, "jjsumi_sede": sede}
            if parent:
                vals["parent_id"] = dep_ids[parent]
            rec = Dept.search([("jjsumi_code", "=", code)], limit=1)
            if rec:
                rec.write(vals)
            else:
                rec = Dept.create(vals)
            dep_ids[code] = rec.id

        # 3. Cargos
        job_ids = {}
        for code, name, dep in pad["jobs"]:
            vals = {"name": name, "jjsumi_code": code, "department_id": dep_ids[dep]}
            rec = Job.search([("jjsumi_code", "=", code)], limit=1)
            if rec:
                rec.write(vals)
            else:
                rec = Job.create(vals)
            job_ids[code] = rec.id

        # 4. Áreas (sin responsable todavía)
        area_ids = {}
        for code, name, dep, scope, _manager in pad["areas"]:
            vals = {"code": code, "name": name, "department_id": dep_ids[dep], "scope": scope}
            rec = Area.search([("code", "=", code)], limit=1)
            if rec:
                rec.write(vals)
            else:
                rec = Area.create(vals)
            area_ids[code] = rec.id

        # 5. Empleados (sin usuario ni jerarquía; se completan después)
        emp_ids = {}
        emp_sede = {}
        for code, name, dep, area, job, sede, _parent, _usr, email, phone in pad["emps"]:
            emp_sede[code] = sede
            vals = {
                "name": name,
                "jjsumi_code": code,
                "department_id": dep_ids[dep],
                "jjsumi_area_id": area_ids[area],
                "job_id": job_ids[job],
                "company_id": sede_ids[sede],
                "work_email": email,
                "mobile_phone": phone,
            }
            rec = Emp.search([("jjsumi_code", "=", code)], limit=1)
            if rec:
                rec.write(vals)
            else:
                rec = Emp.create(vals)
            emp_ids[code] = rec.id

        # 6. Usuarios. Alcance: ROL-001/002 ven todas las sucursales; el resto,
        #    matriz + su sede. Compañía predeterminada: matriz (padrón).
        usr_ids = {}
        usr_roles = {}
        for usr_code, name, login, email, emp_code, roles, phone in pad["usrs"]:
            usr_roles[login] = (usr_code, emp_code, roles)
            if set(roles) & ALL_BRANCH_ROLES:
                company_ids = all_company_ids
            else:
                company_ids = [main.id, sede_ids[emp_sede[emp_code]]]
            vals = {
                "name": name,
                "login": login,
                "email": email,
                "phone": phone,
                "company_id": main.id,
                "company_ids": [(6, 0, company_ids)],
                "jjsumi_sede_id": sede_ids[emp_sede[emp_code]],
                "jjsumi_role_codes": ",".join(roles),
                "tz": "America/Lima",
                "lang": "es_PE",
            }
            rec = User.search([("login", "=", login)], limit=1)
            if rec:
                rec.write(vals)
            else:
                rec = User.create(vals)
            usr_ids[login] = rec.id

        # 7. Vínculo empleado <-> usuario
        for usr_code, name, login, email, emp_code, roles, phone in pad["usrs"]:
            Emp.browse(emp_ids[emp_code]).write({"user_id": usr_ids[login]})

        # 8. Validación: reescribir sede y roles ahora que el empleado existe
        #    (dispara las restricciones de sede y de rol por cargo)
        for login, uid in usr_ids.items():
            user = User.browse(uid)
            user.write({
                "jjsumi_sede_id": user.jjsumi_sede_id.id,
                "jjsumi_role_codes": user.jjsumi_role_codes,
            })
            # 9. Grupos de seguridad a partir de los códigos de rol
            user._jjsumi_apply_role_groups()

        # 10. Jerarquía de empleados (responsable inmediato)
        for code, name, dep, area, job, sede, parent, *_rest in pad["emps"]:
            if parent:
                Emp.browse(emp_ids[code]).write({"parent_id": emp_ids[parent]})

        # 11. Responsables de departamento (después de la jerarquía)
        for code, name, parent, sede, manager in pad["deps"]:
            if manager:
                Dept.browse(dep_ids[code]).write({"manager_id": emp_ids[manager]})

        # 12. Responsables de área
        for code, name, dep, scope, manager in pad["areas"]:
            if manager:
                Area.browse(area_ids[code]).write({"manager_employee_id": emp_ids[manager]})

        # 13. El administrador ve todas las sucursales
        admin = env.ref("base.user_admin", raise_if_not_found=False)
        if admin:
            admin.sudo().write({"company_ids": [(6, 0, all_company_ids)]})

        counts = {
            "sedes": len(sede_ids), "deps": len(dep_ids), "jobs": len(job_ids),
            "areas": len(area_ids), "emps": len(emp_ids), "usrs": len(usr_ids),
        }
        _logger.info("JJSUMI Fase 1 cargada: %s", counts)
        return counts
