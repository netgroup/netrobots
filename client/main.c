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


void get_action(char *status, char *my_action) {
    static char my_dir = 'u';
    char dirs[] = {'u', 'd', 'l', 'r'};
    int reach_border,
        can_fire,
        shuttle_n,
        x,
        y;
    float random_angle = 0.0;
    sscanf(status, "%d %d %d %d", &can_fire, &shuttle_n, &x, &y);


    if (can_fire) {
        random_angle = (rand() % 36000);
        random_angle /= 100;
        sprintf(my_action, "f %f", random_angle);
        return;
    }

    switch (my_dir) {
        case 'u':
            reach_border = (y == arena_size);
            break;
        case 'd':
            reach_border = (y == 0);
            break;
        case 'l':
            reach_border = (x == 0);
            break;
        case 'r':
            reach_border = (x == arena_size);
            break;
    }

    printf("reach_border is %d\n", reach_border);
    printf("x is %d\n", x);
    printf("y is %d\n", y);
    printf("arena_size is %d\n", arena_size);
    printf("(y == arena_size) is %d\n", (y == arena_size));

    if (reach_border) {
        my_dir = dirs[rand()%4];
    } 
    sprintf(my_action, "m %c", my_dir);
}


// TODO add comments
int handle_msg(char recvline[MAX_RX_BUF], int sockfd) {

    char sendline[MAX_TX_BUF];
    int sent_bytes = -1;
    printf("first char is %c\n", recvline[0]);

    switch(recvline[0]) {
        case REQUEST_QUIT:
            // the server ask us to quit, just return
            return 1;
        case REQUEST_NAME:
            // server ask for our name
            // answer "n YOURNAME\"
            printf("Server ask for my name...\n");
            strcpy(sendline, "n lorenzo");
            // it give us the dimension of the arena expressed in number of tiles
            // of each edge of the square area.
            sscanf(&recvline[2], "%d", &arena_size);
            printf("Arena size is %d\n", arena_size);
            // arena is a square arena_size X arena_size
            break;
        case REQUEST_ACTION:
            
            printf("Server ask for action...\n");
            // for our convenience, the server send us the positions of other shuttles
            // in the list we are the first one
            // it send to us also the position of rockets sent by other spacecraft

            // TODO Add if I can fire a rocket
            // the format is
            // CAN_FIRE NUMBER_OF_SPACESHIPS X1 Y1 X2 Y2 X3 Y3 ... NUMBER_OF_ROCKETS X1 Y1 A1 X2 Y2 A2 ...
            // e.g. 3 120 234 45 87 98 67 1 10 100 282.23
            // there are three shuttles. We are at coords (120, 234), there is a rocket at (10, 100)


            // we can decide where to move
            // we can move up (u), down (d), left (l) or right (r)
            // just answer "m u" to go up or "m l" to go left
            
            get_action(&recvline[2], sendline);

            // alternatively, we can also decide to fire
            // syntax is f ANGLE where angle is a float
            //sprintf(sendline, "f %f", 271.32);
            break;


    }
    strcat(sendline, "\r\n"); //add endline
    sent_bytes = send(sockfd, sendline, strlen(sendline), 0); //send to the server
    printf("Sent %d bytes\n", sent_bytes);

    return 0;
}

int main(int argc, char**argv)
{
    int sockfd,n_bytes;
    struct sockaddr_in servaddr,cliaddr;
    char recvline[MAX_RX_BUF];
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
        n_bytes = recv(sockfd, recvline, sizeof(recvline) - 1, 0);

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
            recvline[n_bytes] = '\0';
            printf ("Received %s\n", recvline);
            quit = handle_msg(recvline, sockfd);
        }
    }
    return 0;
}
