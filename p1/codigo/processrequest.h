#ifndef PROCESSREQUEST_H
#define PROCESSREQUEST_H

typedef struct{
    char server_root[30];
    char server_signature[40];
    char max_clients[30];
    char listen_port[30];

}config;


config getServerConfig();
void options(int cliente, char* buffer);
void badRequest(int cliente, char* buffer);
void notFound(int cliente, char* buffer);
void *processRequest(void *clientfd);
#endif

