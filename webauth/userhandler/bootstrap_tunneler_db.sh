#!/bin/sh

ziti edge login https://ziti-edge-controller:${ZITI_CTRL_EDGE_ADVERTISED_PORT} \
    --username=${ZITI_USER} \
    --password=${ZITI_PWD} \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create DB router'
    ziti edge create edge-router db-router \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt 

    ziti edge update identity "db-router" \
        --role-attributes db
    ziti edge create config "db-config" host.v1 \
        '{"protocol":"tcp", "address":"127.0.0.1","port":5432}'
    ziti edge create config "userhandler-config" intercept.v1 \
        "{\"protocols\":[\"tcp\"],\"addresses\":[\"ziti.db\"], \"portRanges\":[{\"low\":5432, \"high\":5432}]}"    
        
    ziti edge create service "db-service" \
        --configs userhandler-config,db-config \
        --role-attributes db-services

    ziti edge create service-policy "db-policy" Bind \
        --service-roles "#db-services" \
        --identity-roles "#db"
fi

chown -R ${ZIGGY_UID:-2171} /ziti-router
echo 'init finished'

