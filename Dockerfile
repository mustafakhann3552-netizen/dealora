FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/uploads

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "waitress-serve --host=0.0.0.0 --port=${PORT:-5000} app:app"]
