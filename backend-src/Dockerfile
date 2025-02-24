FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Create a shell script to handle the PORT variable
RUN echo '#!/bin/bash\n\
PORT="${PORT:-8000}"\n\
exec uvicorn mainapi:app --host 0.0.0.0 --port "$PORT"' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]