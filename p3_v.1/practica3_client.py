# import the library
import threading
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import socket
import DS
import user_info
import call_control

global sock
sock = None

class VideoClient(object):

	def __init__(self, window_size):
		#FALTAN BOTONES (PAUSA) Y INICIO DE SESION, ETC...

		# Creamos una variable que contenga el GUI principal
		self.app = gui("Redes2 - P2P", window_size)
		self.app.setGuiPadding(10,10)


		#Inicio de sesion
		self.app.addLabelEntry("Nombre de usuario/Nick")
		self.app.addLabelEntry("Contraseña")

		
		hostname = socket.gethostname()
		ip_address = socket.gethostbyname(hostname)
		self.app.addLabelEntry("IP (hostname predeterminada)")
		self.app.setEntry("IP (hostname predeterminada)", ip_address)
		self.app.addLabelEntry("Puerto (8000 predeterminado)")
		self.app.setEntry("Puerto (8000 predeterminado)", 8000)

		self.app.addButton("Iniciar Sesion", self.buttonsCallback)
		
		
		#Para capturar la camara en el menu de home
		self.cap = cv2.VideoCapture(0)
		if self.cap is None:
			self.cap = None

	def home(self):
		user = user_info.get_user_info()

		#Quitamos info del login
		self.app.hideLabel("Nombre de usuario/Nick")
		self.app.hideLabel("Contraseña")
		self.app.hideLabel("IP (hostname predeterminada)")
		self.app.hideLabel("Puerto (8000 predeterminado)")
		self.app.hideButton("Iniciar Sesion")

		# Preparación del interfaz
		self.app.addLabel("title", "Cliente Multimedia P2P - Redes2- "+ user['nick'])
		self.app.addImage("video1", "img/false_webcam.gif")


		self.app.setPollTime(20)
		self.app.registerEvent(self.capturaVideo)


		# Añadir los botones
		self.app.addButtons(["Llamar", "Listar usuarios", "Buscar usuario", "Salir"], self.buttonsCallback)

		# Barra de estado
		# Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
		# self.app.addStatusbar(fields=2)



	def capturaVideo(self):
		# Capturamos un frame de la cámara o del vídeo
		if  self.cap is not None:
			ret, frame = self.cap.read()
			frame = cv2.resize(frame, (640,480))
			cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
			img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))		    
			# Lo mostramos en el GUI
			self.app.setImageData("video1", img_tk, fmt = 'PhotoImage')



	# Establece la resolución de la imagen capturada
	def setImageResolution(self, resolution):		
		# Se establece la resolución de captura de la webcam
		# Puede añadirse algún valor superior si la cámara lo permite
		# pero no modificar estos
		if resolution == "LOW":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160) 
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120) 
		elif resolution == "MEDIUM":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320) 
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) 
		elif resolution == "HIGH":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 

	

	# Función que gestiona los callbacks de los botones
	def buttonsCallback(self, button):
		global sock
		global waiting_thread

		#AÑADIR FUNCIONALIDAD POR CADA BOTON AÑADIDO
		if button == "Salir":
			# Salimos de la aplicación
			sock.close()
			self.app.stop()
		elif button == "Iniciar Sesion":
			# Entrada del nick del usuario a conectar    
			nick = self.app.getEntry("Nombre de usuario/Nick")
			password = self.app.getEntry("Contraseña")      
			ip = self.app.getEntry("IP (hostname predeterminada)")
			port = self.app.getEntry("Puerto (8000 predeterminado)")

			resp = DS.register(nick, ip, port, password, 'v0')

			if resp == "NOK":
				self.app.errorBox("Inicio de sesión", "Error en el proceso de inicio de sesión")
			else:
				user = {'nick': nick, 'ip':ip, 'port':int(port)}
				user_info.set_user_info(nick, ip, port)
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				user_address = (user['ip'], int(user['port']))
				sock.bind(user_address)
				waiting_thread = threading.Thread(target=call_control.wait_call, args =(self,sock, self.cap), daemon= True)
				waiting_thread.start()
				self.home()

		elif button == "Buscar usuario":
			nick = self.app.textBox("Buscar", "Introduce el nombre del usuario a buscar")
			if not nick:
				self.app.errorBox("Introduce un nombre de usuario")				
			else:
				nick_query = DS.query(nick)
				nick_query = nick_query.split(' ')[2]
				if not nick_query:
					self.app.errorBox('No encontrado', 'El usuario con nick: '+ nick+ ' no existe')
				else:
					message = 'Nick: ' + nick_query+ '\n' #La posicion 2 es la de nick
					self.app.infoBox("Usuario: ", message)

		elif button == "Listar usuarios":
			users = DS.list_users()
			self.app.infoBox("Usuarios: ", users)

		elif button == "Llamar":
			nick = self.app.textBox("Llamada", "Introduce el nick de a quien deseas llamar")
			if nick:
				user_search = DS.query(nick)
				if not user_search: 
					self.app.errorBox('No encontrado', 'El usuario con nick: '+ nick+ ' no existe')
				else:
					user_search = user_search.split(' ')
					call_control.call(self, user_search, self.cap)


	def start(self):
		self.app.go()


if __name__ == '__main__':

	vc = VideoClient("640x520")

	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...


	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()