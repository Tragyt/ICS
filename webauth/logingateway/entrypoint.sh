#!/bin/sh

set -e

until pg_isready -h db.ziti -p 5432 -U "$DATABASE_USER"; do
  sleep 1
done
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --certfile logingateway.rpi.ics.pem \
    --keyfile logingateway.rpi.ics-key.pem \
    --workers 3 \
    --threads 3 \
    --timeout 120 \
    app:app