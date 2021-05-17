import socket
import DS
import user_info
import practica3_client
from appJar import gui
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
from video import Video

global send_check
send_check = None

BUFF = 4096

def call(gui, user_called, cap):
    #user_called es la respuesta de la query, en un array separado por espacios
    #tener en cuenta que 0 y 1 son OK y USER_FOUND
    user = user_info.get_user_info()

    called_user_address = (user_called[3], int(user_called[4]))
    message = 'CALLING ' + user['nick'] + ' ' + str(user['port'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if user['nick'] == user_called[2]:
        gui.app.infoBox('Llamada denegada.', 'Solo los locos hablan con ellos mismos.')
        return None
    sock.connect(called_user_address)
    sock.send(message.encode())

    response = sock.recv(BUFF).decode()

    sock.close()

    response_split = response.split(' ')

    if response_split[0] == 'CALL_ACCEPTED':
        user_info.set_called_user(user_called[2], user_called[3], user_called[4])
        
        llamada = Video(gui, cap)
        llamada.start()

    elif response_split[0] == 'CALL_DENIED':
        gui.app.infoBox('Llamada denegada.', 'El usuario '+ user_called[2]+ ' no ha aceptado la llamada.')
        return None
    else:
        gui.app.infoBox('Llamada denegada.', 'El usuario '+ user_called[2]+ ' esta ya en llamada con otra persona.')
        return None
    
    return None

def hold_call():
    user = user_info.get_user_info()
    called_user = user_info.get_called_user()

    message = 'CALL_HOLD ' + user['nick']
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (called_user['ip'], int(called_user['port']))

    sock.connect(server_address)

    sock.send(message.encode())
    sock.close()


def resume_call():
    
    user = user_info.get_user_info()
    called_user = user_info.get_called_user()

    message = 'CALL_RESUME ' + user['nick']

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    called_user_address = (called_user['ip'], int(called_user['port']))

    sock.connect(called_user_address)

    sock.send(message.encode())
    sock.close()

def end_call():

    user = user_info.get_user_info()
    called_user = user_info.get_called_user()

    message = "CALL_END " + user['nick']

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    called_user_address = (called_user['ip'], int(called_user['port']))

    sock.connect(called_user_address)

    sock.send(message.encode())

    sock.close()



def wait_call(gui, sock, cap):
    user = user_info.get_user_info()
    sock.listen()

    while 1:
        connection, address = sock.accept()
        peticion = connection.recv(4096)
        peticion_split = peticion.decode().split(' ')
        if peticion_split[0] == 'CALLING':
            if not user_info.enLlamada:
                llamada_aceptada = gui.app.yesNoBox('Llamada entrante', 'Estas recibiendo una llamada de '+ peticion_split[1] + " ¿Aceptar?")
                if llamada_aceptada == False:
                    message = 'CALL_DENIED ' + user['nick']
                    connection.send(message.encode())
                else:
                    message = 'CALL_ACCEPTED ' + user['nick'] + ' ' + user['port']
                    connection.send(message.encode())
                    called_user = DS.query(peticion_split[1])
                    called_user = called_user.split(' ')
                    user_info.set_called_user(called_user[2], called_user[3], called_user[4])
                    llamada = Video(gui, cap)
                    llamada.start()
            else:
                message = 'CALL_BUSY'
                connection.send(message.encode())
        elif peticion_split[0] == 'CALL_HOLD':
            user_info.enPausa = True
        elif peticion_split[0] == 'CALL_RESUME':
            user_info.enPausa = False
        elif peticion_split[0] == 'CALL_END':
            user_info.enLlamada = False
            gui.app.stopSubWindow()
            gui.app.show()

    connection.close()






#

 