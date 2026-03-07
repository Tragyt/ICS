#!/bin/bash

until nc -z localhost 8080; do
    sleep 1
done

source /home/aces/openplc/venv/bin/activate
python3 -u /home/aces/openplc/start_plc.py
touch /tmp/.plc_ready

# tail -f /dev/null