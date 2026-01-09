#!/bin/sh

set -e

until pg_isready -h ziti.db -p 5432 -U "$DATABASE_USER"; do
  sleep 1
done
exec flask run --host=0.0.0.0