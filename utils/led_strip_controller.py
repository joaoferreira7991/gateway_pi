import os
import pigpio
import time
from _thread import start_new_thread

class led_strip_controller:

    # Brightness value (0 to 255)
    brightness = 25.5
    # Brightness rate of change (10% rate)
    BRIGHTNESS_LEVEL = 2.55
    
    # Shifting effect, rate of color change
    STEP = 0.025

    # Increase / Decrease brightness variables
    INCREASE_BRIGHTNESS = 0
    DECREASE_BRIGHTNESS = 1

    def __init__(self, r=17, g=27, b=22):
        
        # LED GPIO pin position
        self.RED_PIN = r
        self.GREEN_PIN = g
        self.BLUE_PIN = b

        # LED color values
        self.RED_COLOR = 0
        self.GREEN_COLOR = 0
        self.BLUE_COLOR = 0

        # Flag to enable/disable shifting
        self.shifting = False
        # Flag to enable/disable breathing
        self.breathing = False

    def start(self):
        self.pi = pigpio.pi()
        self.RED_COLOR = 255
        self.GREEN_COLOR = 255
        self.BLUE_COLOR = 255
        self.updateColors()
        
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
    
    def updateColors(self, reset=0):
        if reset == 1:
            self.updateRed(0)
            self.updateGreen(0)
            self.updateBlue(0)
            self.setLight(self.RED_PIN, self.RED_COLOR)
            self.setLight(self.GREEN_PIN, self.GREEN_COLOR)
            self.setLight(self.BLUE_PIN, self.BLUE_COLOR)
        else:
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
    
    def start_breathingEffect(self):
        start_new_thread(self.breathingEffect, ())        

    def breathingEffect(self):
        while(True):
            pass

    def start_colorshiftEffect(self):
        start_new_thread(self.colorshiftEffect, ())

    def stop_colorshiftEffect(self):
        self.shifting = False

    # Updates the color rgb values (0 to 255)
    def colorshiftEffect(self):  
        try:
            self.shifting = True
            self.updateRed(255)
            self.updateGreen(0)
            self.updateBlue(0)
            self.updateColors()

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
        self.updateColors(reset=1)
        self.pi.stop()
