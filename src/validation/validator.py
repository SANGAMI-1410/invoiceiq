from typing import Any


def validate_invoice_against_po(
    invoice: Any,
    purchase_order: dict | None,
    tolerance_percent: float = 2.0,
) -> dict:
    """
    Validate an invoice against its purchase order.

    Returns validation results without making the final decision.
    """

    issues = []
    checks = {}

    # No PO found
    if purchase_order is None:
        checks["po_found"] = False

        issues.append(
            "Purchase order could not be matched. "
            "Invoice requires manual review."
        )

        return {
            "valid": False,
            "checks": checks,
            "issues": issues,
        }

    checks["po_found"] = True

    # 1. Vendor check
    vendor_match = (
        invoice.vendor.strip().lower()
        == purchase_order["vendor"].strip().lower()
    )

    checks["vendor_match"] = vendor_match

    if not vendor_match:
        issues.append(
            f"Vendor mismatch: invoice vendor '{invoice.vendor}' "
            f"does not match PO vendor '{purchase_order['vendor']}'."
        )

    # 2. Currency check
    currency_match = (
        invoice.currency.strip().upper()
        == str(purchase_order["currency"]).strip().upper()
    )

    checks["currency_match"] = currency_match

    if not currency_match:
        issues.append(
            f"Currency mismatch: invoice currency '{invoice.currency}' "
            f"does not match PO currency '{purchase_order['currency']}'."
        )

    # 3. Amount check
    invoice_total = float(invoice.total)
    po_total = float(purchase_order["total_amount"])

    difference = abs(invoice_total - po_total)

    tolerance_amount = po_total * (tolerance_percent / 100)

    amount_within_tolerance = difference <= tolerance_amount

    checks["amount_difference"] = difference
    checks["tolerance_amount"] = tolerance_amount
    checks["amount_within_tolerance"] = amount_within_tolerance

    if not amount_within_tolerance:
        issues.append(
            f"Amount mismatch: invoice total is {invoice_total:.2f}, "
            f"PO total is {po_total:.2f}, "
            f"and the difference of {difference:.2f} exceeds the "
            f"{tolerance_percent:.2f}% tolerance."
        )

    return {
        "valid": len(issues) == 0,
        "checks": checks,
        "issues": issues,
    } 