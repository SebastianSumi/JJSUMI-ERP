# -*- coding: utf-8 -*-
import logging

from odoo import api, models
from odoo.exceptions import UserError

from . import catalog_data as D

_logger = logging.getLogger(__name__)
MODULE = 'jjsumi_catalog_ext'


def _ruc_valido(idx):
    """RUC de 11 dígitos con dígito verificador (algoritmo SUNAT).
    Prefijo 2090 + correlativo de 6 dígitos. Proveedores con RUC válido."""
    base = '2090%06d' % idx
    weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(base, weights))
    dv = 11 - (total % 11)
    dv = 0 if dv == 10 else (1 if dv == 11 else dv)
    return base + str(dv)


class JJSumiCatalogLoader(models.AbstractModel):
    _name = 'jjsumi.catalog.loader'
    _description = 'Carga idempotente del catálogo JJSUMI Fase 2'

    @api.model
    def run(self):
        company = self.env.ref('base.main_company')
        env = self.with_company(company)
        uoms = env._load_uoms()
        cats = env._load_categories()
        env._load_attributes()
        env._load_tags()
        sale_tax, purchase_tax = env._get_taxes(company)
        env._load_pricelists(company)
        suppliers = env._load_suppliers(company)
        env._load_products(company, uoms, cats, sale_tax, purchase_tax, suppliers)
        env._load_variants()
        env._archive_legacy()
        _logger.info('JJSumi catálogo Fase 2: carga completada')
        return True

    # ---------- Identificadores estables por SKU ----------
    def _xmlid_name(self, sku):
        return 'tmpl_' + sku.replace('-', '_').lower()

    def _find_tmpl(self, sku):
        """Busca el template por XML ID (estable aunque tenga variantes) o por default_code."""
        Tmpl = self.env['product.template'].with_context(active_test=False)
        xid = self.env['ir.model.data'].search([
            ('module', '=', MODULE), ('name', '=', self._xmlid_name(sku)),
            ('model', '=', 'product.template')], limit=1)
        if xid:
            return Tmpl.browse(xid.res_id)
        return Tmpl.search([('default_code', '=', sku)], limit=1)

    def _ensure_xmlid(self, tmpl, sku):
        name = self._xmlid_name(sku)
        if not self.env['ir.model.data'].search([('module', '=', MODULE), ('name', '=', name)], limit=1):
            self.env['ir.model.data'].create({
                'module': MODULE, 'name': name, 'model': 'product.template', 'res_id': tmpl.id,
                'noupdate': True,
            })

    # ---------- UoM ----------
    def _load_uoms(self):
        kg = self.env.ref('uom.product_uom_kgm')
        unit = self.env.ref('uom.product_uom_unit')
        Uom = self.env['uom.uom'].with_context(active_test=False)
        result = {
            'KG': kg,
            'TON': self.env.ref('uom.product_uom_ton'),
            'U': unit,
        }
        for key, (name, base, factor) in D.UOM_CREATE.items():
            ref = kg if base == 'kg' else unit
            uom = Uom.search([('name', '=', name),
                              ('relative_uom_id', '=', ref.id)], limit=1)
            if not uom:
                uom = Uom.create({
                    'name': name,
                    'relative_uom_id': ref.id,
                    'relative_factor': factor,
                })
            result[key] = uom
        return result

    # ---------- Categorías ----------
    def _load_categories(self):
        Cat = self.env['product.category']
        routes = {
            'buy': self.env.ref('purchase_stock.route_warehouse0_buy').id,
            'mfg': self.env.ref('mrp.route_warehouse0_manufacture').id,
        }
        fifo = self.env.ref('stock.removal_fifo')
        result = {}
        for code, name, cost, rts, _lot, _storable in D.CATEGORIES:
            vals = {
                'name': name,
                'parent_id': False,
                'property_cost_method': cost,
                'property_valuation': 'periodic',
                'removal_strategy_id': fifo.id,
                'route_ids': [(6, 0, [routes[r] for r in rts])],
            }
            cat = Cat.search([('name', '=', name), ('parent_id', '=', False)], limit=1)
            if cat:
                cat.write(vals)
            else:
                cat = Cat.create(vals)
            result[code] = cat
        return result

    # ---------- Atributos y etiquetas ----------
    def _load_attributes(self):
        Attr = self.env['product.attribute']
        Val = self.env['product.attribute.value']
        for name, cv, dt, values in D.ATTRIBUTES:
            attr = Attr.search([('name', '=', name)], limit=1)
            if not attr:
                attr = Attr.create({'name': name, 'create_variant': cv, 'display_type': dt})
            elif attr.create_variant != cv and not attr.attribute_line_ids:
                # Solo se cambia si el atributo no está usado en ningún producto.
                attr.write({'create_variant': cv})
            for vname, seq in values:
                if not Val.search([('attribute_id', '=', attr.id), ('name', '=', vname)], limit=1):
                    Val.create({'attribute_id': attr.id, 'name': vname, 'sequence': seq})

    def _load_tags(self):
        Tag = self.env['product.tag']
        for name, color in D.TAGS:
            if not Tag.search([('name', '=', name)], limit=1):
                Tag.create({'name': name, 'color': color})

    # ---------- Impuestos (IGV 18% sin precio incluido) ----------
    def _get_taxes(self, company):
        Tax = self.env['account.tax']

        def pick(type_use):
            for tax in Tax.search([('company_id', '=', company.id),
                                   ('type_tax_use', '=', type_use),
                                   ('amount', '=', 18.0)], order='id'):
                if tax.price_include_override != 'tax_included':
                    return tax
            raise UserError('No se encontró IGV 18%% (%s) sin precio incluido.' % type_use)

        return pick('sale'), pick('purchase')

    # ---------- Listas de precios ----------
    def _load_pricelists(self, company):
        PL = self.env['product.pricelist']
        PLI = self.env['product.pricelist.item']
        pen = self.env.ref('base.PEN')
        for _code, name, disc, minq, _selectable in D.PRICELISTS:
            pl = PL.search([('name', '=', name)], limit=1)
            if not pl:
                # 'selectable' y 'discount_policy' no existen en product.pricelist de Odoo 19.
                pl = PL.create({
                    'name': name,
                    'currency_id': pen.id,
                    'company_id': company.id,
                })
            if disc and not PLI.search([('pricelist_id', '=', pl.id)], limit=1):
                PLI.create({
                    'pricelist_id': pl.id,
                    'applied_on': '3_global',
                    'compute_price': 'percentage',
                    'percent_price': disc,
                    'min_quantity': minq,
                })

    # ---------- Proveedores ----------
    def _load_suppliers(self, company):
        Partner = self.env['res.partner'].with_context(active_test=False)
        pe = self.env.ref('base.pe')
        ruc_type = self.env.ref('l10n_pe.it_RUC', raise_if_not_found=False)
        result = {}
        for idx, (name, city) in enumerate(D.SUPPLIERS, start=1):
            vat = _ruc_valido(idx)
            vals = {
                'name': name,
                'supplier_rank': 1,
                'country_id': pe.id,
                'city': city,
                'vat': vat,
                'company_id': company.id,
            }
            if ruc_type:
                vals['l10n_latam_identification_type_id'] = ruc_type.id
            partner = Partner.search([('vat', '=', vat)], limit=1)
            if partner:
                partner.write(vals)
            else:
                partner = Partner.create(vals)
            result[idx] = partner
        return result

    # ---------- Productos (templates) ----------
    def _load_products(self, company, uoms, cats, sale_tax, purchase_tax, suppliers):
        Sup = self.env['product.supplierinfo']
        pen = self.env.ref('base.PEN')
        cat_meta = {c[0]: (c[4], c[5]) for c in D.CATEGORIES}
        rot = {}
        for sku, name, uom_key, cost, price in D.PRODUCTS:
            code = D.PREFIX_CAT[sku.split('-')[0]]
            cat = cats[code]
            lot, storable = cat_meta[code]
            is_mat = code == 'CAT-MAT'
            uom = uoms[uom_key]
            vals = {
                'name': name,
                'categ_id': cat.id,
                'type': 'consu',
                'is_storable': storable,
                'tracking': 'lot' if lot else 'none',
                'uom_id': uom.id,
                'list_price': price,
                'sale_ok': not is_mat,
                'purchase_ok': True,
                'taxes_id': [(6, 0, [] if is_mat else [sale_tax.id])],
                'supplier_taxes_id': [(6, 0, [purchase_tax.id])],
                'company_id': company.id,
                'active': True,
            }
            tmpl = self._find_tmpl(sku)
            if tmpl and tmpl.attribute_line_ids:
                # Ya tiene variantes: el SKU vive en la variante, no en el template.
                pass
            else:
                vals.update({'default_code': sku, 'standard_price': cost})
            if tmpl:
                tmpl.write(vals)
            else:
                tmpl = self.env['product.template'].create(vals)
            self._ensure_xmlid(tmpl, sku)

            if not Sup.search([('product_tmpl_id', '=', tmpl.id)], limit=1):
                options = D.SUPPLIER_MAP[code]
                n = rot.get(code, 0)
                rot[code] = n + 1
                partner = suppliers[options[n % len(options)]]
                Sup.create({
                    'partner_id': partner.id,
                    'product_tmpl_id': tmpl.id,
                    'price': cost,
                    'min_qty': 1,
                    'delay': 7,
                    'currency_id': pen.id,
                    'company_id': company.id,
                })

    # ---------- Variantes explícitas (D10 revisado) ----------
    def _load_variants(self):
        Attr = self.env['product.attribute']
        AttrVal = self.env['product.attribute.value']
        for tmpl_sku, attr_name, values in D.VARIANT_LINES:
            tmpl = self._find_tmpl(tmpl_sku)
            attr = Attr.search([('name', '=', attr_name)], limit=1)
            vals = AttrVal.search([('attribute_id', '=', attr.id), ('name', 'in', values)])
            if len(vals) != len(values):
                raise UserError('Faltan valores de %s para %s' % (attr_name, tmpl_sku))
            line = tmpl.attribute_line_ids.filtered(lambda l: l.attribute_id == attr)[:1]
            if not line:
                tmpl.write({'attribute_line_ids': [(0, 0, {
                    'attribute_id': attr.id,
                    'value_ids': [(6, 0, vals.ids)],
                })]})
            else:
                missing = vals - line.value_ids
                if missing:
                    line.write({'value_ids': [(4, v.id) for v in missing]})

        attr_by_tmpl = {t: a for t, a, _ in D.VARIANT_LINES}
        for variant_sku, tmpl_sku, value_name, price, cost in D.VARIANT_ITEMS:
            tmpl = self._find_tmpl(tmpl_sku)
            value = AttrVal.search([('name', '=', value_name),
                                    ('attribute_id.name', '=', attr_by_tmpl[tmpl_sku])],
                                   limit=1)
            ptav = tmpl.attribute_line_ids.product_template_value_ids.filtered(
                lambda v: v.product_attribute_value_id == value)
            if not ptav:
                raise UserError('Sin valor %s en %s' % (value_name, tmpl_sku))
            ptav.write({'price_extra': price - tmpl.list_price})
            variant = tmpl.product_variant_ids.filtered(
                lambda p: value in p.product_template_attribute_value_ids.product_attribute_value_id)[:1]
            if not variant:
                raise UserError('No se generó variante %s' % variant_sku)
            variant.write({'default_code': variant_sku, 'standard_price': cost})

    # ---------- Archivado de productos heredados (D11) ----------
    def _archive_legacy(self):
        Tmpl = self.env['product.template'].with_context(active_test=False)
        for code in D.LEGACY_ARCHIVE:
            tmpl = Tmpl.search([('default_code', '=', code)], limit=1)
            if tmpl and tmpl.active:
                tmpl.write({'active': False})
