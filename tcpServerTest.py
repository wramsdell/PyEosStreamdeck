from pythonosc import tcp_client
from pythonosc import osc_tcp_server
from pythonosc.dispatcher import Dispatcher

def filter_handler(address, *args):
    print(f"Foo!! {address} {args}")

d = Dispatcher()

d.map("/eos/out*", filter_handler)

server = osc_tcp_server.ThreadingOSCTCPServer(("127.0.0.1", 1235), d, "1.0")
client = tcp_client.SimpleTCPClient("127.0.0.1", 1234, mode="1.0")

client.send_message("/eos/subscribe",1)

while True:
    resp = client.get_messages(1)
    for r in resp:
       try:
           print(r)
       except Exception as e:
           print(f"oops {str(e)}: {r}")