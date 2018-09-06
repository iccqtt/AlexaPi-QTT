#!bin/bash
#Setting red LED. 
cd /sys/class/gpio
echo 115 > export
cd /sys/class/gpio/gpio115/
echo out > direction
while [ true ];
do	
    sleep 10
    ping -q -c 2 52.46.129.40
    if [ "$?" != "0" ];
        then
            #Turn on red LED.             
            echo 1 > value                                
        else
            #Turn off red LED.
            echo 0 > value        
    fi   
done