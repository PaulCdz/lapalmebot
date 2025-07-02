FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
 && pip install --default-timeout=100 -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "bot.py"]
