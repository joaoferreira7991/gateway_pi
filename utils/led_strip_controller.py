import os
import pigpio
import time
from _thread import start_new_thread

class led_strip_controller:

    brightness = 15

    # shifting effect, rate of color change
    STEP = 0.025
    
    def __init__(self, r=17, g=27, b=22):
        
        # LED GPIO pin position
        self.RED_PIN = r
        self.GREEN_PIN = g
        self.BLUE_PIN = b

        # LED color values
        self.RED_COLOR = 0
        self.GREEN_COLOR = 0
        self.BLUE_COLOR = 0

        self.pi = pigpio.pi()
        self.setLight(self.RED_PIN, 255)
        self.setLight(self.GREEN_PIN, 255)
        self.setLight(self.BLUE_PIN, 255)

        # Flag to enable/disable shifting
        self.shifting = False
        # Flag to enable/disable breathing
        self.breathing = False

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

    # Updates brightness variable. Values (0 to 255)
    def updateBrightness(self, brightness):
        if brightness < 0:
            brightness = 0
        if brightness > 255:
            brightness = 255
        self.brightness = brightness

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

    # Updates the color rgb values (0 to 255)
    def colorshiftEffect(self):  
        self.shifting = True
        self.updateRed(255)
        self.updateGreen(0)
        self.updateBlue(0)
        self.setLight(self.RED_PIN, self.RED_COLOR)
        self.setLight(self.GREEN_PIN, self.GREEN_COLOR)
        self.setLight(self.BLUE_PIN, self.BLUE_COLOR)

        while(self.shifting):
            while(self.RED_COLOR > 0 and self.shifting):
                self.updateRed(self.RED_COLOR - self.STEP)
                self.updateGreen(self.GREEN_COLOR + self.STEP)
                self.setLight(self.RED_PIN, self.RED_COLOR)
                self.setLight(self.GREEN_PIN, self.GREEN_COLOR)
            while(self.GREEN_COLOR > 0 and self.shifting):
                self.updateGreen(self.GREEN_COLOR - self.STEP)
                self.updateBlue(self.BLUE_COLOR + self.STEP)
                self.setLight(self.GREEN_PIN, self.GREEN_COLOR)
                self.setLight(self.BLUE_PIN, self.BLUE_COLOR)                
            while(self.BLUE_COLOR > 0 and self.shifting):
                self.updateBlue(self.BLUE_COLOR - self.STEP)
                self.updateRed(self.RED_COLOR + self.STEP)
                self.setLight(self.BLUE_PIN, self.BLUE_COLOR)  
                self.setLight(self.RED_PIN, self.RED_COLOR)                               

    # Stops the controller by updating every led to 0 and then stopping the pigpio instance
    def stop(self):
        self.setLight(self.RED_PIN, 0)
        self.setLight(self.GREEN_PIN, 0)
        self.setLight(self.BLUE_PIN, 0)

        # Wait 1 second to let the leds shut off
        time.sleep(1)
        self.pi.stop()
