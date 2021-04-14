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
#include "picohttpparser.h"

#define MAX_BUFFER 16384


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
const char* dias[7]= {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};

config configu;


config getServerConfig(){
    FILE* c;
    int i;
    char* string;
    c=fopen("server.conf", "r");
    string = malloc(sizeof(configu.server_root)*sizeof(char));
    fgets(string, sizeof(configu.server_root), c);
    strtok(string, "=");
    strcpy(configu.server_root, strtok(NULL, "="));
    free(string);
    configu.server_root[strlen(configu.server_root)-1] = '\0';

    string = malloc(sizeof(configu.max_clients)*sizeof(char));
    fgets(string, sizeof(configu.max_clients), c);
    strtok(string, "=");
    strcpy(configu.max_clients, strtok(NULL, "="));
    free(string);

    string = malloc(sizeof(configu.listen_port)*sizeof(char));
    fgets(string, sizeof(configu.listen_port), c);
    strtok(string, "=");
    strcpy(configu.listen_port, strtok(NULL, "="));
    free(string);

    string = malloc(sizeof(configu.server_signature)*sizeof(char));
    fgets(string, sizeof(configu.server_signature), c);
    strtok(string, "=");
    strcpy(configu.server_signature, strtok(NULL, "="));
    free(string);

    fclose(c);
    return configu;
}



void *processRequest(void *clientfd){
    configu = getServerConfig();
    struct phr_header headers[500];
    struct sockaddr_in client_address;
    struct stat filestat;
    time_t tim = time(NULL);
    struct tm *t_stand = localtime(&tim);
    struct tm *last_modification;
    int client= *(int*)clientfd;
    int parse_return, minor_version, flag=0, len_arch, file_id, file_length;
    const char * method, *path;
    socklen_t addrlen = sizeof(client_address);
    size_t num_headers, method_len, path_len;
    ssize_t recv_size, buffer_len=0, previous_buffer_len=0;
    char buffer[MAX_BUFFER], path_root[MAX_BUFFER], path_file[MAX_BUFFER], path_file_aux[MAX_BUFFER], tipo[20], script[50], script_2[50];
    memset(buffer, '\0', MAX_BUFFER);
    memset(path_root, '\0', MAX_BUFFER);
    memset(path_file, '\0', MAX_BUFFER);
    memset(path_file_aux, '\0', MAX_BUFFER);

    pthread_detach(pthread_self());
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
            badRequest(client, buffer);
        }

        if (parse_return == -2 && buffer_len == sizeof(buffer)){
            badRequest(client, buffer);
        }
    }
    strcpy(path_root, configu.server_root);

    if(!strncmp(path, "/", path_len)){
        strcat(path_root, "/index.html");
        path_len=strlen(path_root);
    }
    else{
        strncat(path_root, path, path_len);
        path_len=strlen(path_root);
    }

    if(!strncmp(method, "OPTIONS", 7) || !strncmp(method, "options", 7)){
        options(client, buffer);
    }

    if(!strncmp(method, "POST", 4) || !strncmp(method, "post", 4)){
        char* mensaje = strstr(buffer, "\r\n\r\n"); //MENSAJE????
        mensaje += 4*sizeof(char);
        if(!strstr(path_root, "?")){
            strcat(path_root, "?");
        }
        else{
            strcat(path_root, "&");
        }
        strcat(path_root, mensaje);
        path_len += 1 + strlen(mensaje);
    }
    strcpy(script_2, path_root);
    strcpy(script, strtok(script_2, "?"));

    if(!strcmp(script+strlen(script)-3, ".py") || !strcmp(script+strlen(script)-4, ".php")){
        char command[MAX_BUFFER];

        if(!strcmp(script+strlen(script)-3, ".py"))
            strcpy(command, "python3 ");
        else
            strcpy(command, "php ");

        strcat(command, script);
        while(strtok(NULL, "=")!=NULL){
            strcat(command, " ");
            strcat(command, strtok(NULL, "&"));
        }

        strcat(command, " > ./files/output.txt");
        if(system(command)==-1){
            badRequest(client, buffer);
        }
        else
            flag = 1;
        
        strcpy(path_file, "./files/output.txt");
    }
    else{
        strcpy(path_file_aux, path_root);
        strcpy(path_file, strtok(path_file_aux, "?"));
    }
    path_len = strlen(path_file);

    if(stat(path_file, &filestat) < 0){
        notFound(client, buffer);
    }

    last_modification = gmtime(&filestat.st_mtime);
    strcpy(tipo, "not_defined");

    for(int i = 0; i < 11; i++){
        len_arch = strlen(tipos[i].arch);

        if(!strncmp(path_file + path_len - len_arch, tipos[i].arch, len_arch)){
            strcpy(tipo, tipos[i].tipo);
            break;
        }
    }

    if(!strcmp(tipo, "not_defined")){
        if(flag==1){
            system("rm ./files/output.txt");
        }
        badRequest(client, buffer);
    }

    file_id = open(path_file, O_RDONLY);
    if (file_id == -1){
        if(flag == 1)
            system("rm ./files/output.txt");
        notFound(client, buffer);

    }

    file_length = lseek(file_id, 0, SEEK_END);
    lseek(file_id, 0, SEEK_SET);

    sprintf(buffer, "HTTP/1.%d 200 OK\r\n"
                    "Server: %s\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Last-Modified: %s, %d %s %d %d:%d:%d\r\n"
                    "Content-Lenght: %d\r\n"
                    "Content-Type: %s\r\n\r\n",
            minor_version,
            configu.server_signature,
            dias[t_stand->tm_wday],
            t_stand->tm_mday, meses[t_stand->tm_mon], t_stand->tm_year + 1900,
            t_stand->tm_hour, t_stand->tm_min, t_stand->tm_sec,
            dias[last_modification->tm_wday],
            last_modification->tm_mday, meses[last_modification->tm_mon], last_modification->tm_year + 1900,
            last_modification->tm_hour, last_modification->tm_min, last_modification->tm_sec,
            file_length,
            tipo);

    send(client, buffer, strlen(buffer), 0);

    while ((file_length = read(file_id, buffer, MAX_BUFFER))>0){
        send(client, buffer, file_length, 0);
    }

    close(file_id);
    sleep(1);
    if (flag==1){
        system("rm ./files/output.txt");
    }
    close(client);
    pthread_exit(NULL);
}

//FUNCIONES DE RESPUESTA

void options(int cliente, char* buffer){
    time_t tim = time(NULL);
    int minor_version = -1;
    struct tm *t_stand = localtime(&tim);
    sprintf(buffer, "HTTP/1.%d 200 OK\r\n"
                    "Server:%s\r\n"
                    "Allow: OPTIONS, GET, POST\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Content-Lenght:%d\r\n\r\n",
            minor_version,
            configu.server_signature,
            dias[t_stand->tm_wday],
            t_stand->tm_mday, meses[t_stand->tm_mon], t_stand->tm_year + 1900,
            t_stand->tm_hour, t_stand->tm_min, t_stand->tm_sec,
            0);
    send(cliente, buffer, strlen(buffer), 0);
    close(cliente);
    pthread_exit(NULL);
}

void badRequest(int cliente, char* buffer){
    time_t tim = time(NULL);
    int minor_version = -1;
    struct tm *t_stand = localtime(&tim);
    sprintf(buffer, "HTTP/1.%d 400 Bad Request\r\n"
                    "Server:%s\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Connection: Closed\r\n"
                    "Content-Lenght:%d\r\n"
                    "Content-Type: text/plain\r\n\r\n"
                    "Bad Request",
            minor_version,
            configu.server_signature,
            dias[t_stand->tm_wday],
            t_stand->tm_mday, meses[t_stand->tm_mon], t_stand->tm_year + 1900,
            t_stand->tm_hour, t_stand->tm_min, t_stand->tm_sec,
            11);
    send(cliente, buffer, strlen(buffer), 0);
    close(cliente);
    pthread_exit(NULL);

}

void notFound(int cliente, char* buffer){
    time_t tim = time(NULL);
    int minor_version = -1;
    struct tm *t_stand = localtime(&tim);
    sprintf(buffer, "HTTP/1.%d 404 Not Found\r\n"
                    "Server:%s\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Connection: Closed\r\n"
                    "Content-Lenght:%d\r\n"                  
                    "Content-Type: text/plain\r\n\r\n"
                    "Not Found",
            minor_version,
            configu.server_signature,
            dias[t_stand->tm_wday],
            t_stand->tm_mday, meses[t_stand->tm_mon], t_stand->tm_year + 1900,
            t_stand->tm_hour, t_stand->tm_min, t_stand->tm_sec,
            9);
    send(cliente, buffer, strlen(buffer), 0);
    close(cliente);
    pthread_exit(NULL);

}

