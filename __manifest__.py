{
    'name': 'Public Acquisition',
    'version': '11.0.1.0.0',
    'author': 'Aleksandra Shumkoska', 
    'support': 'a_shumkoska@yahoo.com',
    'license': 'Other proprietary',
    'category': 'Purchases',
    'summary': 'Public Acquisition',
    'description': ''' 
        Public Acquisition 
    ''',
    'depends': [
        'mail', 
        'purchase',
        'web_digital_sign'
    ],
    'data': [
        'views/acquisition_offer.xml',
        'views/acquisition_plan.xml',
        'views/commission_member.xml',
        'wizard/sign_acquisition_plan.xml',
        'views/mail_activity.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'auto_install': False,
    'price': 00.00,
    'currency': 'EUR',
}
