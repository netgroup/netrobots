# -*- coding: utf-8 -*-
"""
Client protocol.
It handles the communication with the c programs.
"""

from twisted.protocols import basic
from twisted.internet import reactor
from twisted.protocols.policies import TimeoutMixin
import random 

class PlayerProtocol(basic.LineReceiver, TimeoutMixin):
    """
        When the client connect we ask the name
        When the match starts we ask for actions 
    """
    request_code = {
            'QUIT': 'q',
            'ACTION': 'a',
            'NAME': 'n',
            }
    response_code = {
            'NAME': 'n',
            'FIRE': 'f', 
            'MOVE': 'm',
            }
    RESPONDING_TIMEOUT = 10 #seconds
    hasPendingMessage = False
    name = ''

    def log(self, what):
        if self.name:
            print self.name, ": ", what
        else:
            print "Unknown client", ": ", what
    
    def connectionMade(self):
        print "Got new client!"
        self.transport.setTcpNoDelay(True)

        # ask for the player name
        self.message(self.request_code['NAME'] + " " + str(self.factory.game.GRID_SIZE))
        self.hasPendingMessage = True

    def connectionLost(self, reason):
        # called also after a timeout
        print "Lost a client!"
        shuttle = self.factory.game.getShuttle(self)
        if shuttle and shuttle.is_alive:
            # if the shuttle already entered in the game (i.e. gave at least its name)
            shuttle.die('connection lost')
        self.factory.game.rmPlayer(self)


    def lineReceived(self, line):
        line= unicode(line, errors='ignore')
        print "Line received", line
        if len(line) < 3:
            self.log("message received is too short: " + line)
            return
        if not self.hasPendingMessage:
            self.log("spurious response: " + line)
            return
        code = line[0]
        payload = line[2:]
        self.hasPendingMessage = False
        #self.resetTimeout()
        self.setTimeout(None) 

        # decode the protocol response
        if code == self.response_code['NAME']:
            self.name = payload
            if len(payload) < 1:
                self.log("received empty player name: {}".format(payload))
                return
            self.log("Received client name: " + payload)
            self.factory.game.addPlayer(self, payload)
        elif code == self.response_code['MOVE']:
            self.log("moving " + payload)
            if not (len(payload) == 1 and payload in 'udlr'):
                self.log("received wrong move direction: {}".format(payload))
                return
            self.factory.game.getShuttle(self).move(payload)
        elif code == self.response_code['FIRE']:
            # do the fire action 
            try:
                angle = float(payload)
            except:
                self.log("angle is not a valid float {}".format(payload))
                return 
            if angle <0 or angle > 360:
                self.log("angle is not valid {}".format(angle))
                return

            self.factory.game.getShuttle(self).sendRocket(float(payload))
        else:
            self.log("Received an unknown code from the client: " + payload)

        if self.factory.game.hasEverybodyAnswered() and self.factory.game.isStarted():
            # do game logic 
            print "everybody answered, let's move on"
            self.factory.game.update()

    def sendQuit(self, reason):
        self.message(self.request_code['QUIT'] + " " + reason )
        self.transport.loseConnection()

    def message(self, message):
        message = message.encode('ascii', 'ignore')
        "sending message: ", message
        self.transport.write(message + '\n')


    def timeoutConnection(self):
        print "Timeout"
        try:
            self.transport.abortConnection()
            self.factory.game.getShuttle(self).die('timeout')
            self.factory.game.rmPlayer(self)
        except:
            pass


    def ask_for_actions(self):
        self.log("ask for action")
        self.message(self.request_code['ACTION'] + " " + self.factory.game.getGameStatus(self))
        self.hasPendingMessage = True
        # start a timeout. If clients do not answer in time, kick them out
        self.setTimeout(self.RESPONDING_TIMEOUT)    

