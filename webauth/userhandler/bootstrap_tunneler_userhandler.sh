#!/bin/sh

ziti edge login https://ziti-edge-controller:${ZITI_CTRL_EDGE_ADVERTISED_PORT} \
    --username=${ZITI_USER} \
    --password=${ZITI_PWD} \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create userhandler router'
    ziti edge create edge-router "userhandler-router" \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt
    ziti edge update identity "userhandler-router" \
        --role-attributes userhandler

    ziti edge create service-policy "userhandler-policy" Dial \
        --service-roles "#db-services" \
        --identity-roles "#userhandler"
fi

chown -R ${ZIGGY_UID:-2171} /ziti-router
echo 'init finished'

