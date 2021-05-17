#ifndef PROCESSREQUEST_H
#define PROCESSREQUEST_H

typedef struct{
    char server_root[30];
    char server_signature[40];
    char max_clients[30];
    char port[30];
}config;



config getServerConfig();
void options(int cliente, char* buffer);
void badRequest(int cliente, char* buffer);
void notFound(int cliente, char* buffer);
void *parseaRequest(void *clientfd);
char* comprobar_tipo(char* file, size_t file_len);
void changePostPetition(size_t* path_len, char* path_root, char* buffer);
void* processRequest(int client, char* buffer, const char* path, const char* method, size_t path_len, int version);
#endif
