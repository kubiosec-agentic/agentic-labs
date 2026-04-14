FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent_app.py .
COPY custom_logger.py .

EXPOSE 8080

CMD ["python", "agent_app.py"]
