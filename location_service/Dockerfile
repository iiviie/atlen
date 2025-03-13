FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory contents into /app/app/
COPY ./app /app/app

# Make sure Python can find the modules
ENV PYTHONPATH=/app

# Add a small delay to allow Kafka to start
CMD ["sh", "-c", "sleep 15 && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
