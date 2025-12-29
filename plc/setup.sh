#!/bin/bash

if [ ! -f /home/openplc/scripts/arm_plc.st ]; then
    echo "plc file missing!"
    exit 1
fi

SQL_SCRIPT="INSERT INTO Programs (Name, Description, File, Date_upload) VALUES ('plc', 'arm plc', 'arm_plc.st', strftime('%s', 'now'));"

cp /home/openplc/scripts/arm_plc.st /home/openplc/OpenPLC_v3/webserver/st_files
sqlite3 /home/openplc/OpenPLC_v3/webserver/openplc.db "$SQL_SCRIPT"