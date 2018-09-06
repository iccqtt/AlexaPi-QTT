import pygatt
import logging
from pygatt.util import uuid16_to_uuid
from pygatt.exceptions import NotConnectedError, NotificationTimeout
import binascii
from symbol import argument

CF_CONTROL_POINT_TURN_OFF = 0x00
CF_CONTROL_POINT_TURN_ON = 0x01
CF_CONTROL_POINT_SHORT_COFFEE = 0x02
CF_CONTROL_POINT_LONG_COFFEE = 0x03
CF_CONTROL_POINT_LEVEL_WATER = 0x04
CF_CONTROL_POINT_LEVEL_COFFEE = 0x05
CF_CONTROL_POINT_GLASS_POSITION = 0x06

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

"""
@param handle: indicate the handle from a characteristic
@param measure: value received from notification  
"""
def callback(handle, measure):
    if handle == 11: 
        print("Heart rate service received: ")
        
        
        for i in range(len(measure)):
            print str(measure[i])
        
    elif handle == 19:
        print("Battery service received: ")
        for i in range(len(measure)):
            print str(measure[i])
    
adapter = pygatt.GATTToolBackend()
adapter.start()

try:
    """ connect to bluetooth MAC addres with 10 seconds timeout"""
    device = adapter.connect('00:02:5B:00:15:10', 10)
    print(device)
    
    """ generate characteristics uuid's  """
    uuid_heart_service = uuid16_to_uuid(0x2A37)
    uuid_battery_service = uuid16_to_uuid(0x2A19)
    uuid_set_sensor_location = uuid16_to_uuid(0x2A39)
    uuid_get_sensor_location = uuid16_to_uuid(0x2A38)
    
    """ discover all characteristics uuid's"""
    device.discover_characteristics()
    
    
    """subscribe(self, uuid, callback=None, indication=False):
        
    Enable notifications or indications for a characteristic and register a
    callback function to be called whenever a new value arrives.

    @param: uuid -- UUID as a string of the characteristic to subscribe.
    @param callback -- function to be called when a notification/indication is
                received on this characteristic.
    @param indication -- use indications (where each notificaiton is ACKd). This is
                more reliable, but slower. 
    
    """
    
    device.subscribe(uuid_heart_service, callback, False)
    device.subscribe(uuid_battery_service, callback, False)
    
    """
    To send a message use function char_write(self, uuid, value, wait_for_response=False):
    
    @param uuid - uuid from what service will receive
    @param value - value to send
    @param wait_for_response - if a response from server is expected
    
    e.g
    device.char_write(uuid, value, False)
    """
    
except NotConnectedError:
    print NotConnectedError.message
    
finally:
    while True:
        a = raw_input()
        if a == '0':
            adapter.stop()
            #device.disconnect()
            break
        elif a == '1':
            i = [0x06]
            data = bytearray(i)
            print data[0]
            try:
                device.char_write_handle(16,data, True)
            except NotificationTimeout as e:
                print e
        elif a == '2':
            try:
                val = device.char_read(uuid_get_sensor_location)
                print val[0]
            except NotificationTimeout as e:
                print e
        elif a == '3':
            
            try:
                device.subscribe(uuid_heart_service, callback, False)
                device.subscribe(uuid_battery_service, callback, False)
            except NotConnectedError:
                print NotConnectedError.message
        
        
        
        