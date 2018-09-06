#!/bin/bash
#Create a new connection
conName=`nmcli con show | grep 'WirelessNetwork'`
if [ -z "$conName" ];
then
nmcli connection add \
    type wifi \
    ifname wlan0 \
    autoconnect yes \
    con-name WirelessNetwork \
    ssid "Network"
else
    echo "Network config exists, modifying existing one instead!"
fi
#Set connection details
nmcli connection modify WirelessNetwork \
    802-11-wireless.band bg \
    wifi-sec.key-mgmt "$3" \
    wifi-sec.psk "$1" \
    ssid "$2"
#Restart network services and delete AP 
rm /etc/NetworkManager/system-connections/WirelessAP
systemctl restart NetworkManager
nmcli connection up WirelessNetwork
echo "Setup finished."
sleep 10
#Send to lambda ip
IP=$(sudo ifconfig wlan0 | grep "inet" | cut -f2 -d':' | tr -d [a-zA-Z] | grep -v "214" | cut -c10- | cut -d " " -f1-1)
curl -i \
-H "Accept: application/json" \
-H "Content-Type:application/json" \
-X POST --data "{\"request\": {\"type\": \"IP\", \"address\": \"$IP\"}}" "https://62af71awt2.execute-api.us-west-2.amazonaws.com/status/alexa_ip"
sleep 10
poweroff