# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app
COPY web_app/package*.json ./
RUN npm ci
COPY web_app/ ./

# Explicitly clear API URL so any local .env files don't affect the build
ENV REACT_APP_API_URL=

RUN npm run build

# Stage 2: Final image — Python + nginx + supervisord
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y libpq-dev gcc make nginx supervisor \
    && pip install psycopg2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt Makefile ./
RUN make install

COPY app/ ./

COPY --from=frontend-build /app/build /usr/share/nginx/html

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
