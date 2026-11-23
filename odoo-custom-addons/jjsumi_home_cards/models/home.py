import base64
import hashlib
import hmac
import json
import time

from odoo import api, models, _
from odoo.exceptions import UserError

# Clave de tarjeta -> xmlid del menú nativo al que se redirige.
# La tarjeta solo navega: resuelve la primera acción del árbol del menú
# (mismo criterio que el webclient al abrir una aplicación).
CARD_MENUS = {
    "core": "base.menu_users",
    "crm": "crm.crm_menu_root",
    "sales": "sale.sale_menu_root",
    "inventory": "stock.menu_stock_root",
    "purchases": "purchase.menu_purchase_root",
    "manufacturing": "mrp.menu_mrp_root",
    "quality": "jjsumi_menus.menu_jjsumi_inv_controles",
    "maintenance": "maintenance.menu_maintenance_title",
    "pos": "point_of_sale.menu_point_root",
    "finance": "account.menu_finance",
    "hr": "hr.menu_hr_root",
    "reports": None,  # se resuelve en tiempo de ejecución (menú Reporting sin xmlid).
    "marketing": "mass_mailing.mass_mailing_menu_root",
}

_REPORT_NAMES = ("reporting", "reportes", "informes")


class JjsumiHome(models.AbstractModel):
    _name = "jjsumi.home"
    _description = "Servicios de navegación del inicio JJSUMI"

    @api.model
    def _first_action(self, menu):
        """Primera acción descendente del menú, ordenada por sequence."""
        if menu.action:
            return menu.action
        children = menu.child_id._filter_visible_menus().sorted("sequence")
        for child in children:
            action = self._first_action(child)
            if action:
                return action
        return False

    @api.model
    def _find_menu(self, menu, names):
        children = menu.child_id._filter_visible_menus().sorted("sequence")
        for child in children:
            if (child.name or "").lower() in names:
                return child
            found = self._find_menu(child, names)
            if found:
                return found
        return False

    @api.model
    def _menu_for_key(self, key):
        if key not in CARD_MENUS:
            raise UserError(_("La tarjeta solicitada no existe."))
        xmlid = CARD_MENUS[key]
        if xmlid:
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            if menu:
                return menu
        if key == "reports":
            sale_root = self.env.ref("sale.sale_menu_root", raise_if_not_found=False)
            if sale_root:
                menu = self._find_menu(sale_root, _REPORT_NAMES)
                if menu:
                    return menu
        raise UserError(_(
            "No se encontró el menú nativo asociado a esta tarjeta "
            "(¿falta instalar el módulo?)."
        ))

    @api.model
    def get_card_action(self, key):
        return self.get_card_target(key)["action"]

    @api.model
    def get_card_target(self, key):
        menu = self._menu_for_key(key)
        action = self._first_action(menu)
        if not action:
            raise UserError(_(
                "El menú nativo de esta tarjeta no tiene ninguna acción asociada."
            ))
        xid = action.get_external_id().get(action.id)
        if not xid:
            raise UserError(_(
                "La acción del menú nativo no está registrada como XML ID."
            ))
        return {
            "action": self.env["ir.actions.actions"]._for_xml_id(xid),
            "menu_id": menu.id,
        }

    @api.model
    def get_bsc_sso_url(self, host="127.0.0.1"):
        """Genera un JWT HS256 temporal para iniciar sesión SSO en el BSC."""
        user = self.env.user
        email = (user.email or "").strip() or (
            user.login if "@" in (user.login or "") else f"{user.login}@jjsumi.pe"
        )
        if user.has_group("base.group_system"):
            rol = "ADMIN"
        elif user.has_group("jjsumi_security.group_jjsumi_general_manager"):
            rol = "GERENTE"
        else:
            rol = "ANALISTA"

        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sso": True,
            "email": email,
            "nombre": user.name or user.login,
            "rol": rol,
            "iat": now,
            "exp": now + 300,
        }
        b64 = lambda d: base64.urlsafe_b64encode(
            json.dumps(d, separators=(",", ":")).encode("utf-8")
        ).rstrip(b"=").decode("ascii")
        signing_input = f"{b64(header)}.{b64(payload)}"
        sig = base64.urlsafe_b64encode(
            hmac.new(
                b"cambia-esta-clave-en-produccion",
                signing_input.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).rstrip(b"=").decode("ascii")
        token = f"{signing_input}.{sig}"
        clean_host = (host or "127.0.0.1").split(":")[0]
        comp_map = {
            1: "jjsumi",
            7: "jjsumi-juliaca",
            8: "jjsumi-puno",
            9: "jjsumi-arequipa",
            10: "jjsumi-cusco",
            11: "jjsumi-tacna",
        }
        empresa = comp_map.get(self.env.company.id, "jjsumi")
        return f"http://{clean_host}/bsc/?sso={token}&empresa={empresa}"

    @api.model
    def get_dashboard_summary(self):
        """Devuelve métricas rápidas en vivo por tarjeta para el usuario y compañía activos."""
        def safe_count(model, domain=None):
            if model not in self.env:
                return 0
            try:
                return self.env[model].search_count(domain or [])
            except Exception:
                return 0

        counts = {
            "core": safe_count("res.users", [("share", "=", False), ("active", "=", True)]),
            "crm": safe_count("crm.lead", [("active", "=", True)]),
            "sales": safe_count("sale.order", [("state", "=", "sale")]),
            "inventory": safe_count("stock.picking", [("state", "in", ("assigned", "confirmed"))]),
            "purchases": safe_count("purchase.order", [("state", "in", ("purchase", "done"))]),
            "manufacturing": safe_count("mrp.production", [("state", "in", ("confirmed", "progress", "to_close"))]),
            "quality": safe_count("jjsumi.quality.check"),
            "maintenance": safe_count("maintenance.request"),
            "pos": safe_count("pos.order"),
            "finance": safe_count("account.move", [("move_type", "=", "out_invoice"), ("state", "=", "posted")]),
            "hr": safe_count("hr.employee", [("active", "=", True)]),
            "reports": safe_count("sale.order"),
            "marketing": safe_count("mailing.contact"),
        }
        return {
            "user_name": self.env.user.name,
            "company_name": self.env.company.name,
            "counts": counts,
            "pulse": {
                "sales": counts["sales"],
                "crm": counts["crm"],
                "pos": counts["pos"],
                "hr": counts["hr"],
            },
        }
