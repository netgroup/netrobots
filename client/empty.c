/* Sample TCP client */

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <unistd.h> // for close
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#define MAX_TX_BUF 1500
#define MAX_RX_BUF 1500

#define REQUEST_QUIT 'q'
#define REQUEST_ACTION 'a'
#define REQUEST_NAME 'n'

#define RESPONSE_MOVE 'm'
#define RESPONSE_FIRE 'f'
#define RESPONSE_NAME 'n'

int arena_size;

// This function is called every time we receive a new message from the server
// the message from the server is in request, while our goal is to populate 
// response to answer back.
int handle_msg(char request[MAX_RX_BUF], int sockfd) {

    char response[MAX_TX_BUF];
    int sent_bytes = -1;
    printf("first char is %c\n", request[0]);

    switch(request[0]) {
        case REQUEST_QUIT:
            // the server ask us to quit, just return
            return 1;
        case REQUEST_NAME:
            // server ask for our name
            // answer "n YOURNAME\"
            printf("Server ask for my name...\n");
            // server is sending us the grid size and is asking us our name

            // to get the arena size, parse an int from &request[2]
            // arena is a square arena_size X arena_size

            // write in "response" a string such "n YOUR_NAME"
            
            break;
        case REQUEST_ACTION:
            
            printf("Server ask for action...\n");
            printf("Received from server: %s\n", request);
            // for our convenience, the server send us the positions of other shuttles
            // in the list we are the first one
            // it send to us also the position of rockets sent by other spacecraft

            // the format is
            // CAN_FIRE NUMBER_OF_SPACESHIPS X1 Y1 X2 Y2 X3 Y3 ... NUMBER_OF_ROCKETS X1 Y1 A1 X2 Y2 A2 ...
            // e.g. 0 3 120 234 45 87 98 67 1 10 100 282.23
            // Explaination:
            // You can not fire, there are three shuttles. We are at coords (120, 234), there is a rocket at (10, 100)
            // this string starts from parse &request[2] and write your response in response


            // we can decide where to move
            // we can move up (u), down (d), left (l) or right (r)
            // just answer writing "m u" in "response" to go up or "m l" to go left
            // example: sprintf(response, "m u"); // go up
            
            // alternatively, we can also decide to fire
            // syntax is f ANGLE where angle is a float
            // example: sprintf(response, "f %f", 271.32); // fire at angle 271.32

            break;


    }

    // send response to server
    strcat(response, "\r\n"); //add endline
    sent_bytes = send(sockfd, response, strlen(response), 0); //send to the server
    printf("Sent %d bytes\n", sent_bytes);

    return 0;
}

int main(int argc, char**argv)
{
    int sockfd,n_bytes;
    struct sockaddr_in servaddr,cliaddr;
    char request[MAX_RX_BUF];
    int quit = 0, flag = 1;

    if (argc != 2)
    {
      printf("usage:  robot <IP address>\n");
      exit(1);
    }

    sockfd=socket(AF_INET,SOCK_STREAM,0);
    setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, (char *) &flag, sizeof(int)); // disable Naggle algorithm

    bzero(&servaddr,sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr=inet_addr(argv[1]);
    servaddr.sin_port=htons(10000);

    connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr));

    while(!quit) {
        n_bytes = recv(sockfd, request, sizeof(request) - 1, 0);

        if (n_bytes == -1) {
            // Socket in error state
            return 0;
        } else if (n_bytes == 0) {
            // Socket has been closed
            fprintf (stderr, "Socket %d closed", sockfd);
            close(sockfd);
            return 0;
        } else {
            // let's process it
            request[n_bytes] = '\0';
            printf ("Received %s\n", request);
            quit = handle_msg(request, sockfd);
        }
    }
    return 0;
}
