FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --default-timeout=120 -r requirements.txt

COPY worker/ ./worker/

ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://postgres:example@db:5432/postgres

CMD ["celery", "-A", "worker.app.tasks", "worker", "--loglevel=info"]
