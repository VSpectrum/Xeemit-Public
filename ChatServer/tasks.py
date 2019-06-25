from ProjXeemit.settings import SSL_KEY_PATH, SSL_CERT_PATH
from Xeemit.models import *
from models import *
from twisted.internet import protocol, reactor, ssl
from twisted.internet.protocol import Factory,Protocol
from txsockjs.factory import SockJSFactory
import json, re


chat_room = {}


class ChatProtocol(Protocol):
    def connectionMade(self):
        print("Connection Made")
        self.factory.clients.append(self)
        self.transport.write('{"success":"Connection Succeeded"}')

    def dataReceived(self, data):
        data = json.loads(data)
        toUser = UserProfile.objects.get(user__username=data["toUser"])
        fromUser = UserProfile.objects.get(user__username=data["fromUser"])
        RequestObj = Request.objects.get(requestID=data["requestID"])
        trueKey = ChatKey.objects.get(request=RequestObj)


        if trueKey.key == data["key"]:
            if "msg" in data.keys():
                if data["msg"] == "adduser":
                    if data["requestID"] not in chat_room:
                        chat_room[data["requestID"]] = []
                    if self not in chat_room[data["requestID"]]:
                        chat_room[data["requestID"]].append(self)
                elif re.search('\w+', data["msg"]):
                    RequestChat.objects.create(request=RequestObj, fromUser=fromUser, toUser=toUser, message=data["msg"], statusRead=False)
                    del data["key"]
                    for client in chat_room[data["requestID"]]:
                        client.transport.write(json.dumps(data))



    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        for request in chat_room:
            try:
                chat_room[request].remove(self)
                print("Client Removed")
            except ValueError:
                pass
        print(self, " - Connection Lost")

options = {
    'websocket': True,
    'cookie_needed': False,
    'heartbeat': 10,
    'timeout': 5,
    'streaming_limit': 128 * 1024,
    'encoding': 'cp1252',  # Latin1
    'sockjs_url': 'https://cdn.jsdelivr.net/sockjs/1/sockjs.min.js',
    'proxy_header': None
}


def run_server():
    print("Readying Reactor")
    factory = protocol.ServerFactory()
    factory.protocol = ChatProtocol
    factory.clients = []
    reactor.listenSSL(1025, SockJSFactory(factory, options), ssl.DefaultOpenSSLContextFactory(SSL_KEY_PATH, SSL_CERT_PATH))
    reactor.run()
