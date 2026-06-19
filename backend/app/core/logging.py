import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '../../logs')  # путь к папке logs
os.makedirs(LOG_DIR, exist_ok=True)

# Создаем обработчик логов для общего файла `error.log`
logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)

# Обработчик для ошибок
file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'error.log'))
file_handler.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)