#!/bin/bash

set -a
source /home/aces/ziti/.env
set +a

ziti edge login https://"${ZITI_CTRL_EDGE_ADVERTISED_ADDRESS}":"${ZITI_CTRL_EDGE_ADVERTISED_PORT}" \
    --username="${ZITI_USER}" \
    --password="${ZITI_PWD}" \
    --yes 

ziti edge create edge-router "ziti-router" \
   --jwt-output-file=/home/aces/ziti/ziti-router.jwt

ziti edge update edge-router ziti-router -a "public"