{
    'name': 'Stock Delivery Restriction',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Restrict delivery of products not available in stock',
    'description': """
        This module restricts users from delivering products that are not available in stock.
    """,
    'author': 'Chinedu Uzuegbu (Cesan)',
    'depends': ['base', 'stock'],
    'data': [
        'stock_deliver_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
