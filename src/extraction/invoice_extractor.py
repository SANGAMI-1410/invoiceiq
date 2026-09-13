from datetime import date
import re

from pydantic import BaseModel

from src.extraction.pdf_extractor import extract_text_from_pdf
from src.extraction.ocr_extractor import extract_text_with_ocr


class InvoiceData(BaseModel):
    vendor: str
    invoice_number: str
    invoice_date: date
    po_number: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float
    currency: str = "INR"


def extract_invoice_data(text: str) -> InvoiceData:
    """
    Convert raw invoice text into structured invoice data.
    """

    def get_value(pattern: str, required: bool = True):
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        if required:
            raise ValueError(
                f"Required invoice field not found: {pattern}"
            )

        return None

    vendor = get_value(r"Vendor:\s*(.+)")
    invoice_number = get_value(r"Invoice Number:\s*(.+)")
    invoice_date = get_value(r"Invoice Date:\s*(.+)")
    po_number = get_value(
        r"PO Number:\s*(.+)",
        required=False
    )

    subtotal_text = get_value(
        r"Subtotal:\s*([\d,.]+)",
        required=False
    )

    tax_text = get_value(
        r"Tax:\s*([\d,.]+)",
        required=False
    )

    total_text = get_value(
        r"(?m)^Total:\s*([\d,.]+)",
        required=True
    )

    currency = get_value(
        r"Currency:\s*(.+)",
        required=False
    ) or "INR"

    def parse_amount(value):
        if value is None:
            return None

        return float(value.replace(",", ""))

    return InvoiceData(
        vendor=vendor,
        invoice_number=invoice_number,
        invoice_date=date.fromisoformat(invoice_date),
        po_number=po_number,
        subtotal=parse_amount(subtotal_text),
        tax=parse_amount(tax_text),
        total=parse_amount(total_text),
        currency=currency,
    )


def extract_invoice(pdf_path: str) -> InvoiceData:
    """
    Extract a PDF invoice and return structured invoice data.

    First attempts normal PDF text extraction.
    If the PDF contains no usable text, falls back to OCR.
    """

    # First try normal PDF text extraction
    text = extract_text_from_pdf(pdf_path)

    # If no usable text was found, use OCR
    if not text or not text.strip():
        text = extract_text_with_ocr(pdf_path)

    # Convert extracted text into structured invoice data
    return extract_invoice_data(text) 