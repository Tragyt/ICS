#!/bin/bash

if [ ! -f /home/aces/openplc/arm_plc.st ]; then
    echo "plc file missing!"
    exit 1
fi

SQL_SCRIPT="INSERT INTO Programs (Name, Description, File, Date_upload) VALUES ('plc', 'arm plc', 'arm_plc.st', strftime('%s', 'now'));"

cp /home/aces/openplc/arm_plc.st /home/aces/openplc/OpenPLC_v3/webserver/st_files
sqlite3 /home/aces/openplc/OpenPLC_v3/webserver/openplc.db "$SQL_SCRIPT"

/home/aces/openplc/OpenPLC_v3/start_openplc.sh &> /home/aces/openplc/server_logs &