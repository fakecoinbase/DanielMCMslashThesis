from API.Main.Client import Client, Web_Client
from datetime import datetime
import time

#a = Client.Bithumb()

#print("We get the first pair!\n")
#print(a.ticker("BTC", "KRW"))

a.close()

def process_message(msg):
    try:
        print("message type: {}".format(msg['e']))
        print(msg)
    except:
        print("message type: Other")
        print(msg)

b = Web_Client.Bithumb()
# start any sockets here, i.e a trade socket
#b.start_ticker('BTC-USDT', process_message)

b.start()
print(b.is_alive())
time.sleep(20)
b.close()

