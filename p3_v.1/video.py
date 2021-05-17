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

class Video(object):

    def __init__(self, gui, cap):
        self.gui = gui.app
        self.cap = cap
        self.frame_enviado = None
        self.gui.startSubWindow("Llamada en curso", modal= True)
        self.gui.setSize(640, 250)
        self.gui.addImage("webcam", "img/webcam.gif")
        self.gui.addButtons(["Pausar", "Reanudar", "Colgar"], self.buttonsCallback)
        self.gui.stopSubWindow()

    def start(self):
        self.gui.hideImage("video1")
        self.gui.hide()
        self.gui.showSubWindow("Llamada en curso")

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
                print("BBBBBBBBBBBBBBBBBB")
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (800,600))
                self.frame_enviado = cv2.resize(frame, (800,600))
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
            if self.frame_enviado is not None:
                print("AAAAAAAAAAAAAA")
                frame = cv2.resize(decimg, (800,600))
                frame_peque = self.frame_enviado
                frame_compuesto = frame
                frame_compuesto[0:frame_peque.shape[0], 0:frame_peque.shape[1]] = frame_peque
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
            self.gui.stopSubWindow("Llamada en curso")
            self.gui.show()