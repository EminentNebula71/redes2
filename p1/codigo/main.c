#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <assert.h>
#include <pthread.h>

/*NADIE SABE QUE HACER AQUI⠀⠀⠀⠀⠀⠀
NO ESTA BIEN HECHO*/


int main(int argc, char ∗∗argv){
    int listenfd, connfd, child, socketfd, bind_result;
    socklen_t clilen, addrlen;
    struct sockaddr ∗cliaddr;
    struct sockaddr_in watashi_no_aduresu;
    config config;
    pthread_t thread_id;

    config = getServerConfig();

    /*SOCKET*/
    if(socketfd = socket(AF_INET, SOCK_STREAM, 0) < 0){
        fprintf(stdout, "Error. El socket no se ha abierto correctamente");
        return -1;
    }

    /*BIND*/
    watashi_no_aduresu.sin_family = AF_INET;
    watashi_no_aduresu.sin_port = htons(atoi(config.listen_port));
    watashi_no_aduresu.sin_addr.s_addr = INADDR_ANY;

    if (bind(socketfd, (struct sockaddr *)&watashi_no_aduresu, sizeof(watashi_no_aduresu)) == -1){
        fprintf(stdout, "Error al hacer el bind\n");
        printf("%s\n", strerror(errno));
        return -2;
    }

    /*LISTEN*/
    if (listen(sockfd, atoi(config.max_clientes)) != 0){
        perror("Error al hacer el listen");
        exit(errno);
    }
    
    /*MISTERIO A TERMINAR*/
    for ( ; ; ) {
        connfd = Accept(listenfd, cliaddr, &clilen);
        pthread_create(&thread_id, NULL, FUNCIÓN QUE CREEMOS, (void *)&connfd);
        }

    /* Padre cierra el descriptor de la conexion del hijo (duplicada) */
    }
    close(socketfd);
    return 0;
 }


/********
* FUNCIÓN: do_daemon()
* DESCRIPCIÓN: Activa el modo daemon del servidor
********/
void do_daemon()
{
    pid_t pid;

    pid = fork();

s    if (pid > 0)
        exit(EXIT_SUCCESS); //Si es el proceso padre lo cerramos
    if (pid < 0)
        exit(EXIT_FAILURE); //Si hay error en el fork salimos

    umask(0);
    setlogmask(LOG_UPTO(LOG_INFO)); //Open logs here
    openlog("Server system messages:", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL3);
    syslog(LOG_ERR, "Initiating new server.");

    if (setsid() < 0)
    {
        syslog(LOG_ERR, "Error creando un nuevo SID para el proceso hijo.");
        exit(EXIT_FAILURE);
    }

    if (chdir("/") < 0)
    {
        syslog(LOG_ERR, "Error cambiando el directorio actual uwu = \"/\"");
        exit(EXIT_FAILURE);
    }

    syslog(LOG_INFO, "Cerrando los descriptores de ficheros estandar");
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
}