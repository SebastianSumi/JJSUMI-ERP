# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# Precio base = bolsa de 23 kg (S/ 6). 26 kg = +1 (S/ 7). 30 kg = +2 (S/ 8).
EXTRAS_PRECIO = {
    'jjsumi_base.attribute_value_23kg': 0.0,
    'jjsumi_base.attribute_value_26kg': 1.0,
    'jjsumi_base.attribute_value_30kg': 2.0,
}
PRECIO_BASE = 6.0


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _jjsumi_setup_precios(self):
        """Carga única de precios de venta del yeso (idempotente)."""
        icp = self.env['ir.config_parameter'].sudo()
        if icp.get_param('jjsumi.precios_cargados'):
            return True
        tmpl = self.env.ref('jjsumi_base.product_template_yeso', raise_if_not_found=False)
        if not tmpl:
            return True
        try:
            with self.env.cr.savepoint():
                tmpl.list_price = PRECIO_BASE
                valores = tmpl.attribute_line_ids.product_template_value_ids
                for xmlid, extra in EXTRAS_PRECIO.items():
                    attr_value = self.env.ref(xmlid)
                    valores.filtered(
                        lambda v: v.product_attribute_value_id == attr_value
                    ).write({'price_extra': extra})
                icp.set_param('jjsumi.precios_cargados', '1')
        except Exception:  # noqa: BLE001
            _logger.exception('JJSumi: no se pudieron cargar los precios del yeso')
        return True
