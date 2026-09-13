def make_decision(
    invoice,
    purchase_order,
    validation_result,
    duplicate: bool = False,
) -> dict:
    """
    Make the final invoice processing decision.

    Decision rules:
    - Duplicate invoice -> REJECTED
    - Missing PO -> PENDING REVIEW
    - Vendor mismatch -> REJECTED
    - Currency mismatch -> REJECTED
    - Amount outside tolerance -> PENDING REVIEW
    - Validation passes -> APPROVED
    """

    # Rule 1: Duplicate invoice
    if duplicate:
        return {
            "decision": "REJECTED",
            "reasons": [
                "Duplicate invoice detected."
            ],
        }

    # Rule 2: Missing PO
    if purchase_order is None or not invoice.po_number:
        return {
            "decision": "PENDING REVIEW",
            "reasons": validation_result.get(
                "issues",
                ["Purchase order could not be matched."]
            ),
        }

    # Rule 3: Vendor mismatch
    if not validation_result["checks"]["vendor_match"]:
        return {
            "decision": "REJECTED",
            "reasons": validation_result["issues"],
        }

    # Rule 4: Currency mismatch
    if not validation_result["checks"]["currency_match"]:
        return {
            "decision": "REJECTED",
            "reasons": validation_result["issues"],
        }

    # Rule 5: Amount outside tolerance
    if not validation_result["checks"]["amount_within_tolerance"]:
        return {
            "decision": "PENDING REVIEW",
            "reasons": validation_result["issues"],
        }

    # Rule 6: Everything passed
    return {
        "decision": "APPROVED",
        "reasons": [
            "Invoice passed vendor, currency, purchase order, " 
            "and amount tolerance checks."
        ],
    } 