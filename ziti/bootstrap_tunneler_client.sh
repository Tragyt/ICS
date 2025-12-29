#!/bin/sh

echo "{\"protocols\":[\"tcp\"],\"addresses\":[\"ziti.plc${PLC}\"], \"portRanges\":[{\"low\":502, \"high\":502}]}"
ziti edge login https://ziti-edge-controller:${ZITI_CTRL_EDGE_ADVERTISED_PORT} \
    --username=${ZITI_USER} \
    --password=${ZITI_PWD} \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create HIL router'
    ziti edge create edge-router "hil-router${PLC}" \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt
    ziti edge update identity "hil-router${PLC}" \
        --role-attributes hil${PLC}

    ziti edge create service-policy "hil-policy${PLC}" Dial \
        --service-roles "#plc-services${PLC}" \
        --identity-roles "#hil${PLC}"
fi

chown -R ${ZIGGY_UID:-2171} /ziti-router
echo 'init finished'

