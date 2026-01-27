#!/bin/sh

ziti edge login https://ziti-edge-controller:"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create scada router'
    ziti edge create edge-router "scada-router" \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt
    ziti edge update identity "scada-router" \
        --role-attributes scada
fi

chown -R "${ZIGGY_UID:-2171}" /ziti-router
echo 'init finished'

