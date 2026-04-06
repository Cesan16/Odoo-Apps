# -*- coding: utf-8 -*-

from odoo import _, fields, models


class SaleConfirmWarningWizard(models.TransientModel):
    _name = "sale.confirm.warning.wizard"
    _description = "Sale Confirmation Warning"

    sale_order_id = fields.Many2one("sale.order", required=True, readonly=True)
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id",
        string="Customer",
        readonly=True,
    )
    pricelist_id = fields.Many2one(
        related="sale_order_id.pricelist_id",
        string="Pricelist",
        readonly=True,
    )
    sale_payment_type = fields.Selection(
        related="sale_order_id.sale_payment_type",
        string="Sales Type",
        readonly=True,
    )
    cash_payment_journal_id = fields.Many2one(
        related="sale_order_id.cash_payment_journal_id",
        string="Payment Journal",
        readonly=True,
    )
    amount_total = fields.Monetary(
        related="sale_order_id.amount_total",
        string="Total Payable",
        readonly=True,
    )
    currency_id = fields.Many2one(
        related="sale_order_id.currency_id",
        readonly=True,
    )

    def action_confirm_order(self):
        self.ensure_one()
        return self.sale_order_id.with_context(
            skip_sale_confirmation_warning=True
        ).action_confirm()

    def action_cancel(self):
        return {"type": "ir.actions.act_window_close"}
