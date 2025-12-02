# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder
WORKDIR /tmp/build
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip wheel --wheel-dir=/tmp/wheels -r requirements.txt

FROM python:3.12-slim
ENV TZ=UTC
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /tmp/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/* \
    && rm -rf /tmp/wheels
COPY . /app
RUN chmod +x /app/entrypoint.sh
VOLUME ["/data", "/cron", "/etc/cron.d"]
EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
