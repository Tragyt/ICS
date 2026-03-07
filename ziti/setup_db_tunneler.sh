#!/bin/bash

set -a
source /home/aces/ziti/.env
set +a

ziti edge login https://"${ZITI_CTRL_EDGE_ADVERTISED_ADDRESS}":"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

ziti edge create identity db_tunneler -o /opt/openziti/etc/identities/db_tunneler.jwt

ziti edge create config "dbhostconf" host.v1 '{"protocol":"tcp", "address":"127.0.0.1", "port":5432}'
ziti edge create config "dbintconf" intercept.v1 '{"protocols": ["tcp"], "addresses": ["db.ziti"], "portRanges": [{"low": 5432, "high": 5432}]}'
ziti edge create service "db_service" -c "dbintconf","dbhostconf"
ziti edge create service-policy "db.bind" Bind --service-roles "@db_service" --identity-roles "@db_tunneler"