import requests
import json
import requests
from Crypto.PublicKey import RSA
from securebox_crypto import RSA_generator


def create_user(nombre, email, url, token):

    RSA_generator()

    f = open("../claves/public_rsa_key.bin", "rb")
    public_key = RSA.import_key(f.read())
    f.close()

    args_petition = {"nombre" : nombre, "email": email, "publicKey": public_key}

    try:
        request = requests.post(url, json = args_petition, headers = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1

    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("ERROR CODE")

    print("Identidad con ID #" + respuesta['userID'] +"creada correctamente")
    return 1

def search_user(cadena, url, token):
    print("Buscando usuario '" + cadena + "' en el servidor......")

    args_petition = {'data_search': cadena}
    try:
        request = requests.post(url, json = args_petition, headers = token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1
    respuesta = json.loads(request.txt)
    if request.status_code != 200:
        print("ACA HUBO UN ERROR AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")

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
    print("Solicitando borrado de la identidad #"+ user_id+ "...")
    args_petition = {"userID": user_id}
    try:
        request = requests.post(url, json= args_petition, headers=token)
    except requests.ConnectionError:
        print("Error con la conexion para realizar la peticion")
        return -1
    print("OK")
    respuesta = json.loads(request.text)
    if request.status_code != 200:
        print("ACA HUBO UN ERROR AYUDA POR FAVOR AYUDITAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print("Identidad con ID#"+ user_id+ " borrada correctamente")
    return 1

