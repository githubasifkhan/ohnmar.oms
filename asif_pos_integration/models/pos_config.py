# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, Warning
from odoo.tools import float_compare, float_is_zero
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class POSConfig(models.Model):
    _inherit = 'pos.config'

    f_id = fields.Char('Foodics ID')
    name_localized = fields.Char('Name Localized')
    reference = fields.Char('Reference')
    latitude = fields.Char('Latitude')
    longitude = fields.Char('Longitude')
    phone = fields.Char('Phone')
    opening_from = fields.Char('Opening From')
    opening_to = fields.Char('Opening To')
    inventory_end_of_day_time = fields.Char('Inventory End Time')
    receives_online_orders = fields.Boolean('Receives Online Orders')
    f_created_at = fields.Datetime('Foodics Created Date')
    f_updated_at = fields.Datetime('Foodics Updated Date')
    f_deleted_at = fields.Datetime('Foodics Deleted Date')
