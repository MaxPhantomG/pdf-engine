FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --default-timeout=120 -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://postgres:example@db:5432/postgres

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
