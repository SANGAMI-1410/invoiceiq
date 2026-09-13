import pymupdf 


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a machine-readable PDF.

    Args:
        pdf_path: Path to the invoice PDF.

    Returns:
        Extracted text from all PDF pages.
    """
    document = pymupdf.open(pdf_path) 

    pages_text = []

    for page in document:
        text = page.get_text("text")
        if text:
            pages_text.append(text)

    document.close()

    return "\n".join(pages_text).strip() 