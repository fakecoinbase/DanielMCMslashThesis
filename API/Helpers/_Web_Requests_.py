# cbpro/WebsocketClient.py
# original author: Daniel Paquin
# mongo "support" added by Drew Rice
#
#
# Template object to receive messages from the Coinbase Websocket Feed

from __future__ import print_function
import json
import base64
import hmac
import hashlib
import time
import ast
from threading import Lock, Thread, Event, currentThread

from websocket import create_connection, WebSocketConnectionClosedException
from pymongo import MongoClient
from cbpro.cbpro_auth import get_auth_headers
import gzip

class M_SocketManager(object):
    def __init__(self, url):
        self.url = url
        self.cont = True
        self.error = None
        self.ws = None
        self.thread = []

    def connect_to(self, path, callback, payload = ""):
        #print("PATH = " + path)
        try:
            ws_a = create_connection(path)
        except Exception as e:
            print("Connection not created!!")
            print(path)
            print(e)
            print("Reconnecting...")
            time.sleep(5)
            self.connect_to(path, callback, payload)
        if payload != "":
            ws_a.send(payload)
        t = currentThread()
        while getattr(t, "do_run", True): 
            try:
                pre_msg =  ws_a.recv()
                msg = json.loads(pre_msg)
                callback(msg)
            except WebSocketConnectionClosedException as e:
                print("Connection not created!!")
                print(path)
                print(e)
                print("Reconnecting...")
                time.sleep(5)
                self.connect_to(path, callback, payload)
            except Exception as e:
                try:
                    msg = json.loads(gzip.decompress(pre_msg).decode())
                    if 'ping' in msg:
                        data = {
                            "pong": msg['ping'] 
                        }
                        data = json.dumps(data).encode()
                        ws_a.send(data)
                    callback(msg)
                except TypeError:
                    if pre_msg == "" or msg == "":
                        try:
                            data = {"code":"0","msg":"pong"}
                            data = json.dumps(data).encode()
                            ws_a.send(data)
                except Exception as e2:
                    print("PRIMERO")
                    print(type(e))
                    print(e.args)
                    print(e)
                    print("SEGUNDO! " + path)
                    print(type(e2))
                    print(e2.args)
                    print(e2)
                    print(pre_msg)
                    print("RECONNECTING")
                    print(msg)
                    print(type(msg))
                    print(msg == "")
                    ws_a.close()

            #lock.acquire()
            #message_list.append(response_a)
            #lock.release()
            msg = ""
            pre_msg = ""

    def _start_socket(self, path, callback, version = "", prefix = "", **Kwargs):
        con = self.url
        if version != "":
            con += version
        if prefix != "":
            con += prefix
        if path != "":
            con += path

        payload = ""
        if "payload" in Kwargs:
            payload = json.dumps(Kwargs["payload"], ensure_ascii=False).encode('utf8')
        #print(con, payload)
        thr = Thread(target=self.connect_to, args=(con, callback, payload))
        thr.setDaemon(True)
        self.thread.append(thr)

    def start(self):
        for t in self.thread:
            t.start()
        #for t in self.thread:
        #    t.join()

    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
        except WebSocketConnectionClosedException as e:
            pass

        self.on_close()
    def on_close(self):
        print("\n-- Socket Closed --")

    def close(self):
        for th in self.thread:
            th.do_run = False

    #def on_open(self):
    #    if self.should_print:
    #        print("-- Subscribed! --\n")

    #def on_close(self):
    #    if self.should_print:
    #        print("\n-- Socket Closed --")

    #def on_message(self, msg):
    #    if self.should_print:
    #        print(msg)
    #    if self.mongo_collection:  # dump JSON to given mongo collection
    #        self.mongo_collection.insert_one(msg)

    #def on_error(self, e, data=None):
    #    self.error = e
    #    self.stop = True
    #    print('{} - data: {}'.format(e, data))


if __name__ == "__main__":
    import sys
    import time
    import json

    def process_message(msg):
        try:
            print("message type: {}".format(msg['e']))
            print(msg)
        except:
            print("message type: Other")
            print(msg)
    #class MyWebsocketClient(M_SocketManager):
        #def on_open(self):
        #    self.url = "wss://ws-feed.pro.coinbase.com/"
        #    self.products = ["BTC-USD", "ETH-USD"]
        #    print("HEYHEY!")
        #    self.message_count = 0
        #    print("Let's count the messages!")

        #def on_message(self, msg):
        #    print(json.dumps(msg, indent=4, sort_keys=True))
        #    self.message_count += 1

        #def on_close(self):
        #    print("-- Goodbye! --")


    wsClient = M_SocketManager("wss://ws-feed.pro.coinbase.com/")
    data = {"payload": {
                "type": "subscribe",
                "product_ids": [
                    "ETH-USD",
                    "ETH-EUR"
                ],
                "channels": [
                    "level2",
                    "heartbeat",
                    {
                        "name": "ticker",
                        "product_ids": [
                            "ETH-BTC",
                            "ETH-USD"
                        ]
                    }
                ]
            }}
    data2 = {
            "type": "subscribe",
            "channels": [
                {
                    "name": "level2",
                    "product_ids": [
                        "ETH-USD"
                    ]
                }
            ]
        }
    wsClient._start_socket("",process_message, "", **data)
    wsClient._start_socket("",process_message, "", **data2)
    print("Hola?")

    wsClient.start()
    time.sleep(4)
    wsClient.close()