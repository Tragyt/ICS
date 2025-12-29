#!/bin/bash
set -e

/opt/ScadaBR/tomcat/bin/startup.sh

while ! nc -z localhost 8005; do
    echo "waiting tomcat to start..."
    sleep 2
done
echo "tomcat started!"

while [ ! -d "/opt/ScadaBR/tomcat/webapps/ScadaBR/db/scadabrDB" ]; do
    echo "waiting db to exist..."
    sleep 2
done
echo "db exists!"

if [ ! -f "/opt/ScadaBR/tomcat/webapps/ScadaBR/db/scadabrDB/.import_done" ]; then
    /opt/ScadaBR/tomcat/bin/shutdown.sh
    while pgrep -f org.apache.catalina.startup.Bootstrap >/dev/null; do
        echo "waiting server to be down..."
        sleep 2
    done

    ij "/backup/import.del"
    touch "/opt/ScadaBR/tomcat/webapps/ScadaBR/db/scadabrDB/.import_done"
    /opt/ScadaBR/tomcat/bin/startup.sh
fi
echo "import done!"

tail -f /dev/null