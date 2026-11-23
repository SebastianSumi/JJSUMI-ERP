# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetLogViaje(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    x_jjsumi_odo_salida = fields.Float(string='Odómetro de salida (km)')
    x_jjsumi_odo_llegada = fields.Float(string='Odómetro de llegada (km)')
    x_jjsumi_km_recorridos = fields.Float(string='Km recorridos', compute='_compute_km', store=True)
    x_jjsumi_destino = fields.Char(string='Destino del viaje')

    @api.depends('x_jjsumi_odo_salida', 'x_jjsumi_odo_llegada')
    def _compute_km(self):
        for rec in self:
            rec.x_jjsumi_km_recorridos = max(rec.x_jjsumi_odo_llegada - rec.x_jjsumi_odo_salida, 0.0) \
                if rec.x_jjsumi_odo_llegada else 0.0

    @api.constrains('x_jjsumi_odo_salida', 'x_jjsumi_odo_llegada')
    def _check_odometro(self):
        for rec in self:
            if rec.x_jjsumi_odo_llegada and rec.x_jjsumi_odo_llegada < rec.x_jjsumi_odo_salida:
                raise ValidationError(_('El odómetro de llegada no puede ser menor al de salida.'))


class FleetViajeDisponibilidad(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('x_jjsumi_destino') and vals.get('vehicle_id'):
                veh = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
                estado = veh.state_id.name if veh.state_id else ''
                if estado in ('En ruta', 'En mantenimiento'):
                    raise ValidationError(_('El vehículo %s no está disponible (estado: %s).', veh.license_plate, estado))
        recs = super().create(vals_list)
        for rec in recs.filtered('x_jjsumi_destino'):
            rec._jjsumi_set_state('En ruta' if not rec.x_jjsumi_odo_llegada else 'Disponible')
        return recs

    def write(self, vals):
        res = super().write(vals)
        if 'x_jjsumi_odo_llegada' in vals:
            for rec in self.filtered('x_jjsumi_destino'):
                if rec.x_jjsumi_odo_llegada:
                    rec._jjsumi_set_state('Disponible')
        return res

    def _jjsumi_set_state(self, nombre):
        st = self.env['fleet.vehicle.state'].search([('name', '=', nombre)], limit=1)
        if st and self.vehicle_id:
            self.vehicle_id.state_id = st.id


class FleetTipoViaje(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'service_type_id' in fields_list and not res.get('service_type_id'):
            tipo = self.env['fleet.service.type'].search([('name', '=', 'Viaje de distribución')], limit=1)
            if not tipo:
                tipo = self.env['fleet.service.type'].create({'name': 'Viaje de distribución', 'category': 'service'})
            res['service_type_id'] = tipo.id
        return res
