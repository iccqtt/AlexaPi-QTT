#!/bin/bash
sleep 10
#WiFi power saving off.
iwconfig wlan0 power off
#Calls reset script
bash reset_button.sh &
#Calls LED_NET script
bash led_net.sh &
#Run the node server for Wi-Fi configuration.
cd /home/linaro/cafeteira/wireless_setup
node server.js &
#Internet connection test.
ping -q -c 2 52.46.129.40
if [ "$?" != 0 ];
	then
		#Back to Root
		cd -
		#Setup and run the AP connection. 
		bash hotspot_setup.sh &
		nmcli connection up WirelessAP
		#Setting green LED.
		cd /sys/class/gpio
		echo 36 > export
		cd /sys/class/gpio/gpio36/
		#Internet connection test again.
		ping -c 2 52.46.129.40
		while [ "$?" != "0" ];
		do
			#See if the AP is up.
			conStatus=`nmcli | grep "wlan0: disconnected"`
			if [ -n "$conStatus" ];
				then
					#If not, got up the AP again.
					nmcli connection up WirelessAP
				fi
			#Blink the green LED.
			echo out > direction
			echo 0 > value
			sleep .5
			echo 1 > value
			sleep .5
			#Internet connection test again.
			ping -q -c 1 52.46.129.40
		done
		#Unexport the green LED GPIO.
		echo in > direction
		cd "/sys/class/gpio"
		echo 36 > unexport
fi
# Send ip to lambda
IP=$(sudo ifconfig wlan0 | grep "inet" | cut -f2 -d':' | tr -d [a-zA-Z] | grep -v "214" | cut -c10- | cut -d " " -f1-1)
curl -i \
-H "Accept: application/json" \
-H "Content-Type:application/json" \
-X POST --data "{\"request\": {\"type\": \"IP\", \"address\": \"$IP\"}}" "https://62af71awt2.execute-api.us-west-2.amazonaws.com/status/alexa_ip"
#Start PulseAudio Service
start-pulseaudio-x11
#MAKE SHORT COFFEE
cd /home/linaro/cafeteira/dragonboard/aws_Service
su -c "sudo python main.py" linaro &
echo "ALEXA HAS BOOTED SUCCESSFULLY FROM BASH PROFILE"