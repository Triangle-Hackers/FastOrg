FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

# Create a startup script that ensures PORT is an integer
RUN echo '#!/bin/sh\n\
if [ -z "$PORT" ]; then\n\
  PORT=8000\n\
fi\n\
exec uvicorn mainapi:app --host 0.0.0.0 --port $(($PORT))' > /app/start.sh && \
chmod +x /app/start.sh

CMD ["/app/start.sh"]