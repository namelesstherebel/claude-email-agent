FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py .
COPY gmail_client.py .
COPY claude_agent.py .
COPY config.py .

# credentials.json and token.json are mounted at runtime (never baked into image)
# .env is loaded via --env-file at runtime

CMD ["python3", "agent.py"]
