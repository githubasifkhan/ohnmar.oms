# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, Warning
from odoo.tools import float_compare, float_is_zero
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    name_localized = fields.Char('Name Localized')
    f_id = fields.Char('Foodics ID')
    reference = fields.Char('Reference')
    image = fields.Char('Image URL')
    f_created_at = fields.Datetime('Foodics Created Date')
    f_updated_at = fields.Datetime('Foodics Updated Date')
    f_deleted_at = fields.Datetime('Foodics Deleted Date')