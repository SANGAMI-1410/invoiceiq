import fitz
import pytesseract

from PIL import Image


def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Extract text from a scanned/image-based PDF using OCR.
    """

    document = fitz.open(pdf_path)

    extracted_pages = []

    for page in document:
        # Render PDF page as an image
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples,
        )

        # Run OCR
        text = pytesseract.image_to_string(image)

        extracted_pages.append(text)

    document.close()

    return "\n".join(extracted_pages) 