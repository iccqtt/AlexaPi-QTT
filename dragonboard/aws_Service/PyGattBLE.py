from __future__ import division
import logging
import ServiceAWS as aws
from pygatt.util import uuid16_to_uuid
from pygatt.exceptions import NotConnectedError
from Utils import connect_ble
from time import sleep
import AlexaService
import globals

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

uuid_heart_service = uuid16_to_uuid(0x2A37)
uuid_battery_service = uuid16_to_uuid(0x2A19)
uuid_set_sensor_location = uuid16_to_uuid(0x2A39)
uuid_get_sensor_location = uuid16_to_uuid(0x2A38)

device = None

cf_control_point_turn_off = 0
cf_control_point_turn_on = 1
cf_control_point_short_coffee = 2
cf_control_point_long_coffee = 3
cf_control_point_level_water = 4
cf_control_point_level_coffee = 5
cf_control_point_glass_position = 6
cf_control_point_update = 7

ON = '1'
OFF = '0'

inUse = 2

MACHINE_IN_USE = "coffee_in_progress"

hasWater = 1
empty = 0

COFFEE_READY = 'coffee_ready'

queue = []

conn = connect_ble()
conn.start()

coffee_machine_status = 0

def getConnection(task):
    aws.sendOnlineCoffeeMachine(0)
    globals.COFFEE_MACHINE_STATUS_FLAG = False
    try:
        global device
        device = conn.connect()
        if device is not None:
            subscribeCharacteristics(device)
            aws.sendOnlineCoffeeMachine(1)
            globals.COFFEE_MACHINE_STATUS_FLAG == True
            if task == "write_char_error":
                aws.sendError("reconnected")
            elif task == "reconnecting":
                aws.sendError("reconnected")
        sleep(0.5)
        return device
    except NotConnectedError:
        print (NotConnectedError.message)
        aws.sendError(task)
        getConnection("connection_error")

def subscribeCharacteristics(device):
    try:
        device.subscribe(uuid_heart_service, messageCSRCallback, False)
        device.subscribe(uuid_battery_service, batteryCallback, False)
    except NotConnectedError:
        print "Erro"
        #print "[PyGattBLE]: Exception -> " + NotConnectedError.message

def write_char(handle, data):
    global coffee_machine_status
    if device == None:
        print("[PyGattBLE][write_char] Error: device is none!")
        getConnection("write_char_error")
        aws.sendOnlineCoffeeMachine(0)
        globals.COFFEE_MACHINE_STATUS_FLAG = False
        #if globals.COFFEE_MACHINE_STATUS_FLAG is True:
        #        AlexaService.coffee_machine_is_down()
        #        globals.COFFEE_MACHINE_STATUS_FLAG = False

    else:
        try:
            device.char_write_handle(handle, data, False)
            aws.sendOnlineCoffeeMachine(1)
            globals.COFFEE_MACHINE_STATUS_FLAG = True
            #if globals.COFFEE_MACHINE_STATUS_FLAG is False:
            #    AlexaService.coffee_machine_is_up()
            #    globals.COFFEE_MACHINE_STATUS_FLAG = True

        except NotConnectedError:
            print "[PyGattBLE][bluetooth]: Error to connect!"

def send_keepalive(handle, data):
    global coffee_machine_status
    if device == None:
        print("[PyGattBLE][send_keep_alive]: Error: device is none!")
        getConnection("connection_error")
        aws.sendOnlineCoffeeMachine(0)
        globals.COFFEE_MACHINE_STATUS_FLAG = False
        #if globals.COFFEE_MACHINE_STATUS_FLAG == True:
        #        AlexaService.coffee_machine_is_down()
        #        globals.COFFEE_MACHINE_STATUS_FLAG = False

    else:
        try:
            global device
            device1 = device
            device = device1
            device.char_write_handle(handle, data, False)
            aws.sendOnlineCoffeeMachine(1)
            globals.COFFEE_MACHINE_STATUS_FLAG = True
            #if globals.COFFEE_MACHINE_STATUS_FLAG == False:
            #    AlexaService.coffee_machine_is_up()
            #    globals.COFFEE_MACHINE_STATUS_FLAG = True

        except NotConnectedError:
            getConnection("connection_error")
            aws.sendOnlineCoffeeMachine(0)
            globals.COFFEE_MACHINE_STATUS_FLAG = False
            #if globals.COFFEE_MACHINE_STATUS_FLAG is True:
            #    AlexaService.coffee_machine_is_down()
            #    globals.COFFEE_MACHINE_STATUS_FLAG = False


def batteryCallback(handle, message):
    if handle == 19:
        print "[PyGattBLE][batteryCallback]: Received battery level. "
        #for i in range(len(message)):
        #    print str(message[i])

        write_char(aws.handle, aws.getByteArray(aws.SEND_UPDATE))
        aws.sendError("reconnected")

def messageCSRCallback(handle, message):
    #print("[messageCSRCallback]: Received commands")
    #for i in range(len(message)):
    #    print str(message[i])

    if len(message) == 2:
        if message[0] == cf_control_point_turn_off:
            aws.sendOnOff(OFF)
            print("[PyGattBLE][messageCSRCallback]: Turn off machine.")
            aws.stopTimeoutOnOff()

        if message[0] == cf_control_point_turn_on:
            aws.sendOnOff(ON)
            print("[PyGattBLE][messageCSRCallback]: Turn on machine.")
            aws.stopTimeoutOnOff()

        if message[0] == cf_control_point_short_coffee:
            print("[PyGattBLE][messageCSRCallback]: Short coffee request.")
            if message[1] == inUse:
                aws.sendShortCoffee(MACHINE_IN_USE)
                aws.stopTimeoutShortCoffee()
            elif message[1] == 1:
                aws.sendShortCoffee(COFFEE_READY)
                aws.coffeeDoing = None
                write_char(aws.handle, aws.getByteArray(aws.SEND_UPDATE))
            elif message[1] == 3:
                aws.stopTimeoutShortCoffee()

        if message[0] == cf_control_point_long_coffee:
            print("[PyGattBLE][messageCSRCallback]: Long coffee request.")
            if message[1] == inUse:
                aws.sendLongCoffee(MACHINE_IN_USE)
                aws.stopTimeoutLongCoffee()
            elif message[1] == 1:
                aws.sendLongCoffee(COFFEE_READY)
                aws.coffeeDoing = None
            elif message[1] == 3:
                aws.stopTimeoutLongCoffee()
        if message[0] == cf_control_point_level_water:
            aws.sendLevelWater(str(message[1]))
            globals.coffeeMachineHasWater = bool(int(message[1]))
            print("Has Water: "+str(bool(int(message[1]))))
            print("[PyGattBLE][messageCSRCallback]: Sending water status.")
            aws.stopTimeoutLevelWater()

        if message[0] == cf_control_point_glass_position:
            aws.sendGlassPostion(str(message[1]))
            globals.coffeeMachineHasGlass = bool(int(message[1]))
            print("Glass position: " +str(bool(int(message[1]))))
            aws.stopTimeoutGlassPostion()
    if len(message) == 3:
        if message[0] == cf_control_point_level_coffee:
            print("[PyGattBLE][messageCSRCallback]: Sending coffee status.")
            global queue
            sleep(1)

            #Converts sensor input to percentage
            # Juntar os valores recebidos da CRS
            res = message[2]*256 + message[1]
            res = res * 340
            res = res / 20000
            res = round(res, 1)

            print "Distancia: " + str(res)

            #Nota: a calibragem funciona fazendo a diferenca do valor maximo de
            #distancia (quando o pote esta vazio) com o valor lido (na variavel res)
            #Para calibrar, esvazie o reservatorio de cafe e veja o valor lido pelo sensor
            percent = (res/8.9)*100
            percent = round(percent)
            percent = 100 - int(percent)
            print "[PyGattBLE][messageCSRCallback]: Percentage read -> " + str(percent)
            if percent < 0:
                write_char(aws.handle, aws.getByteArray(aws.SEND_GET_COFFEE_LEVEL))
                print "[PyGattBLE][messageCSRCallback]: New reading from HC sensor."
            elif percent > 100:
                write_char(aws.handle, aws.getByteArray(aws.SEND_GET_COFFEE_LEVEL))
                print "[PyGattBLE][messageCSRCallback]: New reading from HC sensor."

            globals.coffeeMachineCoffeeLevel = int(percent)
            print("Coffee Level: "+str(int(percent)))
            aws.sendCoffeelevel(int(percent))
            aws.stopTimeoutLevelCoffee()


    if len(message) == 4:
        print("[PyGattBLE][messageCSRCallback]: Sending all sensor update.")
        aws.sendUpdate(message)
        aws.stopTimeout()
        
