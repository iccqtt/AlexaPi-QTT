#!/bin/bash
#Create a new connection 
conName=`nmcli con show | grep 'WirelessAP'` 
if [ -z "$conName" ];
    then
    nmcli connection add type wifi ifname wlan0 autoconnect no con-name WirelessAP ssid "Network"
    else
        echo "Network config exists, modifying existing one instead!"
fi
#Set connection details
nmcli connection modify WirelessAP ipv4.method shared 802-11-wireless.band bg 802-11-wireless.mode ap wifi-sec.key-mgmt wpa-psk wifi-sec.psk "qualcomm" ssid "Alexa-AP" 