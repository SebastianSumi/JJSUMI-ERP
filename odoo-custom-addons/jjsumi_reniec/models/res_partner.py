# -*- coding: utf-8 -*-
import hashlib
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

_NOMBRES = [
    'Carlos', 'María', 'José', 'Lucía', 'Luis', 'Ana', 'Jorge', 'Rosa',
    'Pedro', 'Elena', 'Miguel', 'Gabriela', 'Fernando', 'Claudia', 'Ricardo', 'Sofía',
]
_APELLIDOS = [
    'Quispe', 'Mamani', 'Flores', 'Huanca', 'Rojas', 'Condori', 'Vargas', 'Torres',
    'Pari', 'Apaza', 'Calsin', 'Chura', 'Laura', 'Sucasaca', 'Aguilar', 'Delgado',
]
_RAZONES = [
    'Constructora', 'Distribuidora', 'Inversiones', 'Comercializadora',
    'Ferretería Industrial', 'Acabados y Materiales', 'Servicios Generales', 'Grupo',
]
_SUFIJOS = ['S.A.C.', 'S.R.L.', 'E.I.R.L.']
_CALLES = [
    'Jr. Lambayeque', 'Av. Circunvalación', 'Av. El Sol', 'Jr. Lima',
    'Av. Ejército', 'Av. La Cultura', 'Jr. 7 de Junio', 'Av. Bolognesi',
]
_CIUDADES = [
    ('Juliaca', 'PUN'),
    ('Puno', 'PUN'),
    ('Arequipa', 'ARE'),
    ('Cusco', 'CUS'),
    ('Tacna', 'TAC'),
    ('Lima', 'LIM'),
]


def _ruc_valido(ruc):
    if not ruc or len(ruc) != 11 or not ruc.isdigit():
        return False
    if ruc[:2] not in ('10', '15', '17', '20'):
        return False
    pesos = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
    suma = sum(int(ruc[i]) * pesos[i] for i in range(10))
    digito = (11 - (suma % 11)) % 10
    return digito == int(ruc[10])


class ResPartnerReniec(models.Model):
    _inherit = 'res.partner'

    jjsumi_reniec_estado = fields.Char(
        string='Estado RENIEC/SUNAT',
        readonly=True,
        copy=False,
    )

    def _jjsumi_detectar_tipo(self):
        """Devuelve ('dni'|'ruc'|False, numero_limpio)."""
        self.ensure_one()
        num = (self.vat or '').strip()
        if not num:
            return False, ''
        tipo_nombre = (self.l10n_latam_identification_type_id.name or '').upper()
        if 'DNI' in tipo_nombre:
            return 'dni', num
        if 'RUC' in tipo_nombre:
            return 'ruc', num
        if num.isdigit() and len(num) == 8:
            return 'dni', num
        if num.isdigit() and len(num) == 11:
            return 'ruc', num
        return False, num

    def _jjsumi_lookup_mock(self, tipo, num):
        """Consulta en caché local (BD) o genera datos de prueba determinísticos (costo S/ 0)."""
        # 1. Caché local: reutilizar si ya existe otro contacto con ese mismo documento
        existing = self.env['res.partner'].sudo().search([
            ('vat', '=', num),
            ('id', '!=', self._origin.id or 0),
            ('name', '!=', False),
        ], limit=1)
        if existing:
            return {
                'name': existing.name,
                'street': existing.street or '',
                'city': existing.city or '',
                'state_id': existing.state_id.id or False,
                'country_id': existing.country_id.id or False,
                'company_type': 'company' if existing.is_company else 'person',
                'jjsumi_reniec_estado': _('Recuperado de caché local (%s)', tipo.upper()),
            }

        # 2. Generación determinística en modo pruebas
        seed = int(hashlib.sha256(num.encode('utf-8')).hexdigest()[:8], 16)
        ciudad, state_code = _CIUDADES[seed % len(_CIUDADES)]
        calle = f"{_CALLES[(seed >> 4) % len(_CALLES)]} Nro. {100 + (seed % 899)}"
        pe = self.env.ref('base.pe', raise_if_not_found=False)
        state = self.env['res.country.state'].sudo().search([
            ('country_id', '=', pe.id if pe else 0),
            ('code', '=', state_code),
        ], limit=1)

        if tipo == 'dni':
            nom1 = _NOMBRES[seed % len(_NOMBRES)]
            ape1 = _APELLIDOS[(seed >> 4) % len(_APELLIDOS)]
            ape2 = _APELLIDOS[(seed >> 8) % len(_APELLIDOS)]
            return {
                'name': f"{nom1} {ape1} {ape2}",
                'street': calle,
                'city': ciudad,
                'state_id': state.id or False,
                'country_id': pe.id if pe else False,
                'company_type': 'person',
                'jjsumi_reniec_estado': _('Verificado RENIEC (Modo Pruebas)'),
            }

        # RUC
        pref = _RAZONES[seed % len(_RAZONES)]
        ape = _APELLIDOS[(seed >> 4) % len(_APELLIDOS)]
        suf = _SUFIJOS[(seed >> 8) % len(_SUFIJOS)]
        is_empresa = num.startswith('20')
        nombre = f"{pref} {ape} {suf}" if is_empresa else f"{_NOMBRES[seed % len(_NOMBRES)]} {ape}"
        return {
            'name': nombre,
            'street': calle,
            'city': ciudad,
            'state_id': state.id or False,
            'country_id': pe.id if pe else False,
            'company_type': 'company' if is_empresa else 'person',
            'jjsumi_reniec_estado': _('Verificado SUNAT - Activo / Habido (Modo Pruebas)'),
        }

    def _jjsumi_lookup_api(self, provider, token, tipo, num):
        """Consulta real a apis.net.pe, apisperu.com o apiperu.dev."""
        headers = {'Accept': 'application/json'}
        try:
            if provider == 'apisnetpe':
                headers['Authorization'] = f'Bearer {token}'
                url = (
                    f'https://api.apis.net.pe/v2/reniec/dni?numero={num}'
                    if tipo == 'dni'
                    else f'https://api.apis.net.pe/v2/sunat/ruc?numero={num}'
                )
                resp = requests.get(url, headers=headers, timeout=6)
            elif provider == 'apisperu':
                url = (
                    f'https://dniruc.apisperu.com/api/v1/dni/{num}?token={token}'
                    if tipo == 'dni'
                    else f'https://dniruc.apisperu.com/api/v1/ruc/{num}?token={token}'
                )
                resp = requests.get(url, headers=headers, timeout=6)
            elif provider == 'apiperudev':
                headers['Authorization'] = f'Bearer {token}'
                headers['Content-Type'] = 'application/json'
                url = f'https://apiperu.dev/api/{tipo}'
                resp = requests.post(url, json={tipo: num}, headers=headers, timeout=6)
            else:
                return None
        except requests.RequestException as exc:
            _logger.warning('Error consultando %s (%s): %s', provider, num, exc)
            raise UserError(_('No se pudo conectar con el servicio %s: %s', provider, exc))

        if resp.status_code in (401, 403):
            raise UserError(_('Token inválido o sin cuota en %s (HTTP %s).', provider, resp.status_code))
        if resp.status_code == 404:
            raise UserError(_('No se encontraron datos para %s "%s".', tipo.upper(), num))
        if resp.status_code >= 400:
            raise UserError(_('Error en %s (HTTP %s): %s', provider, resp.status_code, resp.text[:200]))

        payload = resp.json() or {}
        data = payload.get('data') if isinstance(payload.get('data'), dict) else payload
        pe = self.env.ref('base.pe', raise_if_not_found=False)

        if tipo == 'dni':
            nombre = (
                data.get('nombre_completo')
                or data.get('nombreCompleto')
                or ' '.join(filter(None, [
                    data.get('nombres'),
                    data.get('apellidoPaterno') or data.get('apellido_paterno'),
                    data.get('apellidoMaterno') or data.get('apellido_materno'),
                ])).strip()
            )
            if not nombre:
                raise UserError(_('La API no devolvió nombres para el DNI %s.', num))
            return {
                'name': nombre.title(),
                'country_id': pe.id if pe else False,
                'company_type': 'person',
                'jjsumi_reniec_estado': _('Verificado RENIEC (%s)', provider),
            }

        razon = data.get('razonSocial') or data.get('nombre_o_razon_social') or data.get('nombre')
        if not razon:
            raise UserError(_('La API no devolvió razón social para el RUC %s.', num))
        estado = data.get('estado') or ''
        condicion = data.get('condicion') or ''
        detalle = ' / '.join(filter(None, [estado, condicion])) or provider
        return {
            'name': razon.strip(),
            'street': (data.get('direccion') or data.get('direccion_completa') or '').strip(),
            'city': (data.get('distrito') or data.get('provincia') or '').strip().title(),
            'country_id': pe.id if pe else False,
            'company_type': 'company' if num.startswith('20') else 'person',
            'jjsumi_reniec_estado': _('Verificado SUNAT - %s', detalle),
        }

    def _jjsumi_aplicar_consulta(self, raise_on_invalid=False):
        self.ensure_one()
        tipo, num = self._jjsumi_detectar_tipo()
        if not num:
            if raise_on_invalid:
                raise UserError(_('Ingrese un número de DNI (8 dígitos) o RUC (11 dígitos) primero.'))
            return False
        if tipo == 'dni' and (not num.isdigit() or len(num) != 8):
            if raise_on_invalid:
                raise UserError(_('El DNI debe tener exactamente 8 dígitos numéricos.'))
            return False
        if tipo == 'ruc' and not _ruc_valido(num):
            if raise_on_invalid:
                raise UserError(_('El RUC "%s" no es válido (debe tener 11 dígitos y dígito verificador SUNAT correcto).', num))
            return False
        if not tipo:
            if raise_on_invalid:
                raise UserError(_('Seleccione tipo DNI (8 dígitos) o RUC (11 dígitos).'))
            return False

        icp = self.env['ir.config_parameter'].sudo()
        provider = icp.get_param('jjsumi.reniec_provider', 'mock')
        token = (icp.get_param('jjsumi.reniec_token') or '').strip()

        if provider != 'mock':
            if not token:
                if raise_on_invalid:
                    raise UserError(_(
                        'Falta el Token API para "%s". Configúrelo en Ajustes → Consulta RENIEC / SUNAT.',
                        provider))
                return False
            vals = self._jjsumi_lookup_api(provider, token, tipo, num)
        else:
            vals = self._jjsumi_lookup_mock(tipo, num)

        for field_name, value in vals.items():
            setattr(self, field_name, value)
        return True

    @api.onchange('vat', 'l10n_latam_identification_type_id')
    def _onchange_jjsumi_reniec(self):
        for partner in self:
            if not partner.vat or partner.name:
                continue
            partner._jjsumi_aplicar_consulta(raise_on_invalid=False)

    def action_jjsumi_consultar_reniec(self):
        for partner in self:
            partner._jjsumi_aplicar_consulta(raise_on_invalid=True)
        return True
