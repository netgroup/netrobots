# netrobots
A tournament game in which players control their own shuttles and must destroy other ones with rockets.

## Features and rules
There is a server and a web interface to display the game status.
The interaction with the players is reduced to be as simply as possible.

Each player periodically must instruct the server on the direction where he want to move his shuttle. This is done by a simple C client program.

Every shuttle can send a rocket specifing the angle. If a rocket hits another shuttle, it will destroy it.

Last shuttle survived is the winner.

# How to play

1) open web/index.html in a browser
2) start the python engine: python server/server.py
3) compile and modify client/main.c - launch the client with ./main IP_OF_THE_SERVER

![alt tag](https://raw.githubusercontent.com/netgroup/netrobots/master/screenshot.png)

