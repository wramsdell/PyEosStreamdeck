from SdPlus import sdPlus
from PIL import Image, ImageSequence, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType
import textwrap
import time
import eos
import socket

CLIENT_IP = SERVER_IP = "127.0.0.1"
#IN_PORT=8000 #Eos's OSC in port
IN_PORT=1234
OUT_PORT=8001 #Eos's OSC out port

encoderPages=["core","color1","color2","shutter","gobo","5","6","7"]
encoderParameters=[
    ["intens","pan","tilt","zoom","edge","iris","",""],
    ["level","red","green","blue","amber","white","hue","saturation"],
    ["level","cyan","magenta","yellow","cto","ctb","hue","saturation"],
    ["level","frame thrust a","frame angle a","zoom","edge","iris","",""],
    ["level","zoom","edge","gobo select","gobo select 2","gobo index/speed","Beam Fx Select","Beam Fx Index/Speed", "zoom"],
    ["level","pan","tilt","zoom","edge","iris","",""],
    ["level","pan","tilt","zoom","edge","iris","",""],
    ["level","pan","tilt","zoom","edge","iris","",""]
]

encoderPage = [0,0]
lastKnobEvent=[time.time()]*4

def drawLcdBackground(img):
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(((10, 10), (190, 90)), 10, fill="blue", outline="white", width=3)
    draw.rounded_rectangle(((210, 10), (390, 90)), 10, fill="blue", outline="white", width=3)
    draw.rounded_rectangle(((410, 10), (590, 90)), 10, fill="blue", outline="white", width=3)
    draw.rounded_rectangle(((610, 10), (790, 90)), 10, fill="blue", outline="white", width=3)
    return img

def drawLcdText(index, text, font, img):
    d = ImageDraw.Draw(img)
    wrapper = textwrap.TextWrapper(width=11)
    text = wrapper.wrap(text)
    text = "\n".join(text)
    d.multiline_text(((index*200)+20, 7), text, font=font, fill="white")
    return img

def drawKeyBackground(img):
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(((10, 10), (110, 110)), 20, fill="blue", outline="white", width=3)
    return img

def updateTouchscreen(text):
    font = ImageFont.truetype("APTOS.TTF", 24, encoding="unic")
    img = Image.new('RGB', (800, 100), 'black')
    img = drawLcdBackground(img)
    n=len(text)
    if n>4: n=4
    for i in range(n):
        img = drawLcdText(i, text[i], font, img)
    sd.setLcdImage(img)

def dialCallback(deck, n, type, data):
        t=time.time()
        parameter = encoderParameters[encoderPage[0]][encoderPage[1]+n]
        if type == DialEventType.TURN:
            deltaT = t-lastKnobEvent[n]
            lastKnobEvent[n] = t
            velocity = data/deltaT
            print(f"{parameter} was turned {data} counts, velocity = {velocity:0.3f} counts/sec")
            e.client.send_message(f"/eos/wheel/{parameter}",float(data))
        if type == DialEventType.PUSH:
            if data:
                print(f"Knob {n} was pushed")
                print(f"{parameter} home")
                e.client.send_message(f"/eos/param/{parameter}/home")
            else: print(f"Knob {n} was released")
    
def touchCallback(deck, event_type, values):
        print("Overridden touchscreen callback",end="")
        if event_type == TouchscreenEventType.SHORT:
            print(f"LCD short-touched at {values['x']},{values['y']}")
        if event_type == TouchscreenEventType.LONG:
            print(f"LCD long-touched at {values['x']},{values['y']}")
        if event_type == TouchscreenEventType.DRAG:
            print(f"LCD dragged from {values['x']},{values['y']} to {values['x_out']},{values['y_out']}")
            if (abs(values['x']-values['x_out'])>abs(values['y']-values['y_out'])):
                if values['x']>values['x_out']:
                    print("Left Swipe")
                    encoderPage[1] = encoderPage[1] + 4
                    if encoderPage[1] >= len(encoderParameters[encoderPage[0]]): encoderPage[1] = 0
                else:
                    print("Right swipe")
                    encoderPage[1] = encoderPage[1] - 4
                    if encoderPage[1] < 0: encoderPage[1] = int(len(encoderParameters[encoderPage[0]])/4)

            if (abs(values['x']-values['x_out'])<abs(values['y']-values['y_out'])):
                if values['y'] > values['y_out']:
                    print("Up Swipe")
                    encoderPage[0]=encoderPage[0]+1
                    if encoderPage[0]>=len(encoderParameters): encoderPage[0]=0
                    encoderPage[1]=0
                else:
                    print("Down swipe")
                    encoderPage[0]=encoderPage[0]-1
                    if encoderPage[0]<0: encoderPage[0]=len(encoderParameters)-1
                    encoderPage[1]=0

            page=encoderPage[0]
            index=encoderPage[1]
            print(encoderPage)
            updateTouchscreen(encoderParameters[page][index:])

def eosDefaultHandler(arg):
    print("My Default Handler ",end="")
    print(arg)

def eosSoftkeyHandler(arg):
    print("Softkey Handler ",end="")
    print(arg)

def eosWheelHandler(arg):
    print(f"Wheel Handler {arg.params}")

sd = sdPlus()
e = eos.eos(SERVER_IP,IN_PORT,CLIENT_IP,OUT_PORT) #Instantiate an Eos client and server
#e.bindDispatcher("/eos*",myEosHandler)
e.bindHandler("",eosDefaultHandler)
e.bindHandler("/eos/out/softkey",eosSoftkeyHandler)
e.bindHandler("/eos/out/active/wheel",eosWheelHandler)
e.client.send_message("/eos/ping",None)

sd.setTouchscreenCallback(touchCallback)
sd.setDialCallback(dialCallback)
for i in range(8): sd.setKeyImage(i,drawKeyBackground(Image.new('RGB', (120, 120), 'black')))
updateTouchscreen(encoderParameters[0][0:4])



while True:
    e.service()
    time.sleep(.005)
