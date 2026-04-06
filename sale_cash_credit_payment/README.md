# Sale Cash Credit Payment

## Overview

This module extends Odoo 18 Sales to support two sales confirmation flows:

- `Cash`: confirm the sale, create the normal Odoo delivery, create and post the invoice, register payment, and reconcile it automatically.
- `Credit`: confirm the sale, create the normal Odoo delivery, create and post the invoice, but do not register payment.

The module also adds a final confirmation popup so users can review the order before the sales order is confirmed.

## Features

- Adds a required `Sales Type` field on the sales order.
- Shows `Payment Journal` only when the sales type is `Cash`.
- Places the sales payment confirmation section directly below the customer field.
- Opens a final warning popup before confirmation.
- Shows the following information in the popup:
  - Sales Order
  - Customer
  - Total Payable
  - Pricelist
  - Sales Type
  - Payment Journal for cash sales

## Business Flow

### Cash Sale

1. User creates a quotation.
2. User selects customer.
3. User selects `Sales Type = Cash`.
4. User selects the payment journal.
5. User clicks `Confirm`.
6. Odoo shows the final confirmation popup.
7. After approval:
   - the sales order is confirmed,
   - the normal Odoo delivery is created,
   - the customer invoice is created,
   - the invoice is posted,
   - a payment is registered,
   - the invoice is reconciled.

### Credit Sale

1. User creates a quotation.
2. User selects customer.
3. User selects `Sales Type = Credit`.
4. User clicks `Confirm`.
5. Odoo shows the final confirmation popup.
6. After approval:
   - the sales order is confirmed,
   - the normal Odoo delivery is created,
   - the customer invoice is created,
   - the invoice is posted,
   - no payment is registered.

## Validation Rules

- `Sales Type` is required before confirmation.
- `Pricelist` must be set before confirmation.
- `Customer` must be set before confirmation.
- `Payment Journal` is required only when the sales type is `Cash`.
- `Payment Journal` must be a journal of type `Bank` or `Cash`.

## Technical Notes

### Main Files

- `models/sale_order.py`
  - Adds the `Sales Type` and `Payment Journal` fields.
  - Overrides confirmation to open the review popup.
  - Executes the cash or credit flow after final confirmation.

- `models/sale_confirm_warning_wizard.py`
  - Creates the transient review popup shown before confirmation.

- `views/sale_order_views.xml`
  - Adds the sales payment confirmation section to the sales order form.

- `views/sale_confirm_warning_views.xml`
  - Defines the final confirmation popup.

## User Guide

### How to Use

1. Open Sales.
2. Create a quotation.
3. Select the customer.
4. Review the sales payment confirmation section under the customer.
5. Choose the `Sales Type`.
6. If `Cash`, select the payment journal.
7. Click `Confirm`.
8. Review the final popup and confirm again.

## Notes

- For `Cash` sales, invoice creation depends on the order being invoiceable according to Odoo rules.
- If a product uses a delivery-based invoicing policy, Odoo may require delivery progress before invoice creation.

## Workflow Image

See:

- `static/description/sale_cash_credit_payment_workflow.svg`
