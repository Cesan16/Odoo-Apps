from odoo import models, fields, api

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    warranty_id = fields.Many2one('product.warranty', string='Warranty', help="Associated Warranty")
    warranty_status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('no_warranty', 'No Warranty')  # Added 'No Warranty' status
    ], string='Warranty Status', compute='_compute_warranty_status', store=True)
    
    days_left = fields.Integer(string='Days Left', related='warranty_id.days_left', readonly=True)
    under_warranty = fields.Boolean(string='Under Warranty', compute='_compute_warranty_status', store=True)
    lot_id = fields.Many2one('stock.lot', string='Chassis Number')  # Assuming lot_id is your chassis number
    warranty_number = fields.Char(string='Warranty Number', related='warranty_id.name', readonly=True)  # Adjust 'name' if the warranty number is stored in another field

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        """Update warranty and related fields when chassis number is selected."""
        for record in self:
            if record.lot_id:
                # Fetch warranty using the chassis number
                warranty = self.env['product.warranty'].search([
                    ('chassis_number_id', '=', record.lot_id.name)  # Ensure this is the correct field
                ], limit=1)

                # If a warranty is found, update the warranty_id and other fields
                if warranty:
                    record.warranty_id = warranty.id
                    record.warranty_status = 'active' if warranty.days_left > 0 else 'expired'
                    record.under_warranty = warranty.days_left > 0
                else:
                    # Reset fields if no warranty is found
                    record.warranty_id = False
                    record.warranty_status = 'no_warranty'
                    record.under_warranty = False
            else:
                # Reset fields if no lot_id is selected
                record.warranty_id = False
                record.warranty_status = 'no_warranty'
                record.under_warranty = False

    @api.depends('warranty_id')
    def _compute_warranty_status(self):
        for record in self:
            if record.warranty_id:
                record.warranty_status = 'active' if record.warranty_id.days_left > 0 else 'expired'
                record.under_warranty = record.warranty_id.days_left > 0
            else:
                record.warranty_status = 'no_warranty'
                record.under_warranty = False

    @api.model
    def create(self, vals):
        """Override create method to check warranty status on record creation."""
        record = super(RepairOrder, self).create(vals)
        if 'lot_id' in vals:
            record._update_warranty_fields()
        return record

    def write(self, vals):
        """Override write method to check warranty status on record modification."""
        result = super(RepairOrder, self).write(vals)
        if 'lot_id' in vals:
            self._update_warranty_fields()
        return result

    def _update_warranty_fields(self):
        """Update warranty-related fields based on the current lot_id."""
        for record in self:
            if record.lot_id:
                # Fetch warranty using the chassis number
                warranty = self.env['product.warranty'].search([
                    ('chassis_number_id', '=', record.lot_id.name)  # Ensure this is the correct field
                ], limit=1)

                # If a warranty is found, update the warranty_id and other fields
                if warranty:
                    record.warranty_id = warranty.id
                    record.warranty_status = 'active' if warranty.days_left > 0 else 'expired'
                    record.under_warranty = warranty.days_left > 0
                else:
                    # Reset fields if no warranty is found
                    record.warranty_id = False
                    record.warranty_status = 'no_warranty'
                    record.under_warranty = False
            else:
                # Reset fields if no lot_id is selected
                record.warranty_id = False
                record.warranty_status = 'no_warranty'
                record.under_warranty = False
