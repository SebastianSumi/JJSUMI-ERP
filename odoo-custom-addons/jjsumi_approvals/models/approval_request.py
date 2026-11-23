# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class JjsumiApprovalRequest(models.Model):
    _name = "jjsumi.approval.request"
    _description = "Solicitud de aprobación CORE"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Número", readonly=True, copy=False, default=lambda self: _("Nuevo"))
    request_type = fields.Selection([
        ("user_new", "Alta de usuario"),
        ("user_role", "Cambio de rol"),
        ("user_deactivate", "Baja de usuario"),
        ("employee_new", "Alta de empleado"),
        ("employee_org", "Cambio departamento/sucursal/cargo"),
        ("employee_leave", "Baja de empleado"),
        ("access_exception", "Excepción de acceso"),
    ], string="Tipo", required=True, tracking=True)
    state = fields.Selection([
        ("draft", "Borrador"),
        ("sent", "Enviada"),
        ("review", "En revisión"),
        ("approved", "Aprobada"),
        ("rejected", "Rechazada"),
        ("done", "Ejecutada"),
        ("cancelled", "Cancelada"),
    ], string="Estado", default="draft", tracking=True, copy=False)
    requester_id = fields.Many2one("res.users", string="Solicitante", default=lambda self: self.env.user, required=True)
    approver_id = fields.Many2one("res.users", string="Aprobador")
    target_user_id = fields.Many2one("res.users", string="Usuario afectado")
    target_employee_id = fields.Many2one("hr.employee", string="Empleado afectado")
    description = fields.Text(string="Detalle", required=True)
    decision_notes = fields.Text(string="Notas de decisión")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("jjsumi.approval.request") or "/"
        return super().create(vals_list)

    def action_send(self):
        self.write({"state": "sent"})

    def action_review(self):
        self.write({"state": "review"})

    def action_approve(self):
        self._check_no_self_approval()
        self._log_audit("approve", "Solicitud aprobada")
        self.write({"state": "approved"})

    def action_reject(self):
        self._check_no_self_approval()
        self._log_audit("reject", "Solicitud rechazada")
        self.write({"state": "rejected"})

    def action_done(self):
        if self.state != "approved":
            raise ValidationError(_("Solo una solicitud aprobada puede ejecutarse."))
        self._log_audit("write", "Solicitud ejecutada")
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def _check_no_self_approval(self):
        for rec in self:
            if rec.requester_id == self.env.user:
                raise ValidationError(_("Un solicitante no puede aprobar su propia solicitud."))

    def _log_audit(self, op, summary):
        self.env["jjsumi.audit.event"].sudo().create({
            "summary": summary,
            "operation": op,
            "model_name": self._name,
            "res_id": self.id,
            "res_display": self.name,
            "notes": (self.decision_notes or "") + "\n" + (self.description or ""),
        })
