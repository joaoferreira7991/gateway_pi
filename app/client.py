import socketio
import json
import requests
from app.sensors import dht11
from utils.json_util import DateTimeEncoder


# URL to wake the heroku web-server
__URL_WAKE = 'https://smart-home-assistant.herokuapp.com/wake'

# Socketio client object
client = socketio.Client(reconnection_delay=5)

@client.event
def connect():
    print('Connected!\nMy session id is ', client.sid)

@client.event
def connect_error():
    print('Connection failed!', client._handle_error)

@client.event
def disconnect():
    print('Disconnected!')    

# Sends json containing the values retrieved from the sensor 
# to the heroku web-server
@client.on('send_data')
def send_data():
    while True:
        error, json_data = dht11(14)
        if json_data is not None:
            print('Sending\n', json_data)
            client.emit('send_data', json.dumps(json_data,cls=DateTimeEncoder))
            json_data.clear()
        else:
            print(error)
        client.sleep(60)

@client.on('response')
def response(message):
    print(message)

#def keep_alive():
#    request = requests.post(url=__URL_WAKE)
#    if 


def start():
    #try:

    #except ConnectionError:
    #    print('Couldn\'t establish a connection to the cloud.')

    client.connect('http://smart-home-assistant.herokuapp.com')

    client.start_background_task(send_data)
    client.wait()