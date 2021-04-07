#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <semaphore.h>
#include <arpa/inet.h>
#include <errno.h>
#include <time.h>
#include <resolv.h>
#include <unistd.h>
#include <syslog.h>
#include <pthread.h>
#include <assert.h>
#include "processrequest.h"
#include "../librerias/picohttpparser.h"

struct
{
    char *tipo;
    char *arch;
} tipos[] = {
    {"text/plain", "txt"},
    {"text/html", "html"},
    {"text/html", "htm"},
    {"image/gif", "gif"},
    {"image/jpeg", "jpeg"},
    {"image/jpeg", "jpg"},
    {"video/mpeg", "mpeg"},
    {"video/mpeg", "mpg"},
    {"application/msword", "doc"},
    {"application/msword", "docx"},
    {"application/pdf", "pdf"}
    };


const char* meses[12]= {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
const char* dias[7]= {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"};




config getServerConfig(){
    config config;
    FILE* c;
    int i;
    char* string;
    c=fopen("server.conf", "r");
    string = malloc(sizeof(config.server_root)*sizeof(char));
    fgets(string, sizeof(config.server_root), c);
    strtok(string, "=");
    strcpy(config.server_root, strtok(NULL, "="));
    free(string);

    string = malloc(sizeof(config.max_clients)*sizeof(char));
    fgets(string, sizeof(config.max_clients), c);
    strtok(string, "=");
    strcpy(config.max_clients, strtok(NULL, "="));
    free(string);

    string = malloc(sizeof(config.listen_port)*sizeof(char));
    fgets(string, sizeof(config.listen_port), c);
    strtok(string, "=");
    strcpy(config.listen_port, strtok(NULL, "="));
    free(string);

    string = malloc(sizeof(config.server_signature)*sizeof(char));
    fgets(string, sizeof(config.server_signature), c);
    strtok(string, "=");
    strcpy(config.server_signature, strtok(NULL, "="));
    free(string);

    fclose(c);
    return config;
}


void *processRequest(void *clientfd){
    config config = getServerConfig();
    struct phr_header headers[500];
    struct sockaddr client_address;
    int client= *(int*)clientfd;
    int parse_return, minor_version;
    const char * method, *path;
    socklen_t addrlen = sizeof(clientfd);
    size_t num_headers, method_len, path_len;
    ssize_t recv_size, buffer_len, previous_buffer_len;
    char buffer[16384];


    getpeername(client, (struct sockaddr *)&client_address ,&addrlen);

    while(1){
        recv_size = recv(client, buffer, sizeof(buffer)-1, 0);
        if (recv_size<=0){
            close(client);
            pthread_exit(NULL);
        }
        previous_buffer_len = buffer_len;
        buffer_len += recv_size;
        num_headers = 500;

        parse_return = phr_parse_request(buffer, buffer_len, &method, &method_len, &path, &path_len,
                                         &minor_version, headers, &num_headers, previous_buffer_len);

        if (parse_return >0)
            break;
        else if (parse_return==-1) {
            //badRequest() CREAR
        }

        if (parse_return == -2 && buffer_len == sizeof(buffer)){
            //badRequest()
        }
    }

    //CONTINUAR
}