#!/bin/bash
#Enter GPIO directory
cd /sys/class/gpio
#Export pin IJ -> 35
echo 35 > export
#Enter in GPIO exported folder
cd gpio35
#Set direction
echo in > direction
while true;
do
        path=$(pwd)
        if [ "$path" == "/etc/NetworkManager/system-connections" ];
                then
                        cd /sys/class/gpio/gpio35
        fi
        #Remove button bouncing
        sleep .2
        #Get button logical value
        buttonValue=$(cat value)
        if [ "$buttonValue" == "1" ];
                then
                        #Delete networks
                        #Get access to network manager files
                        rm /etc/NetworkManager/system-connections/*
                        #Reboot network services
                        systemctl restart NetworkManager
	fi
done