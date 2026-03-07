#!/bin/bash

set -a
source /home/aces/ziti/.env
set +a

ziti edge login https://"${ZITI_CTRL_EDGE_ADVERTISED_ADDRESS}":"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

ziti edge create identity userhandler_tunneler -o /opt/openziti/etc/identities/userhandler_tunneler.jwt
ziti edge update identity userhandler_tunneler --role-attributes "db_client"

while ! ziti edge list services | grep -q "db_service"; do
    sleep 1
done
ziti edge create service-policy "db.dial" Dial --service-roles "@db_service" --identity-roles "#db_client"
