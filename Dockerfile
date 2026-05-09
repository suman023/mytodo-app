# Base image
FROM python:3.11-slim

# Container ke andar working folder
WORKDIR /app

# Python packages install karo
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# Saara code copy karo
COPY app/ .

# Port expose karo
EXPOSE 5000

# App start karo
CMD ["python", "app.py"]