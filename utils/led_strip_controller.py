import os
import pigpio
import time
from _thread import start_new_thread

class led_strip_controller:

    # Brightness rate of change (10% rate)
    BRIGHTNESS_LEVEL = 2.55
    
    # Shifting effect, rate of color change
    STEP = 0.025

    # Increase / Decrease brightness variables
    INCREASE_BRIGHTNESS = 0
    DECREASE_BRIGHTNESS = 1

    def __init__(self, id, red, blue, green, shifting, brightness, gpio_red=17, gpio_green=27, gpio_blue=22):
        
        # Identification number
        self.id = id

        # LED GPIO pin position
        self.RED_PIN = gpio_red
        self.GREEN_PIN = gpio_green
        self.BLUE_PIN = gpio_blue

        # LED color values
        self.RED_COLOR = red
        self.GREEN_COLOR = green
        self.BLUE_COLOR = blue

        # Brightness value (0 to 255)
        self.brightness = brightness

        # Flag to enable/disable shifting
        self.shifting = shifting

        # Flag to enable/disable breathing
        #self.breathing = False

    # Starts a pigpio instance to read and write values from the gpio pins
    def start(self):
        self.pi = pigpio.pi() 
        self.updateColors()
        if self.shifting:
            self.start_colorshiftEffect()
        
    # These update the color rgb values (0 to 255)
    def updateRed(self, color):
        if color < 0:
            color = 0
        if color > 255:
            color = 255
        self.RED_COLOR = color    
    def updateGreen(self, color):
        if color < 0:
            color = 0
        if color > 255:
            color = 255
        self.GREEN_COLOR = color    
    def updateBlue(self, color):
        if color < 0:
            color = 0
        if color > 255:
            color = 255
        self.BLUE_COLOR = color
    
    def updateColors(self, stop=0):
        if stop == 1:
            self.setLight(self.RED_PIN, 0)
            self.setLight(self.GREEN_PIN, 0)
            self.setLight(self.BLUE_PIN, 0)
        elif stop == 0:
            self.setLight(self.RED_PIN, self.RED_COLOR)
            self.setLight(self.GREEN_PIN, self.GREEN_COLOR)
            self.setLight(self.BLUE_PIN, self.BLUE_COLOR)
        

    '''
    Increase or decreases the brightness value based on the rate argument passed.
    Rate : 0 , Increases
    Rate : 1 , Decreases
    '''
    def updateBrightness(self, rate : int):
        if (rate == self.INCREASE_BRIGHTNESS and self.brightness + self.BRIGHTNESS_LEVEL < 255):
            self.brightness += self.BRIGHTNESS_LEVEL
        if (rate == self.DECREASE_BRIGHTNESS and self.brightness - self.BRIGHTNESS_LEVEL > 20):
            self.brightness -= self.BRIGHTNESS_LEVEL
    
    '''
    Updates the color the led, given a color rgb value.

    ...

    Parameters
    ----------
        pin : RED_PIN or GREEN_PIN or BLUE_PIN
        color : RED_COLOR or GREEN_COLOR or BLUE_COLOR
    
    Example
    -------
        x = led_strip_controller()
        x.setLight(x.RED_PIN, x.RED_COLOR)
    '''
    def setLight(self, pin, color):
        realColor = int(int(color) * (float(self.brightness) / 255.0))
        self.pi.set_PWM_dutycycle(pin, realColor)

    def start_colorshiftEffect(self):
        start_new_thread(self.colorshiftEffect, ())

    def stop_colorshiftEffect(self):
        self.shifting = False

    # Updates the color rgb values (0 to 255)
    def colorshiftEffect(self):  
        try:
            self.shifting = True
            while(self.shifting):
                while(self.RED_COLOR > 0 and self.shifting):
                    self.updateRed(self.RED_COLOR - self.STEP)
                    self.updateGreen(self.GREEN_COLOR + self.STEP)
                    self.updateColors()
                while(self.GREEN_COLOR > 0 and self.shifting):
                    self.updateGreen(self.GREEN_COLOR - self.STEP)
                    self.updateBlue(self.BLUE_COLOR + self.STEP)
                    self.updateColors()              
                while(self.BLUE_COLOR > 0 and self.shifting):
                    self.updateBlue(self.BLUE_COLOR - self.STEP)
                    self.updateRed(self.RED_COLOR + self.STEP)
                    self.updateColors()
        except AttributeError as error:
            print('Error: ', error)
            self.shifting = False                          

    # Stops the controller by updating every led to 0 and then stopping the pigpio instance
    def stop(self):
        self.shifting = False
        self.breathing = False
        self.updateColors(stop=1)
        self.pi.stop()
