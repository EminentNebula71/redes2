import sys
import socket

BUFFER = 4096
configuration = open('./config.conf', 'r')
host_server = configuration.readlines(1)
host_server = str(host_server)[16:30]

port = configuration.readlines(1)
port = str(port)[9:13]
configuration.close()

server_info = (host_server, int(port))


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
    flag = 0
    message = 'LIST_USERS'
    resp = sendToServer(message)
    #COMPROBADO QUE NOS INTERESAN LOS PARAMETROS 1,2 y 3 de users para nick, ip y port respectivamente
    resp_check = resp.split(' ')
    
    if resp_check[0] == 'NOK':
        return None
    resp_split = resp.split('#')
    
    user1 = resp_split[0].split(' ')
    info = user1[3] + ' ' + user1[4] + ' ' + user1[5] + '\n' #\n para separar por lineas
    for x in resp_split[1:]:
        if flag < 10:
            user = x.split(' ')
            info += user[0] + ' ' + user[1] + ' ' + user[2] + '\n' 
            flag +=1

    return info


def quit(server_socket):
    message = 'QUIT'
    server_socket.send(message.encode())
    resp = server_socket.recv(BUFFER).decode()