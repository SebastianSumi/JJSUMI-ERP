# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class JjsumiAuditEvent(models.Model):
    _name = "jjsumi.audit.event"
    _description = "Evento de auditoría JJSUMI"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    _rec_name = "summary"

    name = fields.Char(string="Referencia", readonly=True, copy=False, default=lambda self: _("Nuevo"))
    summary = fields.Char(string="Resumen", required=True, tracking=True)
    operation = fields.Selection([
        ("create", "Alta"),
        ("write", "Modificación"),
        ("unlink", "Baja / archivado"),
        ("approve", "Aprobación"),
        ("reject", "Rechazo"),
        ("login", "Acceso administrativo"),
        ("config", "Cambio de configuración"),
    ], string="Operación", required=True, tracking=True)
    model_name = fields.Char(string="Modelo", tracking=True)
    res_id = fields.Integer(string="ID registro", tracking=True)
    res_display = fields.Char(string="Registro", tracking=True)
    actor_id = fields.Many2one("res.users", string="Actor", default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one("res.company", string="Compañía", default=lambda self: self.env.company)
    notes = fields.Text(string="Motivo / detalle")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                seq = self.env["ir.sequence"].next_by_code("jjsumi.audit.event") or "/"
                vals["name"] = seq
        return super().create(vals_list)

    def unlink(self):
        # Registros históricos no se borran físicamente por usuarios funcionales
        if not self.env.is_system():
            raise UserError(_("Los eventos de auditoría no pueden eliminarse."))
        return super().unlink()

    def write(self, vals):
        if not self.env.is_system() and set(vals) - {"message_follower_ids", "message_ids"}:
            # permitir solo tracking de mail; bloquear edición funcional
            blocked = set(vals) - {"message_follower_ids", "message_ids", "activity_schedule"}
            if blocked:
                raise UserError(_("Los eventos de auditoría no pueden editarse."))
        return super().write(vals)
