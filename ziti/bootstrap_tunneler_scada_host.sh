#!/bin/sh

ziti edge login https://ziti-edge-controller:"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create scada host router'
    ziti edge create edge-router "scada-router-host" \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt
    ziti edge update identity "scada-router-host" \
        --role-attributes scada-host

    ziti edge create config "scada-host-config" host.v1 \
        '{"protocol":"tcp", "address":"0.0.0.0","port":8080}'
    ziti edge create config "scada-host-int-config" intercept.v1 \
        "{\"protocols\":[\"tcp\"],\"addresses\":[\"ziti.scada\"], \"portRanges\":[{\"low\":8080, \"high\":8080}]}"
        
    ziti edge create service "scada-host-service" \
        --configs scada-host-int-config,scada-host-config \
        --role-attributes scada-host-services

    ziti edge create service-policy "scada-host-policy" Bind \
        --service-roles "#scada-host-services" \
        --identity-roles "#scada-host"
    ziti edge create service-policy "scada-host-dial-policy" Dial \
        --service-roles "#scada-host-services" \
        --identity-roles "#nginx"

fi

chown -R "${ZIGGY_UID:-2171}" /ziti-router
echo 'init finished'

