import socketio
import json
import sys
import requests
from app.sensors import dht11
from utils.json_util import DateTimeEncoder
from utils.led_strip_controller import led_strip_controller as controller


# Flag to control the sensor reading background task
reading_flag = True

# URL to wake the heroku web-server
__URL_WAKE = 'https://smart-home-assistant.herokuapp.com/wake'

# URL to turn on smart-switch
SMARTSWITCH_ON = 'http://192.168.1.102/control?cmd=GPIO,12,1'
# URL to turn off smart-switch
SMARTSWITCH_OFF = 'http://192.168.1.102/control?cmd=GPIO,12,0'

# Global led_strip_controller object
oLED_CONTROLLER = controller()

# Socketio client object
client = socketio.Client(reconnection_delay=5)

# This event is called when the gateway pi connects to the socketio server
@client.on('connect', namespace='/client-pi')
def connect():
    global reading_flag
    reading_flag = True    
    print('Connected!\nMy session id is ', client.sid)

# This event is called when the gateway pi disconnects to the socketio server
@client.on('disconnect', namespace='/client-pi')
def disconnect():
    global reading_flag
    reading_flag = False
    print('Disconnected!')   

# Acknowledge event used mainly for callbacks
@client.on('response', namespace='/client-pi')
def response(message):
    print(message)

# Receives event to turn on smart_switch
@client.on('SMART_SWITCH_ON', namespace='/client-pi')
def switchOn():
    requests.get(SMARTSWITCH_ON)

# Receives event to turn off smart_switch
@client.on('SMART_SWITCH_OFF', namespace='/client-pi')
def switchOff():
    requests.get(SMARTSWITCH_OFF)

# Receives event to turn on led strip
@client.on('LED_ON', namespace='/client-pi')
def ledInit():
    # Start led controller
    try:
        # Send request to turn on smart switch
        requests.get(SMARTSWITCH_ON)        
        oLED_CONTROLLER.start()
        print('LED_ON')        
    except AttributeError as error:
        print('Error: ', error)

# Receives event to turn off led strip
@client.on('LED_OFF', namespace='/client-pi')
def ledStop():
    # Stop led controller
    try:
        oLED_CONTROLLER.stop()  
        # Send request to turn off smart switch        
        requests.get(SMARTSWITCH_OFF)
        print('LED_OFF')        
    except AttributeError as error:
        print('Error: ', error)
    
# Receives event to start colorshift
@client.on('START_COLORSHIFT', namespace='/client-pi')
def colorshiftStart():
    try:
        oLED_CONTROLLER.start_colorshiftEffect()
        print('START_COLORSHIFT')         
    except AttributeError as error:
        print('Error: ', error)    
   
# Receives event to stop colorshift
@client.on('STOP_COLORSHIFT', namespace='/client-pi')
def colorshiftStop():
    try:
        oLED_CONTROLLER.stop_colorshiftEffect()
        print('STOP_COLORSHIFT')         
    except AttributeError as error:
        print('Error: ', error)        
  

# Receives event to increase brightness
@client.on('INCREASE_BRIGHTNESS', namespace='/client-pi')
def brightnessIncrease():
    try:
        oLED_CONTROLLER.updateBrightness(oLED_CONTROLLER.INCREASE_BRIGHTNESS)
        if not oLED_CONTROLLER.shifting and not oLED_CONTROLLER.breathing:
            oLED_CONTROLLER.updateColors()
        print('INCREASE_BRIGHTNESS: ', oLED_CONTROLLER.brightness)        
    except AttributeError as error:
        print('Error: ', error)              
    
# Receives event to decrease brightness
@client.on('DECREASE_BRIGHTNESS', namespace='/client-pi')
def brightnessDecrease():
    try:
        oLED_CONTROLLER.updateBrightness(oLED_CONTROLLER.DECREASE_BRIGHTNESS)
        if not oLED_CONTROLLER.shifting and not oLED_CONTROLLER.breathing:
            oLED_CONTROLLER.updateColors()        
        print('DECREASE_BRIGHTNESS: ', oLED_CONTROLLER.brightness)  
    except AttributeError as error:
        print('Error: ', error)


# Sends json containing the values retrieved from the sensor 
# to the heroku web-server
@client.on('send_data', namespace='/client-pi')
def send_data():
    global reading_flag
    while reading_flag:
        error, json_data = dht11(14)
        if json_data is not None:
            print('Sending\n', json_data)
            client.emit('send_data', json.dumps(json_data,cls=DateTimeEncoder), namespace='/client-pi')
            json_data.clear()
        else:
            print(error)
        client.sleep(60)
    if (not reading_flag):
        print('Stopped reading from the sensor.', file=sys.stdout)


def start():
    client.connect('https://smart-home-assistant.herokuapp.com', namespaces=['/client-pi'])

    client.start_background_task(send_data)
    client.wait()