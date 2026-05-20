# -*- coding: utf-8 -*-
{
    "name": "Sale Cash Credit Payment",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Chinedu Uzuegbu",
    "summary": "Handle cash and credit sale order flows with automatic invoice payment",
    "depends": ["sale_management", "sale_stock", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/sale_confirm_warning_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
