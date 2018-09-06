# importing the requests library
import requests
import json
import time
import os
import AlexaService
import PyGattBLE as gatt
from threading import Thread
from requests.adapters import HTTPAdapter
import ServiceAWS as aws
import netifaces as ni

#Bottle server endpoint
from bottle import route, run, template, debug, response, hook

# Importing global variables
import globals

# defining the api-endpoint
API_ENDPOINT_COFFEE_MACHINE = 'https://7r9s368i06.execute-api.us-west-2.amazonaws.com/prod/status'
header = {'Content-Type': 'application/json'}
API_ENDPOINT_SMART_LAMP = 'https://jc46hyfmwh.execute-api.us-west-2.amazonaws.com/dev/status'
lampOnline = '0'
# defining topics service AWS
COFFEE_LONG = 'qualcomm/CoffeeMachine/LongCoffee/Android'
COFFEE_SHORT = 'qualcomm/CoffeeMachine/ShortCoffee/Android'
TURN_ON = 'qualcomm/CoffeeMachine/TurnOnOff/Android'

# Bottle webserver setup ==============================================================================


# Enable CORS
@hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@route('/coffeeStatus', method=['OPTIONS', 'GET'])
def coffeeMachineStatus():

    payload = {
        "request": {
            "on_off": globals.coffeeMachineIsOn,
            "water": globals.coffeeMachineHasWater,
            "glass": globals.coffeeMachineHasGlass,
            "coffeelevel": globals.coffeeMachineCoffeeLevel,
            "isWorking": globals.coffeeMachineIsWorking
        }
    }
    payload_return = json.dumps(payload)
    return payload_return


@route('/coffeeShort', method=['OPTIONS', 'GET'])
def coffeeShortWeb():
    machineStatus = checkCoffeeMachineState()
    if(machineStatus == "OK"):
        # O cafe curto demora 8 segundos
        # thr = Thread(target=triggerTimeout, args=([10]))
        # thr.start()
        aws.makeShortCoffee()
        return "OK"
    return machineStatus


@route('/coffeeLong', method=['OPTIONS', 'GET'])
def coffeeLongWeb():
    machineStatus = checkCoffeeMachineState()
    if(machineStatus == "OK"):
        # O cafe longo demora 16 segundos
        # thr = Thread(target=triggerTimeout, args=([18]))
        # thr.start()
        # function to publish on topic sync android through MQTT
        aws.makeLongCoffee()
        return "OK"
    return machineStatus


@route('/turnOff', method=['OPTIONS', 'GET'])
def coffeeOffWeb():
    globals.coffeeMachineIsOn = False
    if(globals.coffeeMachineIsOnline):
        # gatt.write_char(16, getByteArray(0x00))
        # function to publish on topic sync android through MQTT
        aws.turnOffWeb()
        return "OK"


@route('/turnOn', method=['OPTIONS', 'GET'])
def coffeeOnWeb():
    globals.coffeeMachineIsOn = True
    if(globals.coffeeMachineIsOnline):
        # gatt.write_char(16, getByteArray(0x01))
        # function to publish on topic sync android through MQTT
        aws.turnOnWeb()
        return "OK"


def initializeServer():
    debug(True)
    ni.ifaddresses('wlan0')
    ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    ip = str(ip)
    thr = Thread(target=run, kwargs={'host': ip, 'port': 5000})
    thr.daemon = True
    thr.start()
    print("[ServiceHTTP][initializeServer] Servidor inicializado!")


# Returns "OK" if machine can make coffee
def checkCoffeeMachineState():
    if(not globals.coffeeMachineIsOnline):
        return "IsOffline"
    if(not globals.coffeeMachineHasWater):
        return "NoWater"
    if(not globals.coffeeMachineIsOn):
        return "IsOff"
    if(not globals.coffeeMachineHasGlass):
        return "NoGlass"
    if(globals.coffeeMachineCoffeeLevel < 15):
        return "NoCoffee"
    if(globals.coffeeMachineIsWorking):
        return "Busy"
    return "OK"


# Coffee machine handlers ============================================================================
def updateStatus(message):
    payload = {
        "request": {
            "type": "UPDATE",
            "on_off": message[1],
            "water": message[2],
            "glass": message[3],
        }
    }

    # sending post request and saving response as response object
    payload_post = json.dumps(payload)
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, payload_post))
    thr.start()


def sendGlassPosition(position):
    payload = {
        "request": {
            "type": "GLASS",
            "glass": position
        }
    }

    # sending post request and saving response as response object
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload)))
    thr.start()
    # print r.text


def sendLevelWater(level):
    payload = {
        "request": {
            "type": "WATER",
            "water": level
        }
    }

    # sending post request and saving response as response object
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload)))
    thr.start()
    # print r.text


def sendCoffeelevel(level):
    payload = {
        "request": {
            "type": "COFFEE",
            "coffee": level
        }
    }
    # sending post request and saving response as response object
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload)))
    thr.start()


def sendBusyStatus(status):
    print("HAS TRIGGERED BUSY STATUS FROM THREAD! :D >>>>>>>>>>>>>> "+str(status))
    payload = {
        "request": {
            "type": "BUSY",
            "busy": int(status)
        }
    }
    # sending post request and saving response as response object
    doPostRequest(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload))
    # thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload)))
    # thr.start()


def sendOnOff(status):
    payload = {
        "request": {
            "type": "ON_OFF",
            "on_off": status
        }
    }

    # sending post request and saving response as response object
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload)))
    thr.start()


def sendOnlineStatus(status):
    globals.coffeeMachineIsOnline = bool(status)
    payload = {
        "request": {
            "type": "ONLINE",
            "onlinestatus": status
        }
    }
    # sending post request and saving response as response object
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_COFFEE_MACHINE, json.dumps(payload)))
    thr.start()

# Ziglamp handlers ===========================================================


def turnLightOn():
    # This is local post request. Since it's unlikely to fail, we'll leave it on this thread
    doPostRequest('http://localhost:3000/turnOn', '')
    print('[ServiceHttp]: Turning on lamp.')


def turnLightOff():
    # This is local post request. Since it's unlikely to fail, we'll leave it on this thread
    doPostRequest('http://localhost:3000/turnOff', '')
    print('[ServiceHttp]: Turning off lamp.')


def send_lamp_status():

    global lampOnline

    try:
        is_online_aux = requests.get('http://localhost:3000/', timeout=1)
        is_online = is_online_aux.content
        print("[ServiceHttp]: Smart Lamp Message: "+str(is_online))

        if is_online == '1':
            print("[ServiceHttp]: Lamp is online.")
            is_online = 1

        else:
            is_online = 0
            print("[ServiceHttp]: Lamp is offline.")

    except requests.exceptions.ReadTimeout:
        is_online = 0
        print("[ServiceHttp]: Lamp is offline - Timeout exception.")

    except requests.exceptions.RequestException:
        is_online = 0
        globals.LAMP_STAND_STATUS_FLAG = False
        print("[ServiceHttp]: Lamp is offline - Exception.")

    finally:
        payload = {
            "request": {
                "type": "STATUS",
                "onlinestatus": is_online
            }
        }
        if(is_online != lampOnline):
            thr = Thread(target=doPostRequest, args=(API_ENDPOINT_SMART_LAMP, json.dumps(payload)))
            thr.start()

            lampOnline = is_online
            if(is_online == 0):
                AlexaService.lamp_stand_is_down()
            else:
                AlexaService.lamp_stand_is_up()
        return is_online


def send_lamp_offline():
    payload = {
        "request": {
            "type": "STATUS",
            "onlinestatus": 0
        }
    }
    thr = Thread(target=doPostRequest, args=(API_ENDPOINT_SMART_LAMP, json.dumps(payload)))
    thr.start()

# Miscellaneous methods ==============================================================


def connection_check():
    try:
        print "[checking_connection]: Checking internet connection - ping."
        response = os.system("ping -q -c 2 216.58.222.110")
        if response == 0:
            if (AlexaService.get_led_state()):
                AlexaService.internet_is_up()
            return True
        else:
            if(not AlexaService.get_led_state()):
                AlexaService.internet_is_down()                
            return False
    except Exception, e:
        if(not AlexaService.get_led_state()):
            AlexaService.internet_is_down()            
        return False


def doPostRequest(endpoint, json):
    try:
        requests.post(endpoint, json, timeout=4)
        requests.post(endpoint, json, timeout=4)
        requests.post(endpoint, json, timeout=4)
    except requests.ConnectionError:
        print('[ServiceHttp]: An error ocurred while doing the POST! - connection error')
    except requests.exceptions.Timeout:
        print('[ServiceHttp]: An error ocurred while doing the POST! - timeout')
    except requests.exceptions.RequestException as ex:
        print('[ServiceHttp]: An error ocurred while doing the POST!')


def getByteArray(message):
    i = [message]
    data = bytearray(i)
    return data
