FROM python:3.10-slim

WORKDIR /app

# Restante do seu Dockerfile...
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8550
CMD ["python", "main.py"]