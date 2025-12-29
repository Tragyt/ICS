#!/bin/bash

/home/openplc/OpenPLC_v3/start_openplc.sh &> /home/openplc/server_logs &

echo ">> Starting server..."
until nc -z localhost 8080; do
    sleep 1
done

python3 -u /home/openplc/start_plc.py
echo ">> DONE"
touch /tmp/.plc_ready

#pkill -f webserver
tail -f /dev/null