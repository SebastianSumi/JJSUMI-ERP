# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class MaintenanceEquipmentContador(models.Model):
    _inherit = 'maintenance.equipment'

    x_jjsumi_codigo = fields.Char(string='Código JJSUMI')
    x_jjsumi_ubicacion = fields.Char(string='Ubicación en planta')
    x_jjsumi_horas = fields.Float(string='Horas de operación acumuladas')
    x_jjsumi_km = fields.Float(string='Kilómetros acumulados')
    x_jjsumi_frec_horas = fields.Float(string='Preventivo cada (horas)')
    x_jjsumi_frec_km = fields.Float(string='Preventivo cada (km)')
    x_jjsumi_ult_horas = fields.Float(string='Horas en último preventivo')
    x_jjsumi_ult_km = fields.Float(string='Km en último preventivo')

    @api.model
    def _cron_contador_preventivo(self):
        """Crea maintenance.request preventivo cuando las horas o km superan la frecuencia desde el último preventivo."""
        Req = self.env['maintenance.request']
        creadas = self.env['maintenance.request']
        for eq in self.search([]):
            vence_h = eq.x_jjsumi_frec_horas > 0 and (eq.x_jjsumi_horas - eq.x_jjsumi_ult_horas) >= eq.x_jjsumi_frec_horas
            vence_k = eq.x_jjsumi_frec_km > 0 and (eq.x_jjsumi_km - eq.x_jjsumi_ult_km) >= eq.x_jjsumi_frec_km
            if not (vence_h or vence_k):
                continue
            abierta = Req.search_count([
                ('equipment_id', '=', eq.id), ('maintenance_type', '=', 'preventive'),
                ('stage_id.done', '=', False)])
            if abierta:
                continue
            motivo = _('Horas') if vence_h else _('Kilómetros')
            creadas |= Req.create({
                'name': _('Preventivo por %s: %s', motivo.lower(), eq.name),
                'equipment_id': eq.id,
                'maintenance_type': 'preventive',
                'maintenance_team_id': eq.maintenance_team_id.id,
                'user_id': eq.technician_user_id.id if eq.technician_user_id else False,
                'schedule_date': fields.Datetime.now(),
            })
        return creadas


class MaintenanceRequestContador(models.Model):
    _inherit = 'maintenance.request'

    x_jjsumi_costo = fields.Float(string='Costo de mantenimiento')

    def write(self, vals):
        res = super().write(vals)
        if 'stage_id' in vals:
            for req in self.filtered(lambda r: r.maintenance_type == 'preventive' and r.stage_id.done and r.equipment_id):
                eq = req.equipment_id
                eq.write({'x_jjsumi_ult_horas': eq.x_jjsumi_horas, 'x_jjsumi_ult_km': eq.x_jjsumi_km})
        return res
