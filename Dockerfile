FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc make\
    && pip install psycopg2

WORKDIR /app

COPY requirements.txt /app/
COPY Makefile /app/
RUN make install

COPY app/. /app/

CMD ["gunicorn", "server.wsgi:application", "--bind", "0.0.0.0:8000"]