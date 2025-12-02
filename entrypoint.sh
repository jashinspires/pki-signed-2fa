#!/bin/sh
set -eu

export TZ=${TZ:-UTC}
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
printf "%s" "$TZ" > /etc/timezone

if [ -d /data/keys ]; then
  for key_file in /data/keys/*; do
    if [ -f "$key_file" ]; then
      chmod 600 "$key_file" 2>/dev/null || true
    fi
  done
fi

if [ -f /app/cron/2fa-cron ]; then
  install -m 0644 /app/cron/2fa-cron /etc/cron.d/2fa-cron
fi

mkdir -p /cron
mkdir -p /data
touch /data/cron.log

cron

exec uvicorn app.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8080}
