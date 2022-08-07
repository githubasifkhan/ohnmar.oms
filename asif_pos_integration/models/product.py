# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, Warning

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    f_id = fields.Char('Foodics ID')
    business_date = fields.Date("Business Date")
    opener_id = fields.Many2one('res.users', "Opener")
    closer_id = fields.Many2one('res.users', "Closer")
    branch_id = fields.Many2one('pos.config', "Branch")
    f_opened_at = fields.Datetime('Foodics Opened Date')
    f_closed_at = fields.Datetime('Foodics Closed Date')
    f_created_at = fields.Datetime('Foodics Created Date')
    f_updated_at = fields.Datetime('Foodics Updated Date')
    f_deleted_at = fields.Datetime('Foodics Deleted Date')
