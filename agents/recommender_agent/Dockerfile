FROM python:3.11-slim

WORKDIR /app

COPY agents/recommender_agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/recommender_agent/app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
