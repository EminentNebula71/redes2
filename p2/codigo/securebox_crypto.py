from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from securebox_users import getPublicKey
import os



def sign(message):
    secret_code = "Mystery"
    print("Firmando documento..................")
    #Realizamos un hash del mensaje
    digest = SHA256.new()
    digest.update(message)
    #Obtenemos la clave privada del fichero
    encoded_private_key = open("../keys/private_rsa_key.bin", "rb").read()
    key_RSA=RSA.import_key(encoded_private_key, passphrase=secret_code)
    #Firma el hash usando la clave RSA
    signer = pkcs1_15.new(key_RSA)
    sign = signer.sign(message)
    #Guardamos el archivo con la firma de forma temporal
    x = sign + message
    salida = open("../tmp/firma.dat", "wb")
    salida.write(x)
    salida.close()
    print("OK")


def encrypt(filename, public_key):
    print("Encriptando archivo.................")
    try:
        archivo = open(filename, "rb")
        message = archivo.read()
        archivo.close()
    except FileNotFoundError:
        print("El archivo no existe, ayuda")
        return -3
    #Generamos un vector de inicializacion y una clave aleatoria. Despues la ciframos 
    vector = get_random_bytes(16)
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_CBC, vector)
    #Hace falta paddear
    message = pad(message, 16)
    #Encriptamos el fichero
    encoded_message = cipher.encrypt(message)
    #Abrimos la clave publica del receptor y encriptamos con ella
    rsaReceptor = RSA.import_key(public_key)
    funcion_RSA = PKCS1_OAEP.new(rsaReceptor)

    encoded_key = funcion_RSA.encrypt(key)
    message_crypted = vector + encoded_key + encoded_message

    #Lo guardamos en un fichero
    new_archive = filename + "_encrypted"
    archivo = open(new_archive, "wb")
    archivo.write(message_crypted)
    archivo.close()

    print("OK")
    return message_crypted



def encrypt_sign(filename, public_key, url_publicKey, token):
    try:
        archivo = open(filename, "rb")
        message = archivo.read()
        archivo.close()
    except FileNotFoundError:
        print("El archivo no existe, ayuda")
        return -3
    #Mandamos a firmar el fichero
    sign(message)
    #Conseguimos clave publica
    public_key = getPublicKey(public_key, url_publicKey, token)
    #Encriptamos el archivo
    encrypt("../tmp/firma.dat", public_key)
    #Renombramos el archivo temporal
    try:
        os.rename("../tmp/firma.dat_encrypted", "../files/"+filename+"_cifrado")
    except FileExistsError:
        os.remove("../files/"+filename+"_cifrado")
        os.rename("tmp/firma.dat_cifrado", "../files/"+filename+"_cifrado")
    os.remove("../tmp/firma.dat")
    return "../files/"+ filename+ "_cifrado"


def RSA_generator():
    print("Generando par de claves RSA de 2048 bits...")
    new_key = RSA.generate(2048)
    private_key = new_key.exportKey("PEM") 
    public_key = new_key.exportKey("PEM")
    private_file = open("../claves/private_rsa_key.bin", "wb")
    private_file.write(private_key)
    private_file.close()
    public_file = open("../claves/public_rsa_key.bin", "wb")
    public_file.write(public_key)
    public_file.close()
    print("OK")
    return 

def decrypt(filename, user, url_publicKe, token):
    secret_code = "Mystery"
    print("-> Descifrando fichero...")
    archivo = open("../tmp/"+ filename, "rb")
    message = archivo.read()
    archivo.close()
    #Cogemos la clave publica del user
    user = getPublicKey(user, url_publicKey, token)
    if key == None:
        return -1
    #Cogemos cada parte del contenido del fichero
    vector = message[0:16]
    key = message[16:256+16]
    sign = message[256+16:]
    #Abrimos la clave privada del usuario
    encoded_key= open("../claves/private_rsa_key.bin", "rb").read()
    RSA_key = RSA.import_key(encoded_key, passphrase = secret_code)
    #Desencriptamos la clave 
    cipher_rsa = PKCS1_OAEP.new(RSA_key)
    key = cipher_rsa.decrypt(key) 
    #Desencripta la clave usando la clave privada
    cipher = AES.new(key, AES.MODE_CBC, vector)
    decoded_message = cipher.decrypt(message)
    #Quitamos el padding para obtener los datos
    decoded_message = unpad(decoded_message, 16)
    sign = decoded_message[0:256]
    message = decoded_message[256:]
    #Comprobamos si el hasting es correcto
    print("-> Verificando firma.............")
    digest = SHA256.new(message)
    emisor = RSA.import_key(user)

    try:
        pkcs1_15.new(emisor).verify(digest, sign)
    except (ValueError, TypeError):
        print("La firma no coincide con la clave de usuario")
        return
    print("OK")
    salida = open("../downloads/"+ filename, "wb")
    salida.write(message)
    salida.close()    

    try:
        os.remove("../tmp/"+ filename)
    except FileNotFoundError:
        print()
    print("El archivo "+ filename+ "se ha descargado y comprobado de forma correcta")
