#!/bin/sh

set -e

until pg_isready -h "$DATABASE_ADDRESS" -p 5432 -U "$DATABASE_USER"; do
  sleep 1
done
flask db upgrade
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --certfile rpi.userhandler.pem \
    --keyfile rpi.userhandler-key.pem \
    --workers 3 \
    --threads 3 \
    --timeout 120 \
    app:app
