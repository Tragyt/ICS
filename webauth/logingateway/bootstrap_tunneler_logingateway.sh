#!/bin/sh

ziti edge login https://ziti-edge-controller:${ZITI_CTRL_EDGE_ADVERTISED_PORT} \
    --username=${ZITI_USER} \
    --password=${ZITI_PWD} \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create logingateway router'
    ziti edge create edge-router "logingateway-router" \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt
    ziti edge update identity "logingateway-router" \
        --role-attributes logingateway

    ziti edge create service-policy "logingateway-policy" Dial \
        --service-roles "#db-services" \
        --identity-roles "#logingateway"
fi

chown -R ${ZIGGY_UID:-2171} /ziti-router
echo 'init finished'

