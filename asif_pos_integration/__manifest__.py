# -*- coding: utf-8 -*-

{
    'name': 'Asif Foodics Integration',
    'version': '15.0.1',
    'summary': """Integration""",
    'description': """
    Integrate with Foodics
        1. Product
        2. Product Category
        3. POS Sale Order
        4. Payment
        5. Branch
    """,
    'category': "Generic Modules/Tools",
    'author': 'Ohnmar Soe',
    'company': 'Asif',
    'depends': ['base','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/product_category_view.xml',
        'views/product_view.xml',
        'views/pos_config_view.xml',
        'views/payment.xml',
        'data/ir_cron.xml',
        'demo/mapping_config_demo.xml',
    ],
    # "external_dependencies": {"python3": ["pyjwt"]},
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
