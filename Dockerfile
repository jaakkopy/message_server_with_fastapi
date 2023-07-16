FROM python:latest
WORKDIR /app
COPY requirements.txt .
COPY server.py .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "5000"]