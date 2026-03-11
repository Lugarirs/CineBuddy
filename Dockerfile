FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

EXPOSE 8000

# cd into Agentd so simple_agent package is importable
CMD ["sh", "-c", "cd Agentd && uvicorn simple_agent.app:app --host 0.0.0.0 --port 8000"]