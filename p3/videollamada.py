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
    #user_called es la respuesta de la query, en un array separado por espacios
    #tener en cuenta que 0 y 1 son OK y USER_FOUND
    user = user_info.get_user_info()

    called_user_address = (user_called[3], user_called[4])

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
        call_window(gui)
        user_info.set_called_user(user_called)
        captura_video = threading.Thread(target=capturaVideo, args=(gui, called_user_address))
        captura_video.start()
        proceso_llamada = threading.Thread(target=proceso_llamada, args=(gui, called_user_address))
        proceso_llamada.start()


    elif response_split[0] == 'CALL_DENIED':
        gui.app.infoBox('Llamada denegada.', 'El usuario '+ user_called['nick']+ ' no ha aceptado la llamada.')
        return None
    else:
        gui.app.infoBox('Llamada denegada.', 'El usuario '+ user_called['nick']+ ' esta ya en llamada.')
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
        frame = cv2.resize(decimg, (640,480))

        cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(image = Image.fromarray(cv2_im))

        gui.app.setImageData("video1", img_tk, fmt="PhotoImage")

    sock.close()            


# La hemos movido aqui porque es mas coherente que este con los elementos de videollamada
def capturaVideo(gui, called_user_address):
		
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        cap.open()
    while user_info.enLlamada and user_info.on:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640,480))
        param_codificado = [cv2.IMWRITE_JPEG_QUALITY, 50]
        result, encimg = cv2.inmencode('.jpg', frame, param_codificado)
        encimg = encimg.tobytes()

        sock.sendto(encimg, called_user_address)
    sock.close()



def wait_call(gui, sock):
    user = user_info.get_user_info()

    sock.listen(1)

    while 1 and user_info.on:
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
                    call_window(gui)
                    called_user = DS.query(peticion_split[1])
                    user_info.set_called_user(called_user)

                    called_user_address = (called_user['ip'], int(called_user['port']))
                    captura_video = threading.Thread(target=capturaVideo, args=(gui, called_user_address),daemon=True)
                    captura_video.start()
                    proceso_llamada = threading.Thread(target=proceso_llamada, args=(gui, called_user_address),daemon=True)
                    proceso_llamada.start()
            else:
                message = 'CALL_BUSY'
                connection.send(message.encode())
        elif peticion_split[0] == 'CALL_HOLD':
            user_info.enPausa = True
        elif peticion_split[0] == 'CALL_RESUME':
            user_info.enPausa = False
        elif peticion_split[0] == 'CALL_END':
            user_info.enLlamada = False
            gui.app.show()
            gui.app.hideSubWindow("LLamada en curso")

    connection.close()
 