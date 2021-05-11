import sys
import socket

BUFFER = 4096
configuration = open('./config.conf', 'r')
host_server = configuration.readlines(1)
host_server = str(host_server[14:28])
#Prueba de que hicimos bien el coger el nombre
print(host_server) 
port = configuration.readlines(1)
port = str(port[7:11])
#Prueba de que hicimos bien el coger el nombre
print(port) 
configuration.close()
server_info = (host_server, int(port))

#Protocolo 0?? Indicar nosotros

def sendToServer(message):
    server_socket = socket.socket()
    server_socket.connect(server_info)

    server_socket.send(message.encode())
    resp = server_socket.recv(BUFFER).decode()
    quit(server_socket)
    server_socket.close()
    return resp

def register(nick, ip_address, port, password, protocol):

    if not (nick and ip_address and port and password and protocol):
        return "NOK WRONG_PASS"

    message = 'REGISTER ' + nick +' '+ ip_address +' '+ port +' '+ password +' '+ protocol

    resp = sendToServer(message)
    
    return resp




def query(name):
    if not name:
        return "NOK USER_UNKNOWN"

    message = 'QUERY ' + name

    resp = sendToServer(message)
    
    return resp



def list_users():
    message = 'LIST_USERS'
    resp = sendToServer(message)
    print(resp) #Comprobacion de formato de devuelta de usuarios

    resp_check = resp.split(' ')
    
    if resp_check[0] == 'NOK':
        return None
    resp_split = resp.split('#')
    nick1 = resp_split[0].split(' ')[2]
    
    all_nicks = nick1 + '\n' #O ' ' para separar nicks
    for user in resp_split[1:]:
        all_nicks += user  + '\n' #O ' ' para separar nicks


    return all_nicks


def quit(server_socket):
    message = 'QUIT'
    server_socket.send(message.encode())
    resp = server_socket.recv(BUFFER).decode()