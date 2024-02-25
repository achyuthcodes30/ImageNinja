FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y openssl

RUN openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/ST=CA/L=SF/O=My Company/OU=Engineering/CN=localhost" -keyout server.key -out server.crt

RUN chmod 666 server.key

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8888

CMD ["python", "server.py"]

