from src.extraction.invoice_extractor import extract_invoice
from src.matching.po_matcher import find_purchase_order
from src.validation.validator import validate_invoice_against_po
from src.decision.decision_engine import make_decision
from src.storage.database import (
    initialize_database,
    is_duplicate_invoice,
    save_processed_invoice,
)


def process_invoice(pdf_path: str):
    """Run the complete InvoiceIQ invoice processing workflow."""

    # Step 1: Initialize database
    initialize_database()

    # Step 2: Extract invoice data
    invoice = extract_invoice(pdf_path)

    # Step 3: Check for duplicate invoice
    duplicate = is_duplicate_invoice(
        invoice.vendor,
        invoice.invoice_number,
    )

    if duplicate:
        return {
            "invoice": invoice.model_dump(),
            "po": None,
            "validation": None,
            "duplicate": True,
            "decision": "REJECTED",
            "reasons": [
                "Duplicate invoice detected: this vendor and invoice number were already processed."
            ],
        }

    # Step 4: Find matching purchase order
    po = find_purchase_order(invoice.po_number)

    # Step 5: Validate invoice against purchase order
    validation = validate_invoice_against_po(
        invoice,
        po,
    )

    # Step 6: Make final decision
    result = make_decision(
        invoice,
        po,
        validation,
    )

    # Step 7: Save processed invoice
    save_processed_invoice(
        vendor=invoice.vendor,
        invoice_number=invoice.invoice_number,
        invoice_date=str(invoice.invoice_date),
        total=invoice.total,
        decision=result["decision"],
    )

    # Step 8: Return complete processing result
    return {
        "invoice": invoice.model_dump(),
        "po": po,
        "validation": validation,
        "duplicate": False,
        "decision": result["decision"],
        "reasons": result["reasons"],
    } 