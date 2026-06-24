from typing import List, Tuple
import pdfplumber
import logging

logger = logging.getLogger("pdf_service")

def extract_text_with_pages(file_path: str) -> List[Tuple[int, str]]:
    """
    Возвращает список кортежей: [(page_number, text), ...]
    """
    pages_content: List[Tuple[int, str]] = []
    try:
        with open(file_path, 'rb') as f:
            with pdfplumber.open(f) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_content.append((i, text.strip()))
        return pages_content
    except Exception as e:
        logger.exception(f"Failed to parse PDF {file_path}: {str(e)}")
        raise
        
def extract_text(file_path: str) -> str:
    """
    Возвращает полный текст документа в одной строке
    """
    try:
        with open(file_path, 'rb') as f:
            with pdfplumber.open(f) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        full_text += text.strip() + "\n"
                return full_text.strip()
    except Exception as e:
        logger.exception(f"Failed to extract full text from PDF {file_path}: {str(e)}")
        raise

