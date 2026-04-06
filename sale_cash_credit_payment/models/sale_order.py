# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_payment_type = fields.Selection(
        selection=[
            ("credit", "Credit"),
            ("cash", "Cash"),
        ],
        string="Sales Type",
        tracking=True,
        required=True,
    )
    cash_payment_journal_id = fields.Many2one(
        "account.journal",
        string="Payment Journal",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        copy=False,
        tracking=True,
    )

    @api.constrains("sale_payment_type", "cash_payment_journal_id")
    def _check_cash_payment_journal_id(self):
        for order in self:
            if order.sale_payment_type != "cash":
                continue
            if not order.cash_payment_journal_id:
                raise ValidationError(_("A payment journal is required for cash sales."))
            if order.cash_payment_journal_id.type not in ("bank", "cash"):
                raise ValidationError(_("The payment journal must be a bank or cash journal."))

    @api.onchange("sale_payment_type")
    def _onchange_sale_payment_type(self):
        if self.sale_payment_type != "cash":
            self.cash_payment_journal_id = False

    def action_confirm(self):
        if self.env.context.get("skip_sale_confirmation_warning"):
            return self._action_confirm_after_warning()
        return self.action_open_confirmation_warning()

    def _action_confirm_after_warning(self):
        cash_orders = self.filtered(lambda order: order.sale_payment_type == "cash")
        credit_orders = self.filtered(lambda order: order.sale_payment_type == "credit")
        self._validate_sale_confirmation_details()
        cash_orders._validate_cash_sale_before_confirm()

        result = super().action_confirm()

        for order in cash_orders:
            order._create_and_reconcile_cash_sale_payment()
        for order in credit_orders:
            order._create_credit_sale_invoice()
        return result

    def action_open_confirmation_warning(self):
        self.ensure_one()
        self._validate_sale_confirmation_details()
        wizard = self.env["sale.confirm.warning.wizard"].create(
            {"sale_order_id": self.id}
        )
        return {
            "name": _("Confirm Sales Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.confirm.warning.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
        }

    def _validate_sale_confirmation_details(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                continue
            if not order.partner_id:
                raise ValidationError(_("Please select a customer before confirming the sales order."))
            if not order.pricelist_id:
                raise ValidationError(_("Please select a pricelist before confirming the sales order."))
            if not order.sale_payment_type:
                raise ValidationError(_("Please select the sales type before confirming the sales order."))

    def _validate_cash_sale_before_confirm(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                continue
            if not order.cash_payment_journal_id:
                raise ValidationError(_("Please select a payment journal for this cash sale."))
            if not order.order_line.filtered(lambda line: not line.display_type):
                raise ValidationError(_("You cannot confirm a cash sale without order lines."))

    def _create_and_reconcile_cash_sale_payment(self):
        self.ensure_one()

        invoices = self._get_or_create_customer_invoices()

        if not invoices:
            raise UserError(
                _(
                    "Odoo could not create an invoice for this cash sale. "
                    "Please check the invoicing policy on the order lines."
                )
            )

        draft_invoices = invoices.filtered(lambda move: move.state == "draft")
        if draft_invoices:
            draft_invoices.action_post()

        for invoice in invoices.filtered(
            lambda move: move.state == "posted"
            and move.payment_state not in ("paid", "in_payment")
            and move.amount_residual > 0
        ):
            payment_method_line = self._get_inbound_payment_method_line()
            payment_register = self.env["account.payment.register"].with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            ).create(
                {
                    "journal_id": self.cash_payment_journal_id.id,
                    "payment_method_line_id": payment_method_line.id,
                    "amount": invoice.amount_residual,
                    "payment_date": fields.Date.context_today(self),
                    "communication": self.name,
                }
            )
            payment_register._create_payments()

    def _create_credit_sale_invoice(self):
        self.ensure_one()
        invoices = self._get_or_create_customer_invoices()
        if invoices:
            draft_invoices = invoices.filtered(lambda move: move.state == "draft")
            if draft_invoices:
                draft_invoices.action_post()

    def _get_or_create_customer_invoices(self):
        self.ensure_one()
        invoices = self.invoice_ids.filtered(
            lambda move: move.move_type == "out_invoice" and move.state != "cancel"
        )
        if not invoices:
            invoices = self._create_invoices()
        return invoices

    def _get_inbound_payment_method_line(self):
        self.ensure_one()
        payment_method_line = self.cash_payment_journal_id.inbound_payment_method_line_ids[:1]
        if not payment_method_line:
            raise UserError(
                _(
                    "The selected journal does not have an inbound payment method configured."
                )
            )
        return payment_method_line
