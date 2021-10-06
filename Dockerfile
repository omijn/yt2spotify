FROM python:3.9.7-alpine3.14

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "application.py"]
