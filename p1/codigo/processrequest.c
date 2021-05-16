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

//constantes de tiempo para las respuestas de las peticiones
const char* meses[12]= {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
const char* dias[7]= {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};

config configu;

//Coge la informacion del fichero para poder facilitar la conexion con el server
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


//Esta funcion procesa la peticion es compleja, asi que la vamos a dividir en partes
void *processRequest(void *clientfd){
    configu = getServerConfig();
    struct phr_header headers[500];
    struct sockaddr_in client_address;
    struct stat filestat;
    time_t tim = time(NULL);
    struct tm *t_stand = localtime(&tim);
    struct tm *last_modification;
    int client= *(int*)clientfd;
    int parse_return, version, flag=0, file_id, file_length;
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
    //recibimos y parseamos la peticion
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
                                         &version, headers, &num_headers, previous_buffer_len);

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
    
    //Modificamos el path
    if(!strncmp(path, "/", path_len)){
        strcat(path_root, "/index.html");
        path_len=strlen(path_root);
    }
    else{
        strncat(path_root, path, path_len);
        path_len=strlen(path_root);
    }

    //Aqui observamos que metodo es el que quiere hacer la peticion y llamar a la respuesta correspondiente
    //Caso de Options
    if(!strncmp(method, "OPTIONS", 7) || !strncmp(method, "options", 7)){
        options(client, buffer);
    }

    //Caso de Post, convertimos la peticion en una peticion get
    if(!strncmp(method, "POST", 4) || !strncmp(method, "post", 4)){
        changePostPetition(&path_len, path_root, buffer);
    }


    //Obtenemos el nombre del script, en caso de haberlo
    strcpy(script_2, path_root);
    strcpy(script, strtok(script_2, "?"));
    //Miramos si es python o php
    if(!strcmp(script+strlen(script)-3, ".py") || !strcmp(script+strlen(script)-4, ".php")){
        char command[MAX_BUFFER];
        //En caso de ser python ponemos python3 al principio del comando
        if(!strcmp(script+strlen(script)-3, ".py"))
            strcpy(command, "python3 ");
        //En caso de ser php ponemos php al principio del comando
        else
            strcpy(command, "php ");
        //Le metemos el script para realizar su ejecucion
        strcat(command, script);
        while(strtok(NULL, "=")!=NULL){
            strcat(command, " ");
            strcat(command, strtok(NULL, "&"));
        }

        strcat(command, " > ./files/output.txt");
        //Si falla hacemos badRequest
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
    
    strcpy(tipo, comprobar_tipo(path_file, path_len));

    if(!strcmp(tipo, "not_defined")){
        if(flag==1){
            system("rm ./files/output.txt");
        }
        badRequest(client, buffer);
    }
    //abrimos el archivo, si no lo logramos, pero antes hemos marcado que se ha creado hacemos el comando de borrado
    // y devolvemos notFound
    file_id = open(path_file, O_RDONLY);
    if (file_id == -1){
        if(flag == 1)
            system("rm ./files/output.txt");
        notFound(client, buffer);
    }

    file_length = lseek(file_id, 0, SEEK_END);
    lseek(file_id, 0, SEEK_SET);
    //estructura de repuesta correcta
    sprintf(buffer, "HTTP/1.%d 200 OK\r\n"
                    "Server: %s\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Last-Modified: %s, %d %s %d %d:%d:%d\r\n"
                    "Content-Lenght: %d\r\n"
                    "Content-Type: %s\r\n\r\n",
            version,
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

//FUNCIONES DE APOYO

char* comprobar_tipo(char* file, size_t file_len){
    char *tipo = malloc (sizeof (char) * 20);;
    int len_arch;
    strcpy(tipo, "not_defined");
        for(int i = 0; i < 11; i++){
            len_arch = strlen(tipos[i].arch);
            if(!strncmp(file + file_len - len_arch, tipos[i].arch, len_arch)){
                strcpy(tipo, tipos[i].tipo);
                break;
            }
        }
    return tipo;
}


void changePostPetition(size_t* path_len, char* path_root, char* buffer){
    char* mensaje = strstr(buffer, "\r\n\r\n"); 
        mensaje += 4*sizeof(char);
        if(!strstr(path_root, "?")){
            strcat(path_root, "?");
        }
        else{
            strcat(path_root, "&");
        }
        strcat(path_root, mensaje);
       *path_len += 1 + strlen(mensaje);
}


//FUNCIONES DE RESPUESTA

void options(int cliente, char* buffer){
    time_t tim = time(NULL);
    int version = 0;
    struct tm *t_stand = localtime(&tim);
    sprintf(buffer, "HTTP/1.%d 200 OK\r\n"
                    "Server:%s\r\n"
                    "Allow: OPTIONS, GET, POST\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Content-Lenght:%d\r\n\r\n",
            version,
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
    int version = 0;
    struct tm *t_stand = localtime(&tim);
    sprintf(buffer, "HTTP/1.%d 400 Bad Request\r\n"
                    "Server:%s\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Connection: Closed\r\n"
                    "Content-Lenght:%d\r\n"
                    "Content-Type: text/plain\r\n\r\n"
                    "Bad Request",
            version,
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
    int version = 0;
    struct tm *t_stand = localtime(&tim);
    sprintf(buffer, "HTTP/1.%d 404 Not Found\r\n"
                    "Server:%s\r\n"
                    "Date: %s, %d %s %d %d:%d:%d\r\n"
                    "Connection: Closed\r\n"
                    "Content-Lenght:%d\r\n"                  
                    "Content-Type: text/plain\r\n\r\n"
                    "Not Found",
            version,
            configu.server_signature,
            dias[t_stand->tm_wday],
            t_stand->tm_mday, meses[t_stand->tm_mon], t_stand->tm_year + 1900,
            t_stand->tm_hour, t_stand->tm_min, t_stand->tm_sec,
            9);
    send(cliente, buffer, strlen(buffer), 0);
    close(cliente);
    pthread_exit(NULL);

}
