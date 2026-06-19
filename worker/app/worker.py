from celery import Celery
import os

# Загружаем настройки из переменных окружения или файла конфигурации
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Инициализация Celery
celery_app = Celery('worker', broker=redis_url, backend=redis_url)

# Настраиваем Celery (можно добавить дополнительные параметры)
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = 3600  # 1 час

# Импорт задач, чтобы Celery их зарегистрировал
import app.tasks

# Объект, который команда запуска использует
app = celery_app