# -*- coding: utf-8 -*-
import odoo
from odoo import http, _
from odoo.http import request, Response
from odoo.addons.web.controllers import main
import json
from odoo.service import db, security
import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceController(http.Controller):

    # @http.route("/check_method_get", auth='none', type='http',method=['GET'])
    # def check_method_get(self,**values):
    #     headers = {'Content-Type': 'application/json'}
    #     body = { 'results': { 'code':200, 'message':'OK' } }

    #     return Response(json.dumps(body), headers=headers)

    # 1. Define allow_domain_ps
    # 2. Define ps_api_decode_secret
    # 3. Define ps_student_decode_secret
    # 4. Define database.db_name
    @http.route('/invoices', methods=['POST'], csrf=False, type='http', auth="none")
    def print_id(self, **kw):
        #check allow url or not
        # allow_url = request.env['ir.config_parameter'].sudo().get_param('allow_domain_ps') or False
        # _logger.info(request.httprequest.environ)
        # if request.httprequest.environ.get('REMOTE_ADDR') != allow_url:
        #     if allow_url == False:
        #         status = {'code': 401, 'description': "Unauthorized. Please contact to system administrator to define allow url."}
        #     else:
        #         status = {'code': 401, 'description': "Unauthorized. Request URL is not allowed."}
        #     return json.dumps(status)
        #get api token and decryption by using HS256 JWT auth

        #b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Im9kb29hZG1pbkBpc3llZHUub3JnIiwicGFzc3dvcmQiOiJPZDAwQGRtIW4yMDIwIn0.drO_eJxRdVMwuZDc7irNHzLOIGfsEGET1cYE6pL1bT0'
        #get encrypted api-key
        encoded_jwt = request.httprequest.headers.get('Api-Key') or False
        #decode username and password dict
        credential_dict = jwt.decode(encoded_jwt, '3498CA36F63D31C8C5311BB657C8B', algorithms=['HS256'])

        username = credential_dict['username']
        password = credential_dict['password']
        database = request.env['ir.config_parameter'].sudo().get_param('database.db_name') or False
        if database == False:
            status = {'code': 401, 'description': "Unauthorized. Please contact to system administrator to define default database."}
            return json.dumps(status)
        result = main.Session.authenticate(self, database, username, password)
        if not result['session_id']:
            status = {'code': 401, 'description': "Unauthorized Api Token."}
            return json.dumps(status)

        student_id = kw['student_id']
        #matching actual student_id and encrypted student id 105957
        #eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbmNfc3R1ZGVudF9pZCI6MTA1OTU3fQ.fWudP2jy2HvMeUDLgCM-gpzPwEsHN2vjAfQ-Etr7B9I
        enc_student_id_dict = jwt.decode(kw['enc_student_id'], '3498CA36F63D31C8C5311BB657C8B', algorithms=['HS256'])
        enc_student_id = enc_student_id_dict['enc_student_id']
        if int(student_id) == int(enc_student_id):
            partner_student_id = request.env['res.partner'].search([('student_number', '=', student_id)])
            if not partner_student_id:
                status = {'code': 404, 'description': "Not Found. Student does not exist in Odoo."}
                return json.dumps(status)
            last_invoice_id = request.env['account.invoice'].search([('partner_id', '=', partner_student_id.id)], limit=1)
            if not last_invoice_id:
                status = {'code': 404, 'description': "Not Found. There has no invoice for this student."}
                return json.dumps(status)
            data = '["/report/pdf/account.report_invoice_with_payments_copy_1_copy_5/%s","qweb-pdf"]' % (last_invoice_id.id,)
            response = main.ReportController.report_download(main.ReportController(), data, request.session.session_token)
            return response
        else:
            status = {'code': 404, 'description': "Not Found. Unauthorized student id."}
            return json.dumps(status)

    @http.route('/products', methods=['POST'], csrf=False, type='http', auth="none")
    def get_product_list(self,**kw):
        #get encrypted api-key
        encoded_jwt = request.httprequest.headers.get('Api-Key') or False
        if encoded_jwt:
            #decode username and password dict
            credential_dict = jwt.decode(encoded_jwt, '3498CA36F63D31C8C5311BB657C8B', algorithms=['HS256'])

            username = credential_dict['username']
            password = credential_dict['password']
            database = request.env['ir.config_parameter'].sudo().get_param('database.db_name') or False
            if database == False:
                status = {'code': 401, 'description': "Unauthorized. Please contact to system administrator to define default database."}
                return json.dumps(status)
            result = main.Session.authenticate(self, database, username, password)
            if not result['session_id']:
                status = {'code': 401, 'description': "Unauthorized Api Token."}
                return json.dumps(status)
        else:
            status = {'code': 401, 'description': "Unauthorized Api Token."}
            return json.dumps(status)
            
        stock_objs = request.env['isy.stock.report'].sudo().search([('location_id.usage','=','internal')])

        query = """
                SELECT pt.name AS pname, product_id,
                    catg.name AS cname, product_category as category_id,
                    COUNT(*) AS total_qty,
                    SUM(CASE WHEN stock.user_email IS NULL THEN 1 ELSE 0 END) AS avail_qty,
                    SUM(CASE WHEN stock.user_email IS NOT NULL THEN 1 ELSE 0 END) AS reserved_qty
                FROM isy_stock_report stock
                LEFT JOIN product_product pp ON pp.id=stock.product_id
                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                LEFT JOIN stock_location loc ON loc.id=stock.location_id
                LEFT JOIN product_category catg ON catg.id=stock.product_category
                WHERE loc.usage='internal' and (catg.is_it=True OR pt.is_it=True)
                GROUP BY pt.name,product_id,catg.name,product_category
                ORDER BY pt.name;
                """
        request.env.cr.execute(query)
        product_obj = request.env['product.product'].sudo()
        records = request.env.cr.dictfetchall()
        results = []
        product_ids = [r.get('product_id') for r in records]
        image_dt = product_obj.search_read([('id','in',product_ids)],['image_small'])
        for record in records:
            image = list(filter(lambda x:x.get('id')==record.get('product_id'),image_dt))[0].get('image_small')
            results.append({**record,'image':image.decode('utf-8') if image else ''})
        return json.dumps({'code': 200,'description':'Success','data':results})

    @http.route('/products/reserve/<int:product_id>/<string:user_email>', methods=['POST'], csrf=False, type='http', auth="none")
    def get_product_reserve(self,product_id,user_email,**kw):
        #get encrypted api-key
        encoded_jwt = request.httprequest.headers.get('Api-Key') or False
        if encoded_jwt:
            #decode username and password dict
            credential_dict = jwt.decode(encoded_jwt, '3498CA36F63D31C8C5311BB657C8B', algorithms=['HS256'])

            username = credential_dict['username']
            password = credential_dict['password']
            database = request.env['ir.config_parameter'].sudo().get_param('database.db_name') or False
            if database == False:
                status = {'code': 401, 'description': "Unauthorized. Please contact to system administrator to define default database."}
                return json.dumps(status)
            result = main.Session.authenticate(self, database, username, password)
            if not result['session_id']:
                status = {'code': 401, 'description': "Unauthorized Api Token."}
                return json.dumps(status)
        else:
            status = {'code': 401, 'description': "Unauthorized Api Token."}
            return json.dumps(status)

        _logger.debug('##### Reserve Process')
        _logger.debug(product_id)
        _logger.debug(user_email)
        stock_obj = request.env['isy.stock.report'].sudo().search([('product_id','=',product_id),('user_email','=',False)], limit=1)
        
        if not stock_obj:
            response = {'code': 404, 'description': "There is no product that can be reserved. Please contact to admin."}
            return json.dumps(response)
        stock_obj.write({'user_email': user_email})
        template = request.env.ref('mt_isy.stock_reserve_inventory_user_noti')
        request.env['mail.template'].sudo().browse(template.id).send_mail(stock_obj.id)
        response = {'code': 200, 'description': "You have already reserved "+stock_obj.serial_number+" of "+stock_obj.product_id.name+"."}
        return json.dumps(response)
    
    @http.route('/products/cancel/<int:product_id>/<string:user_email>', methods=['POST'], csrf=False, type='http', auth="none")
    def get_product_cancel(self,product_id,user_email):
        #get encrypted api-key
        encoded_jwt = request.httprequest.headers.get('Api-Key') or False
        if encoded_jwt:
            #decode username and password dict
            credential_dict = jwt.decode(encoded_jwt, '3498CA36F63D31C8C5311BB657C8B', algorithms=['HS256'])

            username = credential_dict['username']
            password = credential_dict['password']
            database = request.env['ir.config_parameter'].sudo().get_param('database.db_name') or False
            if database == False:
                status = {'code': 401, 'description': "Unauthorized. Please contact to system administrator to define default database."}
                return json.dumps(status)
            result = main.Session.authenticate(self, database, username, password)
            if not result['session_id']:
                status = {'code': 401, 'description': "Unauthorized Api Token."}
                return json.dumps(status)
        else:
            status = {'code': 401, 'description': "Unauthorized Api Token."}
            return json.dumps(status)
        
        _logger.debug('##### Cancel Process')
        _logger.debug(product_id)
        _logger.debug(user_email)
        # clear user_email when return back to IT Inventory
        stock_obj = request.env['isy.stock.report'].sudo().search([('product_id','=',product_id),('user_email','=',user_email)])
        if not stock_obj:
            response = {'code': 404, 'description': "There is no product that had been reserved by you. Please contact to admin."}
            return json.dumps(response)
        #already checked out, email notify 
        elif len(stock_obj)==1 and  stock_obj.location_id.name != 'A10 IT Storage':
            template = request.env.ref('mt_isy.stock_cancel_inventory_user_noti_tocheckin')
            request.env['mail.template'].sudo().browse(template.id).send_mail(stock_obj.id)
            response = {'code': 200, 'description': "Please return this product to IT Inventory."}
            return json.dumps(response)
        elif len(stock_obj)==1:
            template = request.env.ref('mt_isy.stock_cancel_inventory_user_noti')
            request.env['mail.template'].sudo().browse(template.id).send_mail(stock_obj.id)
            stock_obj.write({'user_email':False})
            response = {'code':200, 'description': "Success"}
            return json.dumps(response)
        elif len(stock_obj)>1:
            s_obj = stock_obj.filtered(lambda x: x.location_id.name == 'A10 IT Storage')
            if s_obj:
                template = request.env.ref('mt_isy.stock_cancel_inventory_user_noti')
                request.env['mail.template'].sudo().browse(template.id).send_mail(s_obj[0].id)
                s_obj[0].write({'user_email':False})
                response = {'code':200, 'description': "Success"}
                return json.dumps(response)
            else:
                template = request.env.ref('mt_isy.stock_cancel_inventory_user_noti_tocheckin')
                request.env['mail.template'].sudo().browse(template.id).send_mail(stock_obj[0].id)
                response = {'code': 200, 'description': "Please return this product to IT Inventory."}
                return json.dumps(response)

