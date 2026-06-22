import pdfplumber
import logging

logger = logging.getLogger("worker_logger")

def extract_text_with_pages(file_path: str):
    """
    Возвращает список кортежей: [(page_number, text), ...]
    """
    pages_content = []
    try:
        with pdfplumber.open(file(file_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    # i + 1, так как страницы в PDF начинаются с 1
                    pages_content.append((i + 1, text.strip()))
        return pages_content
    except Exception as e:
        logger.error(f"Failed to parse PDF {file_path}: {str(e)}")
        raise e
