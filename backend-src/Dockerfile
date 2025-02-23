FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD uvicorn mainapi:app --host 0.0.0.0 --port ${PORT:-8000}