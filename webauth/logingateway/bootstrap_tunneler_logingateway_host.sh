#!/bin/sh

ziti edge login https://ziti-edge-controller:${ZITI_CTRL_EDGE_ADVERTISED_PORT} \
    --username=${ZITI_USER} \
    --password=${ZITI_PWD} \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create logingateway host router'
    ziti edge create edge-router "logingateway-router-host" \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt
    ziti edge update identity "logingateway-router-host" \
        --role-attributes logingateway-host

    ziti edge create config "logingateway-host-config" host.v1 \
        '{"protocol":"tcp", "address":"0.0.0.0","port":5000}'
    ziti edge create config "nginx-config" intercept.v1 \
        "{\"protocols\":[\"tcp\"],\"addresses\":[\"ziti.logingateway\"], \"portRanges\":[{\"low\":5000, \"high\":5000}]}"
        
    ziti edge create service "logingateway-host-service" \
        --configs nginx-config,logingateway-host-config \
        --role-attributes logingateway-host-services

    ziti edge create service-policy "logingateway-host-policy" Bind \
        --service-roles "#logingateway-host-services" \
        --identity-roles "#logingateway-host"
    ziti edge create service-policy "nginx-policy" Dial \
        --service-roles "#logingateway-host-services" \
        --identity-roles "#nginx"

fi

chown -R ${ZIGGY_UID:-2171} /ziti-router
echo 'init finished'

