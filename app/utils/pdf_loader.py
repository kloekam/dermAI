from pathlib import Path
from pypdf import PdfReader


def load_pdf_pages(path: str | Path):
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or '').strip()
        if text:
            pages.append({'page_number': i, 'text': text})
    return pages
