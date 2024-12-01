from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
from pythonosc import tcp_client

def defaultEosHandler(arg):
    print("Default Eos Handler ",end="")
    print(arg)

class eos ():
    def __init__(self,clientIp,clientPort,serverIp,serverPort):
        self.boundHandlers={}
        self.defaultEosHandler = defaultEosHandler
#        self.dispatcher = dispatcher.Dispatcher()
#        self.dispatcher.map("/eos*", self.defaultEosHandler)
#        self.dispatcher.map("/eos/fader*", self.oscFaderHandler)
#        self.client = udp_client.SimpleUDPClient(clientIp,clientPort)
#        self.server = osc_server.ThreadingOSCUDPServer((serverIp,serverPort), self.dispatcher)
        self.client = tcp_client.SimpleTCPClient(clientIp, clientPort, mode="1.0")
        self.client.send_message("/eos/subscribe",1)
        self.client.send_message("/eos/fader/1/config/8",None)


    def start(self):
        self.server.serve_forever()

    # def defaultEosHandler(self, addr, *args):
    #     print("[{}] {}".format(addr,args))
    #     return
    

        
    def oscFaderHandler(self, addr, *args):
        (page,fader)=addr.split("/")[3:5]
        page=int(page)
        fader=int(fader)
        level=100*float(args[0])
        print("Page {} Fader {} is at {:.1f}".format(page,fader,level))
        if "FaderLevel" in self.boundHandlers:self.boundHandlers["FaderLevel"](page,fader,level)

    def bindHandler(self,name,handler):
        print(f"Eos binding handler {name}")
        if name == "": self.defaultEosHandler = handler
        else: self.boundHandlers[name] = handler
    
    def bindDispatcher(self,string,func):
        self.dispatcher.map(string, func)

    def setFaderPage(self,page):
        self.client.send_message("/eos/fader/1/config/{}/8".format(page),None)

    def service(self):
        resp = self.client.get_messages(1)
        for msg in resp:
            for handler in self.boundHandlers.keys():
                if msg.address.find(handler) != -1:
                    self.boundHandlers[handler](msg)
                    return
            self.defaultEosHandler(msg)