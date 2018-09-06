#for ((i=0; i<32; i++)); do echo \ $i; echo in >/sys/class/gpio/gpio\ $i/direction; echo \ $i >/sys/class/gpio/unexport; done
#!/bin/sh
cd /sys/class/gpio;
echo 36 > unexport;
echo 115 > unexport;