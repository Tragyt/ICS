#!/bin/sh

ziti edge login https://ziti-edge-controller:${ZITI_CTRL_EDGE_ADVERTISED_PORT} \
    --username=${ZITI_USER} \
    --password=${ZITI_PWD} \
    --yes 

if [ ! -f /ziti-router/enroll.jwt ]; then
    echo 'Create PLC router'
    ziti edge create edge-router plc-router${PLC} \
        --tunneler-enabled \
        --jwt-output-file /ziti-router/enroll.jwt 

    ziti edge update identity "plc-router${PLC}" \
        --role-attributes plc${PLC}

    ziti edge create config "plc-config${PLC}" host.v1 \
        '{"protocol":"tcp", "address":"127.0.0.1","port":502}'
    ziti edge create config "hil-config${PLC}" intercept.v1 \
        "{\"protocols\":[\"tcp\"],\"addresses\":[\"ziti.plc${PLC}\"], \"portRanges\":[{\"low\":502, \"high\":502}]}"
        
    ziti edge create service "plc-service${PLC}" \
        --configs hil-config${PLC},plc-config${PLC} \
        --role-attributes plc-services${PLC}

    ziti edge create service-policy "plc-policy${PLC}" Bind \
        --service-roles "#plc-services${PLC}" \
        --identity-roles "#plc${PLC}"
    ziti edge create service-policy "scada-policy${PLC}" Dial \
        --service-roles "#plc-services${PLC}" \
        --identity-roles "#scada"


    ziti edge create config "plc-webserver-config${PLC}" host.v1 \
        '{"protocol":"tcp", "address":"127.0.0.1","port":8080}'
    ziti edge create config "webserver-client-config${PLC}" intercept.v1 \
        "{\"protocols\":[\"tcp\"],\"addresses\":[\"ziti.plc${PLC}.webserver\"], \"portRanges\":[{\"low\":8080, \"high\":8080}]}"

    ziti edge create service "plc-webserver-service${PLC}" \
        --configs plc-webserver-config${PLC},webserver-client-config${PLC} \
        --role-attributes plc-webserver-services${PLC}

    ziti edge create service-policy "plc-webserver-policy${PLC}" Bind \
        --service-roles "plc-webserver-services${PLC}" \
        --identity-roles "#plc${PLC}"
    ziti edge create service-policy "webserver-client-policy${PLC}" Dial \
        --service-roles "plc-webserver-services${PLC}" \
        --identity-roles "#logingateway"
fi

chown -R ${ZIGGY_UID:-2171} /ziti-router
echo 'init finished'

