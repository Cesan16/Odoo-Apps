{
    'name': 'Warranty',
    'version': '1.0',
    'category': 'Sales',
    'author': "Chinedu Uzuegbu (Cesan)",
    'summary': 'Module to manage warranties linked with the repair module',
    'description': """
        This module allows you to register warranties after sales, track warranty periods, 
        and automatically update the repair orders with warranty information.
    """,
    'depends': ['sale', 'stock', 'repair'],
    'data': [
        'views/warranty_views.xml',
        'views/repair_order_views_inherit.xml',
        'security/ir.model.access.csv',
        #'security/warranty_security.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
