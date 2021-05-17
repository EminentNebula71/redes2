import videollamada
import DS
from practica3_client import VideoClient
import user_info
import cv2
import socket
import numpy as np
from PIL import Image, ImageTk
import threading
import sys
import time

global check
check = 0

class Video(object):

    def __init__(self, gui, cap):
        global check
        self.gui = gui.app
        self.cap = cap
        self.frame_enviado = None
        if check is 0:
            self.gui.startSubWindow("Llamada", modal= True)
            self.gui.setSize(640, 250)
            self.gui.addImage("webcam", "img/webcam.gif")
            self.gui.addButtons(["Pausar", "Reanudar", "Colgar"], self.buttonsCallback)
            self.gui.stopSubWindow()
            check = 1

    def start(self):
        self.gui.hideImage("video1")
        self.gui.hide()
        self.gui.showSubWindow("Llamada")

        user_info.enLlamada = True

        self.envio = threading.Thread(target=self.envioVideo, args=(), daemon= True)
        self.envio.start()
        self.recepcion = threading.Thread(target=self.recibirVideo, args=(), daemon= True)
        self.recepcion.start()


    def envioVideo(self):
        called_user = user_info.get_called_user()
        called_user_address = (called_user['ip'], int(called_user['port']))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        

        while user_info.enLlamada:
            if self.cap != None:
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640,480))
                self.frame_enviado = cv2.resize(frame, (640,480))
                param_codificado = [cv2.IMWRITE_JPEG_QUALITY, 50]
                result, encimg = cv2.imencode('.jpg', frame, param_codificado)
                if result == False:
                    print('Error al codificar la imagen')
                encimg = encimg.tobytes()
                sock.sendto(encimg, called_user_address)
        sock.close()
        return "OK"

    def recibirVideo(self):

        user = user_info.get_user_info()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((user['ip'], int(user['port'])))

        while user_info.enLlamada:
            data, address = sock.recvfrom(60000)
            decimg = cv2.imdecode(np.frombuffer(data, np.uint8),1)
            frame = cv2.resize(decimg, (640,480))
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(image = Image.fromarray(cv2_im))
            self.gui.setImageData("webcam", img_tk, fmt="PhotoImage")
            while user_info.enPausa:
                time.sleep(0.1)
        sock.close()            
        return "OK"

    def buttonsCallback(self, button):
        if button == "Pausar":
            user_info.enPausa = True
            videollamada.hold_call()

        elif button == "Reanudar":
            user_info.enPausa= False
            videollamada.resume_call()

        elif button == "Colgar":
            user_info.enLlamada= False
            videollamada.end_call()
            time.sleep(0.1)
            self.gui.hideImage("webcam")
            self.gui.showImage("video1")
            self.gui.show()
            self.gui.hideSubWindow("Llamada")
            