# import the library
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import socket
import DS

global sock

sock = None

class VideoClient(object):

	def __init__(self, window_size):
		#FALTAN BOTONES (PAUSA) Y INICIO DE SESION, ETC...

		# Creamos una variable que contenga el GUI principal
		self.app = gui("Redes2 - P2P", window_size)
		self.app.setGuiPadding(10,10)


		#Inicio de sesion
		self.app.addLabelEntry("Nombre de usuario")
		self.app.addLabelEntry("Contraseña")

		
		hostname = socket.gethostname()
		ip_address = socket.gethostbyname(hostname)
		self.app.addLabelEntry("IP")
		self.app.setEntry("IP", ip_address)
		self.app.addLabelEntry("Puerto")
		self.app.setEntry("Puerto", 8000)

		self.app.addButton("Iniciar Sesion", self.buttonsCallback)
		#PRIMERA VERSION DE BOTONES
		self.app.addButtons(["Pausar", "Reaunudar", "Colgar"], self.buttonsCallback)

	def home(self):
		#Quitamos info del login
		self.app.hideLabel("Nombre de usuario")
		self.app.hideLabel("Contraseña")
		self.app.hideLabel("IP")
		self.app.hideLabel("Puerto")
		self.app.hideButton("Iniciar Sesion")

		# Preparación del interfaz
		self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
		self.app.addImage("video", "imgs/webcam.gif")

		# Registramos la función de captura de video
		# Esta misma función también sirve para enviar un vídeo
		self.cap = cv2.VideoCapture(0)
		self.app.setPollTime(20)
		self.app.registerEvent(self.capturaVideo)

		# Añadir los botones
		self.app.addButtons(["Llamar", "Listar usuarios", "Buscar usuario", "Salir"], self.buttonsCallback)
		


		# Barra de estado
		# Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
		self.app.addStatusbar(fields=2)

	def start(self):
		self.app.go()

	# Función que captura el frame a mostrar en cada momento
	def capturaVideo(self):
		
		# Capturamos un frame de la cámara o del vídeo
		ret, frame = self.cap.read()
		frame = cv2.resize(frame, (640,480))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))		    

		# Lo mostramos en el GUI
		self.app.setImageData("video", img_tk, fmt = 'PhotoImage')

		# Aquí tendría que el código que envia el frame a la red
		# ...

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

		#AÑADIR FUNCIONALIDAD POR CADA BOTON AÑADIDO
		if button == "Salir":
			# Salimos de la aplicación
			sock.close()
			self.app.stop()
		elif button == "Iniciar sesion":
			# Entrada del nick del usuario a conectar    
			nick = self.app.getEntry("Nombre de usuario")
			password = self.app.getEntry("Contraseña")      
			ip = self.app.getEntry("IP")
			port = self.app.getEntry("Puerto")

			resp = DS.register(nick, password, ip, port, 'v0')

			if resp == "NOK":
				self.app.errorBox("Inicio de sesión", "Error en el proceso de inicio de sesión")
			else:
				#AQUI HACE COSAS 
				self.home()
		elif button == "Buscar usuario":
			nick = self.app.textBox("Buscar", "Introduce el nombre del usuario a buscar")
			if not nick:
				self.app.errorBox("Introduce un nombre de usuario")				
			else:
				nick_query = DS.query(nick)
				if not nick_query:
					self.app.errorBox('No encontrado', 'El usuario con nick: '+ nick+ ' no existe')
				else:
					message = 'Nick: ' + nick_query['nick']+ '\n'
					self.app.infoBox("Usuario: " + message)
		elif button == "Listar usuarios":
			users = DS.list_users()
			self.app.infoBox("Usuarios: ", users)
		elif button == "Llamar":
			#Funcionalidad de llamar, aun no sabemos con certeza como llevarla a cabo
			print("NINE LIVE BLADE WORKS")

		elif button == "Pausar":
			##Funcionalidad de pausa
			print("PAUSATE")
		elif button == "Reanudar":
			print("TRACE ON")

		elif button == "Colgar":
			print("TRIGGER OFF")




if __name__ == '__main__':

	vc = VideoClient("640x520")

	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...


	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()