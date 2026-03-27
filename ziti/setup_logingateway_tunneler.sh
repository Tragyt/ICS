#!/bin/bash

set -a
source /home/aces/ziti/.env
set +a

ziti edge login https://"${ZITI_CTRL_EDGE_ADVERTISED_ADDRESS}":"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

ziti edge create identity logingateway_tunneler -o /opt/openziti/etc/identities/logingateway_tunneler.jwt
ziti edge update identity logingateway_tunneler --role-attributes "db_client"

ziti edge create config "logingatewayhostconf" host.v1 '{"protocol":"tcp", "address":"127.0.0.1", "port":5000}'
ziti edge create config "logingatewayintconf" intercept.v1 '{"protocols": ["tcp"], "addresses": ["logingateway.ziti"], "portRanges": [{"low": 5000, "high": 5000}]}'
ziti edge create service "logingateway_service" -c "logingatewayintconf","logingatewayhostconf"
ziti edge create service-policy "logingateway.bind" Bind --service-roles "@logingateway_service" --identity-roles "@logingateway_tunneler"

ziti edge create service-policy "logingateway.dial" Dial --service-roles "@logingateway_service" --identity-roles "#login_client"