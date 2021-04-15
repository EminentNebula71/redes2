import requests
import json
import datetime
from securebox_crypto import decrypt

def upload(filename, url, token):
    print("->Subiendo fichero a servidor...")
    try:
        up_file = open(filename, "rb")
    except FileNotFoundError:
        print("Error al abrir el archivo ")
    args_petition = {"ufile": up_file}
    try:
        request = requests.post(url, json = args_petition, headers = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1

    respuesta = json.loads(request.text)

    if request.status_code != 200:
        print("Codigo Error: "+respuesta["error_code"]+": "+respuesta["description"])
        return -2


    print("Subida realizada correctamente, ID del fichero:" + respuesta['file_id'])
    return 1

def download(file_id, user_id, url, token, url_publicKey):
    print("->Descargando fichero de SecureBox...")
    args_petition = {"file_id": file_id}
    try:
        request = requests.post(url, json = args_petition, headers = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1

    if request.status_code != 200:
        print("Codigo Error: "+respuesta["error_code"]+": "+respuesta["description"])
        return -2

    now = datetime.now()
    current_time = now.strftime("%d_%m_%y_%H_%M_%S")
    filename = "Descarga_" + current_time
    do_file = open("tmp/"+ filename)
    do_file.write(request.content)
    do_file.close()
    print("OK")
    print("-> "+ str(len(request.content))+ " bytes descargados correctamente")
    decrypt(filename, user_id, url_publicKey, token) #Se llama aqui o en cliente??

    

def list_files(url, token):
    try:
        request = requests.post(url, header = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1
    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("No se han encontrado ficheros")
        return -2
    print("El numero de ficheros encontrados es de: "+str(respuesta["num_files"]))
    for fichero in response["files_list"]:
        print("Archivo: "+ fichero["fileName"]+" con ID: "+ fichero["fileID"])



def delete_file(file_id, url, token):
    args_petition = {"file_id": file_id}
    try:
        request = requests.post(url, json=args_petition, header = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1
    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("Codigo Error: "+respuesta["error_code"]+": "+respuesta["description"])
        return -2
    print("Archivo con ID: "+ respuesta["file_id"]+ " borrado con exito")


