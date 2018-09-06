import requests
import AlexaService
import time
import os 

def connection_check():
    try:
        print "[checking_connection]: Checking internet connection - Hello world plain text."
        #requests.get("https://raw.githubusercontent.com/leachim6/hello-world/master/t/plain-text.txt", timeout=1)
        response = os.system("ping -q -c 2 216.58.222.110")
        if response == 0:
            AlexaService.internet_is_up()
            return True
        else:
            AlexaService.internet_is_down()
            return False   
    except Exception, e:
        AlexaService.internet_is_down()
        return False 