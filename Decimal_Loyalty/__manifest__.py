# __manifest__.py
{
    'name': 'Custom_Loyalty_Program',
    'version': '15.0.1.0.0',
    'author': 'Chinedu Uzuegbu (cesan)',
    'category': 'Tools',
    'depends': ['base', 'pos_loyalty'],  # Add any dependencies here
    'data': [
        #'views/loyalty_program_views.xml',  # Make sure to adjust the path if needed
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
