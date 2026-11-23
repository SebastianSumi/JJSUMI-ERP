# -*- coding: utf-8 -*-
from odoo import models


class JjsumiParams(models.AbstractModel):
    _name = "jjsumi.params"
    _description = "Parámetros CORE JJSUMI"

    def get(self, key, default=""):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    def set(self, key, value):
        self.env["ir.config_parameter"].sudo().set_param(key, value)
