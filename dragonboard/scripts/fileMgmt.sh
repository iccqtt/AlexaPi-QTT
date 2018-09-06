#!/bin/bash
cd /home/linaro/cafeteira/app/app_Web/
#Copy app_Web folder to designed html
cp -r * /var/www/html 
webPath=/var/www/html
#Verify if app_Web was copy successfully
if [ -d "$webPath" ]  
	then
		echo "AppWeb folder moved successfully"
fi
cd /home/linaro/cafeteira/dragonboard/scripts
#Copy scripts to their destination folder
cp .bash_profile hotspot_setup.sh reset_button.sh led_net.sh ~ 
cd ~
echo "Script files moved successfully"