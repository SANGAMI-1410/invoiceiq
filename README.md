# InvoiceIQ — AI-Powered Invoice Processing & Decision Engine

## 1. Overview

InvoiceIQ is an automated Finance/AP invoice processing system that converts an invoice PDF into a clear, explainable business decision.

The workflow is:

**Invoice PDF → Data Extraction → Validation → PO Matching → Duplicate Check → Business Rules → Decision → Explanation**

The final decision can be:

- **APPROVED**
- **PENDING REVIEW**
- **REJECTED**

## 2. Problem

Accounts Payable teams often receive invoices in different PDF formats, including machine-readable and scanned documents.

Manual processing requires teams to:

- Extract invoice information
- Identify the vendor
- Find the purchase order
- Compare invoice and PO amounts
- Validate required fields
- Detect duplicate invoices
- Apply business rules
- Decide whether an invoice should be approved or reviewed

InvoiceIQ automates this workflow while providing an explanation for every decision.

## 3. Solution / Workflow

InvoiceIQ processes each invoice through the following stages:

1. **Invoice Upload** — User uploads an invoice PDF through the Streamlit interface.
2. **Document Processing** — Text is extracted from machine-readable PDFs. OCR is used as a fallback for scanned/image-based PDFs.
3. **Invoice Data Extraction** — Extracts vendor, invoice number, invoice date, PO number, currency, tax, line items, and total amount.
4. **Validation** — Required invoice fields are checked for completeness and validity.
5. **Purchase Order Matching** — The invoice is matched against available purchase-order data.
6. **Duplicate Detection** — Checks whether the same vendor and invoice number have already been processed.
7. **Business Rule Evaluation** — Vendor, currency, amount tolerance, PO, and other validation rules are evaluated.
8. **Decision Engine** — Produces APPROVED, PENDING REVIEW, or REJECTED.
9. **Explanation** — Displays the decision and supporting reasons.

## 4. Key Features

- PDF invoice processing
- OCR fallback for scanned invoices
- Structured invoice data extraction
- Purchase order matching
- Vendor validation
- Currency validation
- Amount tolerance validation
- Duplicate invoice detection
- Explainable decision making
- Processing-stage visibility
- Streamlit user interface
- Realistic operational edge cases

## 5. Decision Logic & Business Rules

InvoiceIQ uses deterministic business rules for the final financial decision.

### Required Fields

The following fields are required:

- Vendor
- Invoice number
- Invoice date
- Total amount

Missing required information can result in **PENDING REVIEW**.

### Purchase Order Matching

The system checks:

- PO existence
- Vendor match
- Currency match
- Invoice amount vs PO amount

### Amount Tolerance

The configured amount tolerance is **±2%**.

If the invoice amount is within the configured tolerance, processing can continue.

If the amount is outside the tolerance:

**PENDING REVIEW**

### Duplicate Detection

Invoices are checked using:

**Vendor + Invoice Number**

If the same invoice has already been processed:

**REJECTED**

### Vendor Mismatch

If the invoice vendor does not match the PO vendor:

**REJECTED**

### Currency Mismatch

If the invoice currency does not match the PO currency:

**REJECTED**

### Missing PO

If the invoice does not contain a usable PO reference:

**PENDING REVIEW**

### Decision Summary

| Condition | Decision |
|---|---|
| All checks pass | APPROVED |
| Missing information / PO / amount outside tolerance | PENDING REVIEW |
| Duplicate invoice | REJECTED |
| Vendor mismatch | REJECTED |
| Currency mismatch | REJECTED |

## 6. Edge Cases

### Missing PO

An invoice without a valid PO reference is sent for manual review.

**Decision: PENDING REVIEW**

### Amount Mismatch

An invoice amount outside the configured PO tolerance is sent for manual review.

**Decision: PENDING REVIEW**

### Duplicate Invoice

A previously processed invoice with the same vendor and invoice number is rejected.

**Decision: REJECTED**

### Vendor Mismatch

An invoice whose vendor differs from the associated PO vendor is rejected.

**Decision: REJECTED**

### Scanned Invoice

For scanned or image-based PDFs, InvoiceIQ uses OCR as a fallback when normal PDF text extraction is insufficient.

## 7. Technology Stack

### Frontend

- Streamlit

### Backend

- Python

### Document Processing

- PyMuPDF
- Tesseract OCR
- Pillow

### Data Validation & Processing

- Pydantic
- pandas

### Storage

- SQLite
- CSV-based purchase-order data

### Configuration

- YAML
- python-dotenv

### Testing

- pytest

## 8. How to Run

### 1. Clone the repository

```bash
git clone https://github.com/SANGAMI-1410/invoiceiq.git
cd invoiceiq 