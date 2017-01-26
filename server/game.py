# -*- coding: utf-8 -*-
"""
Main game logic
"""
import random
import time 
import math



class Rocket:
    """
           __
       \ \_____
    ###[==_____>
       /_/      __
                \ \_____
             ###[==_____>
                /_/

    """

    COLLISION_RANGE = 10

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

    def move(self):
        self.x = self.x + math.cos(math.radians(self.angle))
        self.y = self.y + math.sin(math.radians(self.angle))
        print "Moving rocket to ", self.x, " ", self.y
        
    def isOut(self):
        return self.rocket.x == self.rocket.grid_size or \
            self.rocket.x == 0 or \
            self.rocket.y == self.grid_size or \
            self.rocket.y == 0

    def collide(self, x, y):
        if abs(x - self.x) < self.COLLISION_RANGE and abs(y - self.y) < self.COLLISION_RANGE:
            return True
        else:
            return False




class Shuttle:
    """
            | \
        =[_|H)--._____
        =[+--,-------'
         [|_/""        
    """

    def __init__(self, protocol, name, grid_size):
        self.is_alive = True
        self.protocol = protocol
        self.name = name
        self.grid_size = grid_size
        self.x = random.randint(0, grid_size)
        self.y = random.randint(0, grid_size)
        self.rocket = None

    def sendRocket(self, angle):
        if not self.rocket:
            self.rocket = Rocket(self.x, self.y, angle)

    def canFire(self):
        return not self.rocket


    def move(self, direction):
        # move up down ...
        if direction == 'u':
            #up
            self.y = min(self.y+1, self.grid_size)
        elif direction == 'd':
            #down
            self.y = max(self.y-1, 0)
        elif direction == 'l':
            #left
            self.x = max(self.x-1, 0)
        elif direction == 'r':
            #right
            self.x = min(self.x+1, self.grid_size)


    def die(self, reason):
        self.is_alive = False
        self.protocol.sendQuit(reason)
        # disconnect client?


class Game:
    # settings
    NUMBER_OF_PLAYER = 2 #how many player we need to wait before starting the game?
    GRID_SIZE = 300 # the grid is a square GRID_SIZE X GRID_SIZE

    # interal variables
    GAME_WAIT_FOR_PLAYERS = 1
    GAME_STARTED = 2
    GAME_OVER = 3

    status = GAME_WAIT_FOR_PLAYERS
    players = []
    winner = None


    def addPlayer(self, protocol, name):
        shuttle = Shuttle(protocol, name, self.GRID_SIZE)
        self.players.append(shuttle)
        print "player added! len is ", len(self.players)
        if len(self.players) == self.NUMBER_OF_PLAYER:
            self.start()

    def rmPlayer(self, protocol): 
        i = 0
        for p in self.players:
            if p.protocol == protocol:
                del self.players[i]
                print "player removed, len is ", len(self.players)
                break 
            else:
                i += 1

    def start(self):
        print "Game is started!"
        self.status = self.GAME_STARTED
        for player in self.players:
            player.protocol.ask_for_actions()

    def isStarted(self):
        return self.status == self.GAME_STARTED

    def hasEverybodyAnswered(self):
        for player in self.players:
            if player.protocol.hasPendingMessage:
                return False
        return True


    def onEverybodyAnswered(self):
        for player in self.players:
            players.protocol.ask_for_actions()


    def end(self):
        import sys
        self.status = self.GAME_OVER
        print("game is terminated")

    def update(self):
        """
        Everybody answered, let's compute collision and move on
        """
        # -- move rockets
        # -- check for collision
        time.sleep(0.01)
        alive_players = 0
        for p in self.players:
            if p.is_alive and p.rocket:
                p.rocket.move()
                for o in self.players:
                    if p != o and p.rocket.collide(o.x, o.y):
                        print "Player " + p.name + " kills " + o.name
                        o.die("you have been killed by " + p.name)
                if p.rocket.x > self.GRID_SIZE or p.rocket.x < 0 or \
                    p.rocket.y > self.GRID_SIZE or p.rocket.y < 0:
                    del p.rocket
                    p.rocket = None

        for p in self.players:
            if p.is_alive:
                alive_players += 1

        if alive_players == 1:
            print "Only one player, it wins"
            for p in self.players:
                if p.is_alive:
                    self.winner = p.name
                    p.die("You win!")
            self.end()
        elif alive_players == 0:
            print "no one survived!"
            self.end()
        else:
            for p in self.players:
                p.protocol.ask_for_actions()





    def getShuttle(self, protocol):
        """
        Return a shuttle object given its protocol instance
        """
        for player in self.players:
            if player.protocol == protocol:
                return player
        return None


    def getGameStatus(self, protocol):
        """
        Return the game status to the clients. 
        The format is:
        CAN_FIRE NUMBER_OF_SPACESHIPS X1 Y1 X2 Y2 X3 Y3 ... NUMBER_OF_ROCKETS X1 Y1 A1 X2 Y2 A2 ...
        We are the first spaceship!
        """

        alive_players = 0
        alive_rockets = 0
        positions = []
        rockets = []

        for p in self.players:
            if p.is_alive:
                alive_players += 1
                if p.protocol == protocol:
                    positions.insert(0, p.y)
                    positions.insert(0, p.x)
                else:
                    positions.append(p.x)
                    positions.append(p.y)
                if p.rocket:
                    alive_rockets += 1
                    rockets.append(int(round(p.rocket.x)))
                    rockets.append(int(round(p.rocket.y)))
                    rockets.append(p.rocket.angle)

        game_status = str(int(self.getShuttle(protocol).canFire())) + " " +  \
            str(alive_players) + " " + \
            " ".join(str(x) for x in positions) + " " +\
            str(alive_rockets) + " " +\
            " ".join(str(x) for x in rockets)

        return game_status


