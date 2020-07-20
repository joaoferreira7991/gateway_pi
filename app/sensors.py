import time
import board
import adafruit_dht
import RPi.GPIO
from datetime import datetime
import requests
import json

'''
Dictionary meant to ease GPIO pin recognition with board module.
'''
DATA_PINS = {
    14 : board.D14,
    23 : board.D23
}

def dht11(data_pin):
    ''' 
    Initializes a dht11 sensor and returns a tuple 
    containing a error message and a dictionary with the extracted data.

    ...

    Parameters
    ----------
    data_pin : int 
        Number of the GPIO pin connected to the raspberry pi.

    Return
    ------
    error : str
        Returns a str containing the error message or None.
    json_data : dict
        Returns a dictionary containing the dht11 extracted 
        values as well as a timestamp or None.
    '''
    dht11 = adafruit_dht.DHT11(DATA_PINS[data_pin])

    try:
        # Gather the values
        temperature_c = float(dht11.temperature)
        humidity = dht11.humidity
        timestamp = datetime.now()
        #print("T{}, H{}, D{}".format(temperature_c, humidity, timestamp))

        # Data to be sent to the API
        json_data = {
            "temperature" : temperature_c,
            "humidity" : humidity,
            "timestamp" : timestamp
        }

        # Invoking deinit() method from PulseIn to deinitialize it
        # thus releasing any hardware and software resources for reuse
        dht11.pulse_in.deinit()
        return None, json_data
    except RuntimeError as error:      
        dht11.pulse_in.deinit()  
        return error, None
