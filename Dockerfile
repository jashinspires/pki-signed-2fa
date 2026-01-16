# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

ENV TZ=UTC

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && ln -snf /usr/share/zoneinfo/UTC /etc/localtime \
    && echo UTC > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY app ./app
COPY scripts ./scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY student_private.pem ./student_private.pem
COPY student_public.pem ./student_public.pem
COPY instructor_public.pem ./instructor_public.pem

RUN chmod 0644 /etc/cron.d/2fa-cron \
    && crontab /etc/cron.d/2fa-cron \
    && mkdir -p /data /cron \
    && chmod 755 /data /cron

EXPOSE 8080

CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
