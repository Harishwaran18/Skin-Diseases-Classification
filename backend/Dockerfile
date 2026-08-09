FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY ml /app/ml

WORKDIR /app/backend

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 12000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12000"]
