FROM python:3.12.10-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 application:application
