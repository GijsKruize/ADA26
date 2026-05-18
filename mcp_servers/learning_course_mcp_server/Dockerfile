FROM python:3.11-slim

WORKDIR /app

COPY mcp_servers/learning_course_mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_servers/learning_course_mcp_server/server.py /app/server.py
COPY mcp_servers/learning_course_mcp_server/tools.py /app/tools.py

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
