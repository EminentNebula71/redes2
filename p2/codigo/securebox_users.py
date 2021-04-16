import requests
import json
from Crypto.PublicKey import RSA
import securebox_crypto 


def create_user(nombre, email, url, token):

    securebox_crypto.RSA_generator()

    f = open("../claves/public_rsa_key.bin", "rb")
    public_key = RSA.import_key(f.read())
    f.close()
    public_key = public_key.exportKey("OpenSSH").decode("utf-8")

    args_petition = {"nombre" : nombre, "email": email, "publicKey": public_key}

    try:
        request = requests.post(url, json = args_petition, headers = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1

    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("Error, fallo en la creación del usuario")
        return -2

    print("Identidad con ID #" + respuesta['userID'] +" creada correctamente")
    return 1

def getPublicKey(user_id, url, token):
    print("-> Recuperando clave publica de ID #"+ user_id+ "...", end=" ")
    args_petition = {"userID": user_id}
    try:
        request = requests.post(url, json= args_petition, headers=token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1

    if request.status_code != 200:
        print("Error, clave no encontrada")
        return -2
    respuesta = json.loads(request.text)

    print("OK")
    return respuesta["publicKey"]

def search_user(cadena, url, token):
    print("Buscando usuario '" + cadena + "' en el servidor......", end=" ")

    args_petition = {'data_search': cadena}
    try:
        request = requests.post(url, json = args_petition, headers = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1
    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("Error, fallo en la busqueda de usuarios")
        return -2
    if len(respuesta)>1:
        user_number = 1
        print("OK")
        print(str(len(respuesta))+" usuarios encontrados:")
        for usuario in respuesta:
            name = str(usuario["nombre"])
            email = str(usuario["email"])
            user_id = str(usuario["userID"])
            print("["+ str(user_number)+"]"+ name+ ", " + email+ " ID: "+ user_id)
            user_number += 1
    else:
        print("No hay usuarios con la cadena "+ cadena)
    return 1


def delete_user(user_id, url, token):
    print("Solicitando borrado de la identidad #"+ user_id+ "...", end=" ")
    args_petition = {"userID": user_id}
    try:
        request = requests.post(url, json= args_petition, headers=token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1
    print("OK")
    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("Error, fallo en la eliminación del usuario")
        return -2
    print("Identidad con ID#"+ user_id+ " borrada correctamente")
    return 1

