from .worker import app
import pdf_service  # например, сервис обработки PDF
import file_service  # загрузка/сохранение файлов

@app.task
def process_pdf(file_path):
    """
    Задача для обработки PDF файла.
    """
    try:
        extracted_data = pdf_service.extract_text(file_path)
        return {"status": "success", "data": extracted_data}
    except Exception as e:
        # Обработка ошибок
        return {"status": "error", "message": str(e)}