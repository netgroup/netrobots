# -*- coding: utf-8 -*-
"""
This module implement the websocket protocol.
It speaks with the javascript to update robot positions and actions. 
"""
from autobahn.twisted.websocket import WebSocketServerProtocol
import json
from twisted.internet import reactor

class WebInterfaceProtocol(WebSocketServerProtocol):
    """
    This class implements the protocol for the websocket communication.
    Protocol is quite simple: 
    - when game is started, send the initial information (player names etc)
    - if "s" is received, return the current game status
    """

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.initGame()

    def initGame(self):
        # polling: we send initial game information when the game is started
        # otherwise we keep looping
        if self.factory.game.isStarted():
            self.sendGameInfo()
        else:
            reactor.callLater(0.1, self.initGame)

    def onMessage(self, payload, isBinary):
        print "received payload", payload
        if payload == "s": 
            # give current game status
            status = self.getGameStatus()
            self.sendMessage(status)

    def sendGameInfo(self):
        player_names = []
        for p in self.factory.game.players:
            if p.is_alive:
                player_names.append(p.name)

        game_info = {
                "type": "init",
                "player_names": player_names,
                "grid_size": self.factory.game.GRID_SIZE,
                }
        payload = json.dumps(game_info)
        self.sendMessage(payload)


    def getGameStatus(self):
        shuttles = []
        for p in self.factory.game.players:
            if p.is_alive:
                shuttle = {'name': p.name, 'x': p.x, 'y': p.y}
                if p.rocket:
                    shuttle['rocket'] = {'x': math.round(p.rocket.x), 'y': math.round(p.rocket.y), 'angle': p.rocket.angle}
                shuttles.append(shuttle)

        game_status = {
                "type": "update",
                "shuttles": shuttles,
                }
                
        return json.dumps(game_status)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
