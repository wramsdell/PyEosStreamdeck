from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

class eos ():
    def __init__(self,clientIp,clientPort,serverIp,serverPort):
        self.boundHandlers={}
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/eos*", self.defaultEosHandler)
        self.dispatcher.map("/eos/fader*", self.oscFaderHandler)
        self.client = udp_client.SimpleUDPClient(clientIp,clientPort)
        self.server = osc_server.ThreadingOSCUDPServer((serverIp,serverPort), self.dispatcher)
        self.client.send_message("/eos/subscribe",1)
        self.client.send_message("/eos/fader/1/config/8",None)

    def start(self):
        self.server.serve_forever()

    def defaultEosHandler(self, addr, *args):
        print("[{}] {}".format(addr,args))
        return
    
    def oscFaderHandler(self, addr, *args):
        (page,fader)=addr.split("/")[3:5]
        page=int(page)
        fader=int(fader)
        level=100*float(args[0])
        print("Page {} Fader {} is at {:.1f}".format(page,fader,level))
        if "FaderLevel" in self.boundHandlers:self.boundHandlers["FaderLevel"](page,fader,level)

    def bindHandler(self,name,handler):
        print("Eos binding handler {}".format(name))
        self.boundHandlers[name]=handler
    
    def bindDispatcher(self,string,func):
        self.dispatcher.map(string, func)

    def setFaderPage(self,page):
        self.client.send_message("/eos/fader/1/config/{}/8".format(page),None)