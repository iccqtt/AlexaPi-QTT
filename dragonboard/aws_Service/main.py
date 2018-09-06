#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PyGattBLE, ServiceAWS
from Utils import Keep_alive
import time
import checking_connection as CheckCon
import AlexaService
import subprocess
import os
import sys
import ServiceHTTP
import globals

def connectAWSIoT():
    try:
        client.connect()
    except Exception, e:
        print('[main][ServiceAWS]: Error connecting to AWS IoT. Retrying...')
        time.sleep(3)
        connectAWSIoT()

if __name__ == "__main__":
    # Inicia as variáveis globais
    globals.init()

    # Inicia o servico de controle do Zigbee na rede local
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/resources/zbserver/server.js'
    #zServer = subprocess.Popen('node '+dir_path, shell=True)
    #print('[main][zServer]: Zigbee server process ID: '+str(zServer.pid))
    #print(os.path.realpath(__file__).rstrip(os.path.basename(__file__))+'alexapi/')

    sys.path.append(os.path.realpath(__file__).rstrip(os.path.basename(__file__))+'alexapi/')
    time.sleep(1)

    # Create Amazon IOT client
    client = ServiceAWS.createClient()
    connectAWSIoT()

    # Inicia o servidor Bottle para report de status de devices
    ServiceHTTP.initializeServer()

    #Subscribe all topics
    ServiceAWS.subscribeTopics(client)

    # Start up AlexaPi service
    AlexaService.setupAlexaService()

    # Notify user about program being ready to work
    AlexaService.readySound()

    #Send initial lamp state
    ServiceAWS.sendOfflineSmartLamp()

    # Connect to CSR bluetooth device
    device = PyGattBLE.getConnection("connection_error")

    if device is None:
        print "[main][PyGattBLE]: Cannot connect to the Coffee Machine."

    alive = Keep_alive()
    alive.start()

    ServiceAWS.updateCallback(None, None, None)

    coffee_online = False
    # Checa se o server Zigbee esta rodando
    while True:
        CheckCon.connection_check()
        print("COFFEE_MACHINE_STATUS_FLAG: "+str(globals.COFFEE_MACHINE_STATUS_FLAG))
        print("COFFEE ONLINE AUX VARIABLE: "+str(coffee_online))
        if(globals.COFFEE_MACHINE_STATUS_FLAG == True) and (coffee_online == False):
            AlexaService.coffee_machine_is_up()
            coffee_online = True
        elif(globals.COFFEE_MACHINE_STATUS_FLAG == False) and (coffee_online == True):
            AlexaService.coffee_machine_is_down()
            coffee_online = False
        time.sleep(15)
        #if(zServer.poll() != None):
            #pass
            #ServiceAWS.sendOnlineSmartLamp()
            #print("[main][zServer]: Zigbee server has crashed! Starting up again...")
            #zServer = subprocess.Popen('node '+dir_path, shell=True)
            #print('[main][zServer]: New Zigbee server process ID: '+str(zServer.pid))
        #ServiceAWS.sendOnlineSmartLamp()
