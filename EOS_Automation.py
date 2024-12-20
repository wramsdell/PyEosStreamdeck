from SdPlus import sdPlus
import eos
import time
import socket
encoderPages=["core","color1","color2","shutter","gobo","5","6","7"]
encoderParameters=[
    ["level","pan","tilt","zoom","edge","iris","",""],
    ["level","red","green","blue","amber","white","hue","saturation"],
    ["level","cyan","magenta","yellow","cto","ctb","hue","saturation"],
    ["level","frame thrust a","frame angle a","zoom","edge","iris","",""],
    ["level","zoom","edge","gobo select","gobo select 2","gobo index\speed","Beam Fx Select","Beam Fx Index\Speed"],
    ["level","pan","tilt","zoom","edge","iris","",""],
    ["level","pan","tilt","zoom","edge","iris","",""],
    ["level","pan","tilt","zoom","edge","iris","",""]
]

sd = sdPlus()

encoderPage=0
faderPage=0

CLIENT_IP=socket.gethostbyname(socket.gethostname()) #It's assumed that this script is running on the same machine as Eos.  If not, change this to the Eos machine's IP address.
print(CLIENT_IP)
SERVER_IP="192.168.137.1"
IN_PORT=8000 #Eos's OSC in port
OUT_PORT=8001 #Eos's OSC out port


def xtFaderHandler(arg): #Custom XTouch fader event handler: sends the new level to Eos via OSC
    e.client.send_message("/eos/fader/1/{}".format(arg["fader"]+1),float(arg["level"]/16000))

def eosFaderHandler(page,fader,level): #Custom Eos fader event handler: sends the new fader value to the XTouch
    xt.setFader(fader-1,int(level*(16256/100)))

def xtKnobIncrementHandler(arg):
    e.client.send_message("/eos/wheel/{}".format(encoderParameters[encoderPage][arg["channel"]]),float(1+((arg["speedRange"]-1)*10)))

def xtKnobDecrementHandler(arg):
    e.client.send_message("/eos/wheel/{}".format(encoderParameters[encoderPage][arg["channel"]]),float(-(1+((arg["speedRange"]-1)*10))))

def setScribbleStripText(channel,row,text):
    xt.channel[channel].scribbleStrip[row].setText(text)

def xtEncoderModePressHandler(arg):
    setEncoderPage(arg["channel"])

def xtFaderPagePressHandler(arg):
    global faderPage
    if (faderPage<6): faderPage=faderPage+1
    else: faderPage=0
    setFaderPage(faderPage)

def xtFaderPagePressAndHoldHandler(arg):
    global faderPage
    faderPage=0
    setFaderPage(faderPage)

def setFaderPage(page):
        xt.channel[7].vuBar.set((page*2)+1)
        e.setFaderPage(page+1)

def setEncoderPage(page):
    global encoderPage
    encoderPage=page
    for i in range(len(encoderParameters[page])):
        if (i>7):
            return
        setScribbleStripText(i,0,encoderParameters[page][i])

def initButtonLabels():
    for i in range(len(encoderPages)):
        if i>7: return
        setScribbleStripText(i,1,encoderPages[i])

xt=XTouch.XTouch() #Instantiate an XTouch Extender
e=eos.eos(CLIENT_IP,IN_PORT,CLIENT_IP,OUT_PORT) #Instantiate an Eos client and server

xt.bind("FaderLevel",xtFaderHandler) #Bind our custom XTouch fader event handler
xt.bind("KnobIncrement",xtKnobIncrementHandler) #Bind our custom XTouch fader event handler
xt.bind("KnobDecrement",xtKnobDecrementHandler) #Bind our custom XTouch fader event handler
xt.bind("ButtonPress0",xtEncoderModePressHandler) #Bind the encoder mode buttons
xt.bind("ButtonPress3",xtFaderPagePressHandler,channels=7) #Bind the fader page button
xt.bind("ButtonPressAndHold3",xtFaderPagePressAndHoldHandler,channels=7) #Bind the fader page button
e.bindHandler("FaderLevel",eosFaderHandler) #Bind our custom Eos fader event handler

initButtonLabels()
setEncoderPage(0)
setFaderPage(0)

e.start() #This is blocking, so always issue it as the very last step