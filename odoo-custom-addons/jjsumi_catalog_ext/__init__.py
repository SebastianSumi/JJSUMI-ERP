# -*- coding: utf-8 -*-
from . import models


def post_init_hook(env):
    """Carga idempotente del catálogo Fase 2 al instalar el módulo."""
    env['jjsumi.catalog.loader'].run()
