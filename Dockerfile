FROM python:3.8

ENV PYTHONUNBUFFERED=1
ENV WEBHOOK_URL=""
ENV TOKEN=""
ENV CHAT_ID=""
ENV WEBHOOK_PORT=5000

RUN mkdir /bot
WORKDIR /bot

COPY requirements.txt /bot/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /bot/

CMD ["python3", "main.py"]
