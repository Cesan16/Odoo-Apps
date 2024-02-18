# models.py

from odoo import models, fields

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    # Update the 'points' field with default decimal places set to 3
    points = fields.Float(string='Points', digits=(16, 3))
