from odoo import models, api, exceptions

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            if picking.picking_type_id.code == 'outgoing':
                for move in picking.move_lines:
                    if move.product_id.qty_available < move.quantity_done:
                        raise exceptions.UserError("Product Quantity not available")
        return super(StockPicking, self).button_validate()