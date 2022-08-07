# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, Warning
from odoo.tools import float_compare, float_is_zero
from datetime import datetime
import logging
import json
import requests
_logger = logging.getLogger(__name__)

class MyMappingConfig(models.Model):
    _name = 'my.mapping.config'

    name = fields.Char('Name',required=True)
    api_url = fields.Char('Access URL',required=True)
    odoo_model_id = fields.Many2one('ir.model','Odoo Model')
    line_ids = fields.One2many('my.mapping.config.line', 'config_id', string='Lines', copy=True)
    access_token = fields.Char('Access Token')

    def action_integration(self,model):
        integration_ids = self.env['my.mapping.config'].search([('odoo_model_id.model','=',model)])
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU1MmJmZjJlZjFlMGU5ODUwMzYzZGU4YzFjZTc4ZmI0MjA2MzFlNDU5ZGM0YzQ0Mzg4N2RhNTA5NDgzMDI2OGVmMjQ3ZDRkNDc0M2JiNThlIn0.eyJhdWQiOiI5MGQ1YTcxOC1lMzBkLTQ5ODYtODY0Ni0wNjdlZDBkMzdkMGUiLCJqdGkiOiJlNTJiZmYyZWYxZTBlOTg1MDM2M2RlOGMxY2U3OGZiNDIwNjMxZTQ1OWRjNGM0NDM4ODdkYTUwOTQ4MzAyNjhlZjI0N2Q0ZDQ3NDNiYjU4ZSIsImlhdCI6MTY1NjQwMzcwOSwibmJmIjoxNjU2NDAzNzA5LCJleHAiOjE4MTQxNzAxMDksInN1YiI6IjkyZWI1NjU0LWQ5NDQtNGY4Yi1hZGNlLWU2MDk3YjY1ODZjZCIsInNjb3BlcyI6WyJnZW5lcmFsLnJlYWQiLCJvcmRlcnMubGlzdCJdLCJidXNpbmVzcyI6IjkyZWI1NjU0LWQ5ODEtNGZjMi1hZjU3LTM1MGFmZmUxMWJhOSIsInJlZmVyZW5jZSI6IjkwNzkzNCJ9.ObIh_KGnaYPGSrQij65LugRkeFmd8XcTs68S5fqTT40nl4pXIZRdyvFQu56Uu2TDqM5Eg79sRNR_Sy-mU7gtabOz1WYirb36IKYzPBHLrxW71eWdQW-7POUG2BSEPf0bGQZ68uiZ_h-Gax7ycccCuagKJX4veIiJixuAwLMwBTyC2jQxm7r6uoI5mrKoJFaZGgwK44lDuE3uuqjE2gq3cGymjKFk3SP5QkYkJGFgTTM438HvlQKWfI4J01YJywfDZ6NveQ47gGPgSIizNDtL8YwrQQC7pdmNww91Ig5wiu47RZ8NqTEmzZp-WuDV1nN6XjmOu-zXVfSEG8MqZ2XFyN9PMj1wkOdlh6drzXpJbZCJEaFOQY3tnjAT7oj7Dw9_rmnxeY8FROiUgxNPTVmIwZ0OSKbThhcJpir-MzRvTqFWJ4KFQ1C5NWQl34gTbTIZGHBkTokVgikREWFNmtQ8mMosdv2GD-3sI8ZQkoiTbLtlj3gLOB0Aa6yIdNe13oNNUnPWwtrSWkEUEy-5k7GfEebdZH4Oo8fx56PJHbyH7gvQapfhxIBzmuRTh_v8AtfyKo9aO3ocOouwOD_8UJoahzkq2sOKD2elp0DlqJ1DMrKJyTM1wdWbZt-HLt37KfUtA3DY6OjM0hfSvfiXsQTaXPoh_XJbPqvMhMHpvPCLr6U"
        hed = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
        for integration in integration_ids:
            # import pdb;pdb.set_trace()
            # myresponse = requests.post("https://powerschool.isyedu.org/ws/schema/query/api.school.pull_odoo_student?pagesize=0", headers=hed)
            # model = integration.odoo_model_id.model
            myresponse = requests.get(integration.api_url,headers=hed)
            mydata = myresponse.json()
            foodics_data = mydata.get('data') or []
            _logger.info("@@@@ Data from Foodics %s "%(integration.odoo_model_id.name))
            _logger.info(foodics_data)

            for f_data in foodics_data:
                tmp = integration.create_by_integration(f_data)
        return

    def create_by_integration(self,f_data):
        integration = self
        model = self.odoo_model_id.model
        field_dict = {}
        for integration_line in integration.line_ids.filtered(lambda x: x.odoo_field_id):
            odoo_field_id=integration_line.odoo_field_id
            odoo_relation_id = integration_line.odoo_relation_id
            odoo_relation_name = integration_line.odoo_relation_name

            foodics_value = f_data.get(integration_line.name)
            if integration_line.name=='type' and integration.odoo_model_id.model=='pos.payment.method':
                journal_obj = self.env['account.journal']
                name = f_data.get('name')
                code = f_data.get('code') 
                code = code or (name if len(name)>4 else name[0:3])
                journal_id = journal_obj.search([('code','=',code)])
                _logger.info(foodics_value)
                if foodics_value=='1' or foodics_value==1:
                    
                    type = 'cash'
                elif foodics_value=='2' or foodics_value=='2':
                    type = 'bank'
                else:
                    type = 'general'
                _logger.info(type)
                _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ')
                _logger.info(name)
                _logger.info(code or (name if len(name)>4 else name[::-1][0:4]))
                if not journal_id:
                    journal_id = journal_obj.create({
                        'name': code,
                        'type': type,
                        'code': code or (name if len(name)>4 else name[::-1][0:4]),
                    })
                field_dict['journal_id'] = journal_id.id

            if odoo_field_id:
                field_type=odoo_field_id.ttype
                if odoo_field_id.required and not foodics_value:
                    _logger.info('@@@@@@@@@@@@ %s of %s is missing.'%(odoo_field_id.field_description,model))
                    _logger.info(foodics_value)
                    return
                if field_type == "boolean":
                    field_dict[integration_line.odoo_field_id.name] = foodics_value or False
                elif field_type == "datetime" and foodics_value:
                    date_time_obj = datetime.strptime(foodics_value, '%Y-%m-%d %H:%M:%S')
                    field_dict[integration_line.odoo_field_id.name] = date_time_obj

                elif field_type == "date" and foodics_value:
                    date_obj = datetime.strptime(foodics_value, '%Y-%m-%d')
                    field_dict[integration_line.odoo_field_id.name] = date_obj

                elif field_type == "many2many" and foodics_value:
                    field_relation = self.env[odoo_field_id.relation]
                    if 'f_id' in field_relation.field_id.mapped('name'):
                        many2many_ids = []
                        for f_value in foodics_value:
                            existing_rec = field_relation.search([('f_id', '=', f_value.get('id'))])
                            if not existing_rec:
                                inner_integration = self.env['my.mapping.config'].search([('odoo_model_id.model', '=' ,odoo_field_id.relation)])
                                if inner_integration:
                                    many2many_id = inner_integration.create_by_integration(f_value)
                                    many2many_ids.append(many2many_id.id)
                            else:
                                many2many_ids.append(existing_rec.id)

                        field_dict[integration_line.odoo_field_id.name] = many2many_ids
                elif field_type == "many2one" and foodics_value:
                    field_relation = self.env[odoo_field_id.relation]
                    if 'f_id' in field_relation.field_id.mapped('name'):
                        existing_rec = field_relation.search([('f_id', '=', foodics_value.get('id'))])
                        if not existing_rec:
                            inner_integration = self.env['my.mapping.config'].search([('odoo_model_id.model', '=' ,odoo_field_id.relation)])
                            if inner_integration:
                                many2one_id = inner_integration.create_by_integration(f_value)
                                field_dict[integration_line.odoo_field_id.name] = many2one_id.id
                        else:
                            field_dict[integration_line.odoo_field_id.name] = existing_rec.id

                elif field_type == "integer" and foodics_value:
                    field_dict[integration_line.odoo_field_id.name] = int(foodics_value)
                elif field_type == "float" and foodics_value:
                    field_dict[integration_line.odoo_field_id.name] = float(foodics_value)
                elif foodics_value: # Char
                    field_dict[integration_line.odoo_field_id.name] = str(foodics_value)

        if len(field_dict.keys())>0:
            existing_record = self.env[model].search([('f_id', '=', f_data.get('id'))])
            if integration.odoo_model_id.model=='product.template':
                field_dict['available_in_pos'] = True
            _logger.info(field_dict)
            if existing_record:
                existing_record.update(field_dict)
            else:
                existing_record = self.env[model].create(field_dict)

        # CASE: when sync category, datas contain product list
        for integration_line in integration.line_ids.filtered(lambda x: x.odoo_relation_id and x.odoo_relation_name and not x.odoo_field_id):
            odoo_field_id=integration_line.odoo_field_id
            odoo_relation_id = integration_line.odoo_relation_id
            field_relation = self.env[odoo_relation_id.model]
            odoo_relation_name = integration_line.odoo_relation_name
            foodics_value = f_data.get(integration_line.name) or []
            # foodics_value means product list
            # existing_record means category id

            for f_value in foodics_value:
                if f_value.get('id'):
                    existing_rec = field_relation.search([('f_id', '=', f_value.get('id'))])
                    _logger.info("@@@@@@@@@@@@ Without Odoo field")
                    _logger.info('%s,%s'%(existing_record.id,existing_record.name))
                    if existing_rec:
                        existing_rec.update({odoo_relation_name : existing_record.id})
                    # else:
                    #     inner_integration = self.env['my.mapping.config'].search([('odoo_model_id', '=' ,odoo_relation_id.id)])
                    #     if inner_integration:
                    #         try:
                    #             many2one_id = inner_integration.create_by_integration(f_value)
                    #             many2one_id.update({odoo_relation_name : existing_record.id})
                    #         except Exception as e:
                    #             _logger.info("Data is not enough to create record. %s, %s"%(odoo_relation_id.model,str(f_value)))

        return existing_record


class MyMappingConfigLine(models.Model):
    _name = 'my.mapping.config.line'

    name = fields.Char('Name')
    config_id = fields.Many2one('my.mapping.config','Config')
    odoo_field_id = fields.Many2one('ir.model.fields','Odoo Field', domain="[('model_id','=',parent.odoo_model_id)]")
    odoo_relation_id = fields.Many2one(
        'ir.model',
        string='Odoo Relation',
        )
    odoo_relation_name = fields.Char('Odoo Relation Name')
