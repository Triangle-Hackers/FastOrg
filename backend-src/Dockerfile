FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Use a direct shell command to ensure proper variable handling
CMD uvicorn mainapi:app --host 0.0.0.0 --port 8000