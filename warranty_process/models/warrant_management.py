from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date

class ProductWarranty(models.Model):
    _name = 'product.warranty'
    _description = 'Product Warranty'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STAGE_SELECTION = [
        ('in_warranty', 'In Warranty'),
        ('not_in_warranty', 'Not in Warranty'),
    ]

    APPROVAL_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('validated', 'Validated'),
    ]

    name = fields.Char(string='Warranty Number', required=True, copy=False, readonly=True, default='New')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    sales_order_id = fields.Many2one('sale.order', string='Sales Order', domain="[('partner_id', '=', customer_id)]", required=True)
    delivery_order_id = fields.Many2one('stock.picking', string='Delivery Order', domain="[('sale_id', '=', sales_order_id)]", required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    chassis_number_id = fields.Many2one('stock.lot', string='Chassis Number', domain="[('product_id', '=', product_id)]", required=True)
    registration_date = fields.Date(string='Registration Date', default=fields.Date.today)
    warranty_period = fields.Selection(
        [('6', '6 Months'), ('12', '1 Year'), ('24', '2 Years')],
        string="Warranty Period", required=True
    )
    days_left = fields.Integer(string='Days Left', compute='_compute_days_left', store=True)
    delivery_date = fields.Datetime(string='Delivery Date', related='delivery_order_id.date_done', store=True)
    warranty_stage = fields.Selection(STAGE_SELECTION, string='Warranty Stage', compute='_compute_warranty_stage', store=True)
    approval_state = fields.Selection(APPROVAL_STATE_SELECTION, string="Approval State", default='draft', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('product.warranty') or 'New'
        if 'company_id' not in vals:
            vals['company_id'] = self.env.company.id
        self._validate_warranty_creation(vals)
        return super(ProductWarranty, self).create(vals)

    def write(self, vals):
        if self.approval_state == 'validated' and any(field in vals for field in ['customer_id', 'sales_order_id', 'delivery_order_id', 'product_id', 'chassis_number_id', 'warranty_period']):
            raise ValidationError("You cannot modify validated warranties. Set it back to draft to modify.")
        if 'company_id' not in vals:
            vals['company_id'] = self.env.company.id
        self._validate_warranty_update(vals)
        return super(ProductWarranty, self).write(vals)

    def unlink(self):
        for warranty in self:
            if warranty.approval_state == 'validated':
                raise ValidationError("You cannot delete a validated warranty.")
        return super(ProductWarranty, self).unlink()

    def _validate_warranty_creation(self, vals):
        if vals.get('delivery_order_id'):
            delivery_order = self.env['stock.picking'].browse(vals.get('delivery_order_id'))
            delivery_date = delivery_order.date_done
            if not delivery_date:
                raise ValidationError("The delivery order has not been completed yet.")
            delivery_date = delivery_date.date()
            registration_date = fields.Date.from_string(vals.get('registration_date', fields.Date.today))
            if registration_date > delivery_date + timedelta(days=90):
                raise ValidationError("Warranty registration must be done within 90 days of the delivery date.")

    def _validate_warranty_update(self, vals):
        if vals.get('delivery_order_id'):
            delivery_order = self.env['stock.picking'].browse(vals.get('delivery_order_id'))
            delivery_date = delivery_order.date_done
            if not delivery_date:
                raise ValidationError("The delivery order has not been completed yet.")
            delivery_date = delivery_date.date()
            registration_date = fields.Date.from_string(vals.get('registration_date', self.registration_date))
            if registration_date > delivery_date + timedelta(days=90):
                raise ValidationError("Warranty registration must be done within 90 days of the delivery date.")

    @api.depends('registration_date', 'warranty_period')
    def _compute_days_left(self):
        for warranty in self:
            if warranty.registration_date:
                expiry_date = warranty.registration_date + timedelta(days=int(warranty.warranty_period) * 30)
                days_remaining = (expiry_date - date.today()).days
                warranty.days_left = max(days_remaining, 0)
            else:
                warranty.days_left = 0

    @api.depends('registration_date', 'warranty_period')
    def _compute_warranty_stage(self):
        for warranty in self:
            if warranty.registration_date:
                end_date = warranty.registration_date + timedelta(days=int(warranty.warranty_period) * 30)
                warranty.warranty_stage = 'in_warranty' if date.today() <= end_date else 'not_in_warranty'
            else:
                warranty.warranty_stage = 'not_in_warranty'

    def action_validate(self):
        for warranty in self:
            warranty.approval_state = 'validated'
            warranty.state = 'validated'

    def action_set_to_draft(self):
        for warranty in self:
            warranty.approval_state = 'draft'
            warranty.state = 'draft'

    def update_warranty_days_left(self):
        warranties = self.search([('days_left', '>', 0)])
        for warranty in warranties:
            warranty._compute_days_left()

    @api.constrains('chassis_number_id')
    def _check_duplicate_chassis_number(self):
        for warranty in self:
            if warranty.chassis_number_id:
                existing_warranty = self.search([
                    ('id', '!=', warranty.id),
                    ('chassis_number_id', '=', warranty.chassis_number_id.id),
                ])
                if existing_warranty:
                    raise ValidationError("The chassis number entered has already been registered.")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProductWarranty, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = self.browse(self.env.context.get('active_id'))
            if doc and doc.state == 'validated':
                doc_arch = res['arch']
                doc_arch = doc_arch.replace('<form', '<form readonly="1"')
                res['arch'] = doc_arch
        return res
