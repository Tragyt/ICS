#!/bin/sh
set -e

while [ ! -f "/ziti-router/enroll.jwt" ] && [ ! -f "/ziti-router/config.yml" ]; do
  echo "waiting jwt..."
  sleep 1
done

if [ ! -f "/ziti-router/config.yml" ]; then
  echo "enrollment..."
  ZITI_ENROLL_TOKEN="$(cat /ziti-router/enroll.jwt)"
  export ZITI_ENROLL_TOKEN
else
  unset ZITI_ENROLL_TOKEN
fi

exec /entrypoint.bash "$@"
