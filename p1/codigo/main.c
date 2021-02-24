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

/*NADIE SABE QUE HACER AQUI
NO ESTA BIEN HECHO*/
int main(int argc, char ∗∗argv){
    int listenfd, connfd;
    socklen_t clilen, addrlen;
    struct sockaddr ∗cliaddr;
    
    /* Contiene las llamadas a socket(), bind() y listen() */
    listenfd = Tcp_listen(argv[1], argv[2], &addrlen);
 
    for ( ; ; ) {
        connfd = Accept(listenfd, cliaddr, &clilen);
        if ( (childpid = Fork()) == 0) {
            process_request(connfd); /* Procesa la peticion */
        exit(0); 
        }

    /* Padre cierra el descriptor de la conexion del hijo (duplicada) */
    Close(connfd);
    }
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