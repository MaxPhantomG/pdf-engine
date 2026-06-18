import json
import PyPDF2
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Извлекает текст из PDF.
    Возвращает словарь с структурой: {page_number: text}
    """
    pages_data = {}
    
    try:
        with open(file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                pages_data[page_num + 1] = text if text else ""
    
    except Exception as e:
        raise Exception(f"Error extracting PDF: {str(e)}")
    
    return pages_data


def save_extracted_data(extracted_path: str, pages_data: dict):
    """Сохраняет извлеченные данные в JSON"""
    Path(extracted_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(extracted_path, "w", encoding="utf-8") as f:
        json.dump(pages_data, f, ensure_ascii=False, indent=2)


def load_extracted_data(extracted_path: str) -> dict:
    """Загружает извлеченные данные из JSON"""
    try:
        with open(extracted_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

