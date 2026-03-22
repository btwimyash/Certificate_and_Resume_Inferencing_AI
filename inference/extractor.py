# inference/extractor.py

import fitz  # PyMuPDF
from PIL import Image
import base64
import io
import os


SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]
SUPPORTED_PDF_FORMAT = [".pdf"]
MAX_RESUME_PAGES = 10


def load_certificate(file_path: str) -> dict:
    """
    Accepts an image or PDF file path.
    Returns a dict with base64-encoded image data and mime type,
    ready to be sent to Gemini.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in SUPPORTED_IMAGE_FORMATS:
        return _load_image(file_path)

    elif ext in SUPPORTED_PDF_FORMAT:
        return _load_pdf(file_path)

    else:
        raise ValueError(f"Unsupported file format: {ext}. Use JPG, PNG, WEBP or PDF.")


def _load_image(file_path: str) -> dict:
    """
    Loads an image file, converts to RGB, encodes to base64.
    """
    with Image.open(file_path) as img:
        img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        encoded = base64.b64encode(buffer.read()).decode("utf-8")

    return {
        "mime_type": "image/jpeg",
        "data": encoded
    }


def _load_pdf(file_path: str) -> dict:
    """
    Converts the first page of a PDF to an image, then encodes to base64.
    Certificates are almost always a single page — we take page 0.
    """
    pdf = fitz.open(file_path)

    # Render first page at high resolution (2x zoom for clarity)
    page = pdf[0]
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)

    # Convert pixmap to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)

    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    pdf.close()

    return {
        "mime_type": "image/jpeg",
        "data": encoded
    }


def load_resume(file_path: str) -> list:
    """
    Accepts an image or PDF file path.
    Returns a list of base64-encoded image dicts (one per page for PDFs).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in SUPPORTED_IMAGE_FORMATS:
        return [_load_image(file_path)]

    elif ext in SUPPORTED_PDF_FORMAT:
        return _load_pdf_all_pages(file_path)

    else:
        raise ValueError(f"Unsupported file format: {ext}. Use JPG, PNG, WEBP or PDF.")


def _load_pdf_all_pages(file_path: str) -> list:
    """
    Converts all pages of a PDF to base64-encoded JPEG images.
    Capped at MAX_RESUME_PAGES to avoid exceeding Gemini context limits.
    """
    pdf = fitz.open(file_path)
    page_count = len(pdf)

    if page_count > MAX_RESUME_PAGES:
        print(f"  Warning: Resume has {page_count} pages; processing first {MAX_RESUME_PAGES} only.")
        page_count = MAX_RESUME_PAGES

    pages = []
    mat = fitz.Matrix(2.0, 2.0)

    for i in range(page_count):
        page = pdf[i]
        pix  = page.get_pixmap(matrix=mat)
        img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        pages.append({"mime_type": "image/jpeg", "data": encoded})

    pdf.close()
    return pages