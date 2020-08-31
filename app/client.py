import socketio
import json
import sys
import requests
from app.sensors import dht11
from utils.json_util import DateTimeEncoder
from utils.led_strip_controller import led_strip_controller as controller


# Flag to control the sensor reading background task
reading_flag = True

# URL to turn on smart-switch
SMARTSWITCH_ON = '/control?cmd=GPIO,12,1'
# URL to turn off smart-switch
SMARTSWITCH_OFF = '/control?cmd=GPIO,12,0'

# Global led_strip_controller object
oLED_CONTROLLER = list()
oLED_CONTROLLER_dict = dict()

# Socketio client object
client = socketio.Client(reconnection_delay=5)

# This event is called when the gateway pi connects to the socketio server
@client.on('connect', namespace='/client-pi')
def connect():
    global reading_flag
    reading_flag = True    
    print('Gateway Pi is connected!')

# This event is called when the gateway pi disconnects to the socketio server
@client.on('disconnect', namespace='/client-pi')
def disconnect():
    global reading_flag
    reading_flag = False
    print('Disconnected!')   

@client.on('loadData', namespace='/client-pi')
def loadValues(data):
    parsed = json.loads(data)
    # Load actuator
    for actuator in parsed['arrActuator']:
        if actuator['state']:
            switchOn(actuator)
        if not actuator['state']:
            switchOff(actuator)

    # Load ControllerLed
    for controllerLed in parsed['arrControllerLed']:
        global oLED_CONTROLLER    
        global oLED_CONTROLLER_dict    
        write_flag = True

        # Check if this controller was already loaded before
        for i in oLED_CONTROLLER:
            print('controller id: {}'.format(i.id))
            if controllerLed['id'] == i.id:
                write_flag = False
        
        # Only add to the list if it wasnt already loaded bfore
        if write_flag:            
            # Add to list
            aux = controller(
                controllerLed['id'],
                controllerLed['red'],
                controllerLed['green'],
                controllerLed['blue'],
                controllerLed['state_colorshift'],
                controllerLed['brightness'],
                controllerLed['gpio_red'],
                controllerLed['gpio_green'],
                controllerLed['gpio_blue']
            )
            oLED_CONTROLLER.append(aux)
            # Add reference of controllerLed id to oLED_CONTROLLER position
            oLED_CONTROLLER_dict[controllerLed['id']] = oLED_CONTROLLER.index(aux)

            if controllerLed['state']:                
                oLED_CONTROLLER[oLED_CONTROLLER_dict[controllerLed['id']]].start()
                if controllerLed['state_colorshift']:
                    oLED_CONTROLLER[oLED_CONTROLLER_dict[controllerLed['id']]].start_colorshiftEffect()

# Event to add a controller led to the list
@client.on('addController', namespace='/client-pi')
def addController(data):
    global oLED_CONTROLLER
    global oLED_CONTROLLER_dict
    aux = controller(
        data['id'],
        data['red'],
        data['green'],
        data['blue'],
        data['state_colorshift'],
        data['brightness'],
        data['gpio_red'],
        data['gpio_green'],
        data['gpio_blue']
    )
    oLED_CONTROLLER.append(aux)
    # Add reference of controllerLed id to oLED_CONTROLLER position
    oLED_CONTROLLER_dict[data['id']] = oLED_CONTROLLER.index(aux)

# Acknowledge event used mainly for callbacks
@client.on('response', namespace='/client-pi')
def response(message):
    print(message)

# Receives event to turn on actuator
@client.on('switchOn', namespace='/client-pi')
def switchOn(data):
    try:
        r = requests.get('http://' + data['ip'] + SMARTSWITCH_ON)
        # Confirm it was turned on
        if r.json()['state'] == 1:
            print('Actuator #{} was turned on.'.format(data['id']))
            response = {
                'id' : data['id'],
                'state' : True
            }
            return json.dumps(response)
    except Exception as error:
        print('Error connecting to {} : {}'.format(data['ip'], error))


# Receives event to turn off actuator
@client.on('switchOff', namespace='/client-pi')
def switchOff(data):
    try:
        r = requests.get('http://' + data['ip'] + SMARTSWITCH_OFF)
        # Confirm it was turned off
        if r.json()['state'] == 0:
            print('Actuator #{} was turned off.'.format(data['id']))
            response = {
                'id' : data['id'],
                'state' : False
            }
            return json.dumps(response)
    except Exception as error:
        print('Error connecting to {} : {}'.format(data['ip'], error))

# Receives event to turn on led strip
@client.on('ledOn', namespace='/client-pi')
def ledOn(data):
    # Check if it was turned off
    if not data['state']:
        # Start led controller by it's id
        try:                
            oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].start()
            if data['state_colorshift']:
                oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].start_colorshiftEffect()
            print('Led Strip #{} was turned on.'.format(data['id']))
            data['state'] = True
            return json.dumps(data)     
        except AttributeError as error:
            print('Error: ', error)

# Receives event to turn off led strip
@client.on('ledOff', namespace='/client-pi')
def ledOff(data):
    # Check if it was turned on
    if data['state']:
        # Stop led controller by it's id
        try:                  
            oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].stop()
            print('Led Strip #{} was turned off.'.format(data['id']))
            data['state'] = False
            return json.dumps(data)     
        except AttributeError as error:
            print('Error: ', error)
    
# Receives event to start colorshift
@client.on('startColorshift', namespace='/client-pi')
def startColorshift(data):
    # Check if led is turned on first
    if data['state'] :
        # Check if colorshift is off
        if not data['state_colorshift']:
            try:
                oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].start_colorshiftEffect()
                print('Led Strip #{} started colorshifting.'.format(data['id']))
                data['state_colorshift'] = True
                return json.dumps(data)                     
            except AttributeError as error:
                print('Error: ', error)    
   
# Receives event to stop colorshift
@client.on('stopColorshift', namespace='/client-pi')
def stopColorshift(data):   
    # Check if led is turned on first
    if data['state'] :
        # Check if colorshift is on
        if data['state_colorshift']:
            try:
                oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].stop_colorshiftEffect()
                print('Led Strip #{} stopped colorshifting.'.format(data['id']))
                data['state_colorshift'] = False
                data['red'] = oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].RED_COLOR
                data['green'] = oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].GREEN_COLOR
                data['blue'] = oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].BLUE_COLOR
                return json.dumps(data)                    
            except AttributeError as error:
                print('Error: ', error)      


# Receives event to increase brightness
@client.on('increaseBrightness', namespace='/client-pi')
def increaseBrightness(data):
    # Check if the led is turned on
    if data['state']:
        try:
            oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].updateBrightness(controller.INCREASE_BRIGHTNESS)
            if oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].shifting:
                oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].updateColors()
                print('Led Strip #{} increase brightness. {}'.format(data['id'], oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].brightness))
                data['brightness'] = oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].brightness
                return json.dumps(data)
        except AttributeError as error:
            print('Error: ', error)              
    
# Receives event to decrease brightness
@client.on('decreaseBrightness', namespace='/client-pi')
def decreaseBrightness(data):
    # Check if the led is turned on
    if data['state']:
        try:
            oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].updateBrightness(controller.DECREASE_BRIGHTNESS)
            if not oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].shifting:
                oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].updateColors()
                print('Led Strip #{} decrease brightness. {}'.format(data['id'], oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].brightness))
                data['brightness'] = oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].brightness
                return json.dumps(data)
        except AttributeError as error:
            print('Error: ', error)    

# Receives event to delete Controller Led
@client.on('deleteController', namespace='/client-pi')
def deleteController(data):
    try:
        if data['state']:
            if oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]].stop():
                oLED_CONTROLLER.remove(oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]])
                oLED_CONTROLLER_dict.pop(data['id'])
        else:
            oLED_CONTROLLER.remove(oLED_CONTROLLER[oLED_CONTROLLER_dict[data['id']]])
            oLED_CONTROLLER_dict.pop(data['id'])
    except AttributeError as error:
        print('Error: ', error) 


# Receives event to send sensor data to the server
@client.on('sendData', namespace='/client-pi')
def sendData():
    error, json_data = dht11(14)
    if json_data is not None:
        print('Sending\n', json_data)
        client.emit('receiveData', json.dumps(json_data,cls=DateTimeEncoder), namespace='/client-pi', callback=response)
        json_data.clear()
    else:
        print('Sensor error: ', error)


def start():
    client.connect('https://smart-home-assistant.herokuapp.com', namespaces=['/client-pi'])
    client.wait()