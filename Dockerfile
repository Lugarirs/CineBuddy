FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r Agentd/simple_agent/requirements.txt

CMD ["uvicorn", "Agentd.simple_agent.app:app", "--host", "0.0.0.0", "--port", "8080"]