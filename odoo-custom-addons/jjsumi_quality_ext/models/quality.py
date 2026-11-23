# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class JjsumiQualityPoint(models.Model):
    _name = 'jjsumi.quality.point'
    _description = 'Punto de control de calidad JJSumi'
    _order = 'code'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    test_type = fields.Selection([('measure', 'Medida'), ('pass_fail', 'Pasa/Falla')], required=True, default='measure')
    moment = fields.Selection([
        ('reception', 'Recepción'), ('production', 'Producción'), ('finished', 'Producto terminado'),
        ('dispatch', 'Despacho'), ('returns', 'Devoluciones'), ('maintenance', 'Mantenimiento'),
    ], required=True)
    norm_min = fields.Float(string='Norma mínima')
    norm_max = fields.Float(string='Norma máxima')
    unit = fields.Char()
    product_tmpl_ids = fields.Many2many('product.template', string='Productos')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Centro de trabajo')
    active = fields.Boolean(default=True)
    _code_uniq = models.Constraint('unique(code)', 'El código del punto de control debe ser único.')


class JjsumiQualityCheck(models.Model):
    _name = 'jjsumi.quality.check'
    _description = 'Inspección de calidad JJSumi'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(compute='_compute_name', store=True)
    point_id = fields.Many2one('jjsumi.quality.point', required=True, tracking=True)
    test_type = fields.Selection(related='point_id.test_type')
    production_id = fields.Many2one('mrp.production', string='Orden de fabricación')
    picking_id = fields.Many2one('stock.picking', string='Albarán')
    lot_id = fields.Many2one('stock.lot', string='Lote')
    measure = fields.Float(string='Medición')
    result = fields.Selection([('none', 'Pendiente'), ('pass', 'Aprobado'), ('fail', 'Rechazado')],
                              default='none', tracking=True)
    user_id = fields.Many2one('res.users', default=lambda s: s.env.user, string='Inspector')
    check_date = fields.Datetime(default=fields.Datetime.now)
    observations = fields.Text(string='Observaciones')
    cuarentena = fields.Boolean(compute='_compute_cuarentena', store=True)

    @api.depends('point_id', 'production_id', 'picking_id')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s %s' % (rec.point_id.code or '', rec.production_id.name or rec.picking_id.name or '')

    @api.depends('result')
    def _compute_cuarentena(self):
        for rec in self:
            rec.cuarentena = rec.result == 'fail'

    @api.constrains('point_id', 'measure', 'result', 'lot_id', 'production_id', 'picking_id')
    def _check_rules(self):
        for rec in self:
            if rec.point_id.test_type == 'measure' and rec.result != 'none' and rec.measure is not None:
                p = rec.point_id
                ok = (p.norm_min is None or rec.measure >= p.norm_min) and (not p.norm_max or rec.measure <= p.norm_max)
                if (rec.result == 'pass') != ok:
                    raise ValidationError(_('El resultado no coincide con la norma del punto %s.', p.code))
            if (rec.production_id or rec.picking_id) and rec.result != 'none' and not rec.lot_id:
                raise ValidationError(_('Todo control asociado a producción o recepción requiere lote.'))

    @api.onchange('measure')
    def _onchange_measure(self):
        for rec in self:
            p = rec.point_id
            if p.test_type == 'measure' and rec.measure:
                ok = (rec.measure >= p.norm_min) and (not p.norm_max or rec.measure <= p.norm_max)
                rec.result = 'pass' if ok else 'fail'

    @staticmethod
    def _resultado_medida(point, measure):
        ok = (measure >= point.norm_min) and (not point.norm_max or measure <= point.norm_max)
        return 'pass' if ok else 'fail'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            point = self.env['jjsumi.quality.point'].browse(vals.get('point_id'))
            if point and point.test_type == 'measure' and vals.get('measure') is not None and vals.get('result', 'none') == 'none':
                vals['result'] = self._resultado_medida(point, vals['measure'])
        return super().create(vals_list)

    def write(self, vals):
        if 'measure' in vals and 'result' not in vals:
            for rec in self.filtered(lambda r: r.point_id.test_type == 'measure'):
                vals_r = dict(vals, result=self._resultado_medida(rec.point_id, vals['measure']))
                super(JjsumiQualityCheck, rec).write(vals_r)
            rest = self.filtered(lambda r: r.point_id.test_type != 'measure')
            if rest:
                return super(JjsumiQualityCheck, rest).write(vals)
            return True
        if 'result' in vals or 'measure' in vals:
            if not self.env.user.has_group('jjsumi_security.group_jjsumi_quality_manager') \
                    and not self.env.user.has_group('jjsumi_security.group_jjsumi_admin'):
                if any(r.result != 'none' for r in self):
                    raise UserError(_('Solo el responsable de calidad puede modificar un resultado ya registrado.'))
        return super().write(vals)


class MrpProductionCalidad(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        bloqueos = self.env['jjsumi.quality.check'].search([('production_id', 'in', self.ids), ('result', '=', 'fail')])
        if bloqueos:
            raise UserError(_('No se puede terminar la orden: hay controles rechazados (%s).', ', '.join(bloqueos.mapped('point_id.code'))))
        return super().button_mark_done()


class StockPickingCalidad(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        bloqueos = self.env['jjsumi.quality.check'].search([('picking_id', 'in', self.ids), ('result', '=', 'fail')])
        if bloqueos:
            raise UserError(_('Recepción bloqueada por calidad (%s). Dejar en cuarentena.', ', '.join(bloqueos.mapped('point_id.code'))))
        return super().button_validate()
