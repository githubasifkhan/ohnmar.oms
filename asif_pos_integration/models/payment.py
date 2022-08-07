# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, Warning

class POSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    f_id = fields.Char('Foodics ID')
    name_localized = fields.Char("Name Localized")
    code = fields.Char('Code')
    auto_open_drawer = fields.Boolean('Auto Open Drawer')
    f_type = fields.Selection([('1','Cash'),('2','Card'),('3','Other'),('4','Gift Card'),('5','House Account'),('7','3rd Party')],string='Type')
    is_active = fields.Boolean('Active')
    f_created_at = fields.Datetime('Foodics Created Date')
    f_updated_at = fields.Datetime('Foodics Updated Date')
    f_deleted_at = fields.Datetime('Foodics Deleted Date')


    
