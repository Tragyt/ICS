#!/bin/bash

ij "CONNECT 'jdbc:derby:/opt/ScadaBR/tomcat/webapps/ScadaBR/db/scadabrDB';"

echo "importing tables..."
for file in "/backup/*.del"; do
    ij $file
done
echo "done!"