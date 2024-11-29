import itertools
import os
import threading
import time
import io
import PIL
import math

from fractions import Fraction
from PIL import Image, ImageSequence, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

FRAMES_PER_SECOND=30

class sdPlus:
    def __init__(self):
        print("Init!")
        streamdecks = DeviceManager().enumerate()

        print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

        self.deck=None

        for index, d in enumerate(streamdecks):
            if d.DECK_TYPE == 'Stream Deck +':
                print("Found a StreamDeck+")
                self.deck = d
        self.lastKnobEvent=[time.time()]*4
        if self.deck == None: return

        self.deck.open()
        self.deck.reset()

        self.deck.set_key_callback(self.keyChange)
        self.deck.set_dial_callback(self.dialChange)
        self.deck.set_touchscreen_callback(self.lcdTouched)

        self.deck.set_brightness(100)

    
    def keyChange(self, deck, key, keyState):
        print("Key change")
        print(key)
        print(keyState)

    def dialChange(self,parent,n,type,data):
        t=time.time()
#        print(parent,n,type,data)
        if type == DialEventType.TURN:
            deltaT = t-self.lastKnobEvent[n]
            self.lastKnobEvent[n] = t
            velocity = data/deltaT
            print(f"Knob {n} was turned {data} counts, velocity = {velocity:0.3f} counts/sec")
        if type == DialEventType.PUSH:
            if data: print(f"Knob {n} was pushed")
            else: print(f"Knob {n} was released")

    def lcdTouched(self, deck, event_type, values):
        if event_type == TouchscreenEventType.SHORT:
            print(f"LCD short-touched at {values['x']},{values['y']}")
        if event_type == TouchscreenEventType.LONG:
            print(f"LCD long-touched at {values['x']},{values['y']}")
        if event_type == TouchscreenEventType.DRAG:
            print(f"LCD dragged from {values['x']},{values['y']} to {values['x_out']},{values['y_out']}")
            if (abs(values['x']-values['x_out'])>abs(values['y']-values['y_out'])):
                if values['x']>values['x_out']: print("Left Swipe")
                else: print("Right swipe")
            if (abs(values['x']-values['x_out'])<abs(values['y']-values['y_out'])):
                if values['y'] > values['y_out']: print("Up Swipe")
                else: print("Down swipe")
   
    def setKeyCallback(self, func):
        self.deck.set_key_callback(func)
        
    def setDialCallback(self, func):
        self.deck.set_dial_callback(func)

    def setTouchscreenCallback(self, func):
        self.deck.set_touchscreen_callback(func)
    
    def setKeyImage(self, key, img):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        self.deck.set_key_image(key, img_byte_arr)

    def setLcdImage(self, img, xPos=0, yPos=0, width=800, height=100):
        self.lcdImg = img
        img_byte_arr = io.BytesIO()
        self.lcdImg.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        self.deck.set_touchscreen_image(img_byte_arr, xPos, yPos, width, height)

    def __del__(self):
        self.deck.close()