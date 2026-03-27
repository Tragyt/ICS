#!/bin/bash

set -a
source /home/aces/ziti/.env
set +a

ziti edge login https://"${ZITI_CTRL_EDGE_ADVERTISED_ADDRESS}":"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

ziti edge create identity "${IDENTITY}" -o /opt/openziti/etc/identities/"${IDENTITY}".jwt


if [ "$TYPE" == "host" ]; then  

    ziti edge update identity "${IDENTITY}" --role-attributes "login_client"

    if ! ziti edge list configs | grep -q "plc${PLC}hostconf"; then
        ziti edge create config "plc${PLC}hostconf" host.v1 '{"protocol":"tcp", "address":"127.0.0.1", "port":502}'
    fi

    if ! ziti edge list configs | grep -q "plc${PLC}intconf"; then
        ziti edge create config "plc${PLC}intconf" intercept.v1 "{\"protocols\": [\"tcp\"], \"addresses\": [\"plc${PLC}.ziti\"], \"portRanges\": [{\"low\": 502, \"high\": 502}]}"
    fi

    if ! ziti edge list services | grep -q "plc${PLC}modbustcp"; then
        ziti edge create service "plc${PLC}modbustcp" -c "plc${PLC}intconf","plc${PLC}hostconf"
    fi

    if ! ziti edge list service-policies | grep -q "plc${PLC}modbustcp.bind"; then
        ziti edge create service-policy "plc${PLC}modbustcp.bind" Bind --service-roles "@plc${PLC}modbustcp" --identity-roles "@${IDENTITY}"
    fi

fi

if [ "$TYPE" == "client" ]; then  

    ziti edge update identity "${IDENTITY}" --role-attributes "plc${PLC}_client"

    while ! ziti edge list services | grep -q "plc${PLC}modbustcp"; do
        sleep 1
    done

    if ! ziti edge list service-policies | grep -q "plc${PLC}modbustcp.dial"; then

        ziti edge create service-policy "plc${PLC}modbustcp.dial" Dial --service-roles "@plc${PLC}modbustcp" --identity-roles "#plc${PLC}_client"
        
    fi
    
fi

if [ "$TYPE" == "scada" ]; then

    ziti edge update identity "${IDENTITY}" --role-attributes "plc1_client,plc2_client,login_client"

fi