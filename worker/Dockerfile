FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --default-timeout=120 -r requirements.txt

COPY worker/ ./worker/

ENV PYTHONPATH=/app

CMD ["celery", "-A", "worker.app.tasks", "worker", "--loglevel=info"]
