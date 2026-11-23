# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class JjsumiMarketingSeed(models.AbstractModel):
    _name = 'jjsumi.marketing.seed'
    _description = 'Carga inicial del área Marketing'

    @api.model
    def _jjsumi_seed(self):
        self._seed_lista_correo()
        self._seed_automatizaciones()
        self._seed_encuesta()
        return True

    def _seed_lista_correo(self):
        if 'mailing.list' not in self.env:
            return
        Lista = self.env['mailing.list']
        if Lista.search_count([('name', '=', 'Clientes JJSumi')]):
            return
        try:
            with self.env.cr.savepoint():
                Lista.create({'name': 'Clientes JJSumi'})
        except Exception:  # noqa: BLE001
            _logger.exception('JJSumi: no se pudo crear la lista de correo')

    def _seed_automatizaciones(self):
        Auto = self.env['jjsumi.automatizacion']
        if Auto.search_count([]):
            return
        try:
            with self.env.cr.savepoint():
                Auto.create([
                    {
                        'name': 'Gracias por tu compra (WhatsApp)',
                        'disparador': 'postventa', 'dias': 2, 'canal': 'whatsapp',
                        'mensaje': 'Hola {nombre}, gracias por comprar yeso JJSumi. '
                                   '¿Cómo te fue con el producto? Escríbenos para tu próximo pedido.',
                    },
                    {
                        'name': 'Reactivación a 30 días (correo)',
                        'disparador': 'reactivacion', 'dias': 30, 'canal': 'correo',
                        'asunto': '¿Necesitas más yeso? - JJSumi',
                        'mensaje': 'Hola {nombre}, hace un mes que no te visitamos. '
                                   'Recuerda: por cada 200 bolsas te regalamos 3.',
                    },
                ])
        except Exception:  # noqa: BLE001
            _logger.exception('JJSumi: no se pudieron crear las automatizaciones iniciales')

    def _seed_encuesta(self):
        if 'survey.survey' not in self.env:
            return
        Survey = self.env['survey.survey']
        titulo = 'Satisfacción del cliente JJSumi'
        if Survey.with_context(active_test=False).search_count([('title', '=', titulo)]):
            return
        try:
            with self.env.cr.savepoint():
                survey = Survey.create({'title': titulo})
                Q = self.env['survey.question']
                Q.create({
                    'survey_id': survey.id, 'title': '¿Qué tan satisfecho está con la calidad del yeso?',
                    'question_type': 'simple_choice', 'sequence': 1,
                    'suggested_answer_ids': [(0, 0, {'value': v, 'sequence': i}) for i, v in enumerate(
                        ['Muy satisfecho', 'Satisfecho', 'Regular', 'Insatisfecho'], start=1)],
                })
                Q.create({
                    'survey_id': survey.id, 'title': '¿La entrega llegó a tiempo?',
                    'question_type': 'simple_choice', 'sequence': 2,
                    'suggested_answer_ids': [(0, 0, {'value': v, 'sequence': i}) for i, v in enumerate(
                        ['Sí', 'Con retraso', 'No llegó'], start=1)],
                })
                Q.create({
                    'survey_id': survey.id, 'title': '¿Qué podemos mejorar?',
                    'question_type': 'text_box', 'sequence': 3,
                })
        except Exception:  # noqa: BLE001
            _logger.exception('JJSumi: no se pudo crear la encuesta inicial')
