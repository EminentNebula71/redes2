from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
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
    signer = PKCS1_v1_5.new(key_RSA)
    sign = signer.sign(message)
    #Guardamos el archivo con la firma de forma temporal
    x = firma + mensaje
    salida = open("../tmp/firma.dat", "wb")
    salida.write(x)
    salida.close()
    print('OK')


def encrypt(file, public_key):
    print("Encriptando archivo.................")
    secret_code = "Mystery"
    try:
        archivo = open(file, "rb")
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
    new_archive = file + "_encrypted"
    archivo = open(new_archive, "wb")
    archivo.write(message_crypted)
    archivo.close()

    print("OK")
    return message_crypted



def encrypt_sign(file, public_key):
    secret_code = "Mystery"
    try:
        archivo = open(file, "rb")
        message = archivo.read()
        archivo.close()
    except FileNotFoundError:
        print("El archivo no existe, ayuda")
        return -3
    #Mandamos a firmar el fichero
    signed = sign(message)
    #Encriptamos el archivo
    encrypt("../tmp/firma.dat", public_key)
    #Renombramos el archivo temporal
    try:
        os.rename("../tmp/firma.dat_encrypted", "../files/"+file+"_cifrado")
    except FileExistsError:
        os.remove("../files/"+file+"_cifrado")
        os.rename("tmp/firma.dat_cifrado", "../files/"+file+"_cifrado")
    os.remove("../tmp/firma.dat")
    return "../files/"+ file+ "_cifrado"


def RSA_generator():
    secret_code = "Mystery"
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

def decrypt(file, user):
    secret_code = "Mystery"
    print("Descifrando fichero.........")
    archivo = open("../tmp/"+ file, "rb")
    message = archivo.read()
    archivo.close()
    #Cogemos cada parte del contenido del fichero
    vector = message[0:16]
    key = message[16:256+16]
    sign = message[256+16:]
    #Abrimos la clave privada del usuario
    encoded_key= open("../claves/private_rsa_key.bin", "rb").read()
    RSA_key = RSA.import_key(encoded_key, passphrase = secret_code)
    #Desencripta la clave usando la clave privada
    cipher = AES.new(key, AES.MODE_CBC, vector)
    decoded_message = cipher.decrypt(message)
    #Quitamos el padding para obtener los datos
    decoded_message = unpad(decoded_message, 16)
    sign = decoded_message[0:256]
    message = decoded_message[256:]
    #Comprobamos si el hasting es correcto
    print("Comprobando firma.............")
    digest = SHA256.new(message)
    emisor = RSA.import_key(user)
    
    try:
        PKCS1_v1_5.new(emisor).verify(digest, sign)
    except (ValueError, TypeError):
        print("La firma no coincide con la clave de usuario")
        return
    print("OK")
    salida = open("../downloads/"+ file, "wb")
    salida.write(message)
    salida.close()    

    try:
        os.remove("../tmp/"+ file)
    except FileNotFoundError:
        print()
    print("El archivo "+ file+ "se ha descargado y comprobado de forma correcta")
