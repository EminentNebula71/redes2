import socket
import DS
import user_info
import practica3_client
from appJar import gui
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk

BUFF = 4096

def call(gui, user_called):
    user = user_info.get_user_info()

    called_user_address = (user_called['ip'], user_called['port'])

    message = 'CALLING ' + user['nick'] + ' ' + str(user['port'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if user['nick'] == user_called['nick']:
        gui.app.infoBox('Llamada denegada.', 'Solo los locos hablan con ellos mismos.')
        return None

    sock.connect(called_user_address)
    print(message)
    sock.send(message.encode())

    response = sock.recv(BUFF).decode()

    sock.close()

    response_split = response.split(' ')

    if response_split[0] == 'CALL_ACCEPTED':
        call_window(gui)
        user_info.set_called_user(user_called)
        captura_video = threading.Thread(target=practica3_client.capturaVideo, args=(gui, called_user_address),daemon=True)
        captura_video.start()
        proceso_llamada = threading.Thread(target=proceso_llamada, args=(gui, called_user_address),daemon=True)
        proceso_llamada.start()


    elif response_split[0] == 'CALL_DENIED':
        gui.app.infoBox('Llamada denegada.', 'El usuario '+ user_called['nick']+ ' no quiere hablar contigo, esta con el free fire.')
        return None
    else:
        gui.app.infoBox('Llamada denegada.', 'El usuario '+ user_called['nick']+ ' esta ocupado en duo en el apex con otra persona')
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


def call_window(gui):
    user_info.enLlamada = True

    gui.app.hide()
    gui.app.showSubWindow("Llamada en curso")


def proceso_llamada(gui):
    user = user_info.get_user_info()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((user['ip'], int(user['port'])))

    while user_info.enLlamada and user_info.on:
        data, address = sock.recvfrom(60000)
        decimg = cv2.imdecode(np.frombuffer(data, np.uint8),1)
        frame = cv2.resize(decimg, (480,360))

        cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(image = Image.fromarray(cv2_im))

        gui.app.setImageData("video1", img_tk, fmt="PhotoImage")

    sock.close()            


