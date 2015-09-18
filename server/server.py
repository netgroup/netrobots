# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
A game server for C "robot war" like game.

This server allow C programs to connect and pilot space shuttles that can move inside an arena. 
Shuttles can fire to other shuttles. Last one wins.
This server communicate via websocket with a web page, showing what is going on.

"""
__author__ = "Lorenzo Bracciale"
__license__ = "GPL3"
__email__ = "lorenzo.bracciale@uniroma2.it"


from autobahn.twisted.websocket import WebSocketServerFactory
from webprotocol import WebInterfaceProtocol
from playerprotocol import PlayerProtocol
from game import Game
import sys

from twisted.python import log
from twisted.internet import reactor, protocol



if __name__ == '__main__':


    log.startLogging(sys.stdout)

    game = Game()


    # to speak with the web page we use a websocket
    factory_web = WebSocketServerFactory(u"ws://127.0.0.1:9000", debug=False)
    factory_web.protocol = WebInterfaceProtocol
    factory_web.game = game
    
    # to speak with C client, we use standard TCP sockets    
    factory_client = protocol.ServerFactory()
    factory_client.protocol = PlayerProtocol
    factory_client.game = game

    reactor.listenTCP(9000, factory_web)
    reactor.listenTCP(10000, factory_client)
    reactor.run()
