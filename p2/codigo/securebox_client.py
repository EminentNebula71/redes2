#Funcionalidad del cliente

#Debe de leer que argumentos recibe y hacer x funcion a partir de ahi

from securebox_crypto import *
from securebox_files import *
from securebox_users import *
import sys
import argparse

parser = argparse.ArgumentParser(description = "Opciones posibles")

parser.add_argument("--create_id",dest="create_id", metavar=("nombre", "email"), nargs=2, 
                    help="Crea una nueva identidad (par de claves púlica y privada) para un usuario con nombre nombre y correo email, y la registra en SecureBox, para que pueda ser encontrada por otros usuarios. alias es una cadena identificativa opcional")
parser.add_argument("--search_id", dest="search_id", metavar="cadena", nargs=1, 
                    help="	Busca un usuario cuyo nombre o correo electrónico contenga cadena en el repositorio de identidades de SecureBox, y devuelve su ID")
parser.add_argument("--delete_id", dest="delete_id", metavar="id", nargs=1, 
                    help= "	Borra la identidad con ID id registrada en el sistema. Obviamente, sólo se pueden borrar aquellas identidades creadas por el usuario que realiza la llamada.")                    
parser.add_argument("--upload", dest="upload", metavar="fichero", nargs=1,
                    help="Envia un fichero a otro usuario, cuyo ID es especificado con la opción --dest_id. Por defecto, el archivo se subirá a SecureBox firmado y cifrado con las claves adecuadas para que pueda ser recuperado y verificado por el destinatario.")
parser.add_argument("--source_id", dest="source_id", metavar="id", nargs=1,
                    help="ID del emisor del fichero.")
parser.add_argument("--dest_id", dest="dest_id", metavar="id", nargs=1,
                    help="ID del receptor del fichero.")          
parser.add_argument("--list_files", dest="list_files", action="store_true", help="Lista todos los ficheros pertenecientes al usuario")   
parser.add_argument("--download", dest="download", metavar="id_fichero", nargs=1,
                    help= "Recupera un fichero con ID id_fichero del sistema (este ID se genera en la llamada a upload, y debe ser comunicado al receptor). Tras ser descargado, debe ser verificada la firma y, después, descifrado el contenido.")
parser.add_argument("--delete_file", dest="delete_file", metavar="id_fichero", nargs=1,
                    help="Borra un fichero del sistema.")
parser.add_argument("--encrypt", dest="encrypt", metavar="fichero", nargs=1,
                    help="Cifra un fichero, de forma que puede ser descifrado por otro usuario, cuyo ID es especificado con la opción --dest_id")
parser.add_argument("--sign", dest="sign", metavar="fichero", nargs=1,
                    help="Firma un fichero.")
parser.add_argument("--enc_sign", dest="enc_sign", metavar="fichero", nargs=1,
                    help="Cifra y firma un fichero, combinando funcionalmente las dos opciones anteriores.")

args=parser.parse_args()


if len(sys.argv) < 2:
    print("Pon algo chiquillo")
    sys.exit()

if not os.path.isdir('../download_files'):
    try:
        os.mkdir('../download_files')
    except OSError:
        print('Error al generar los directorios necesarios, asegurese de que el programa puede modificar directorios')

if not os.path.isdir('../tmp'):
    try:
        os.mkdir('../tmp') 
    except OSError:
        print('Error al generar los directorios necesarios, asegurese de que el programa puede modificar directorios')

if not os.path.isdir('../files'):
    try:
        os.mkdir('../files')
    except OSError:
        print('Error al generar los directorios necesarios, asegurese de que el programa puede modificar directorios')

if not os.path.isdir('../claves'):
    try:
        os.mkdir('../claves')
    except OSError:
        print('Error al generar los directorios necesarios, asegurese de que el programa puede modificar directorios')


config = open('../config.conf', 'r')
api_url=config.readlines(1)
api_url=str(api_url)[12:43]

auth_token=config.readlines(2)
auth_token=str(auth_token)[10:33]
config.close()

token={'Authorization' : auth_token}


# Gestion de usuarios e identidades
if args.create_id:
    url = api_url + "/users/register"
    create_user(args.create_id[0], args.create_id[1], url, token)

if args.search_id:
    url = api_url +"/users/search"
    search_user(args.search_id[0], url, token)

if args.delete_id:
    url = api_url + "/users/delete"
    delete_user(args.delete_id[0], url, token)


# Subida y descarga de ficheros
if args.upload:
    if not args.dest_id:
        print("Escribe la ID del usuario al que vas a enviar el fichero con --dest_id")
        sys.exit()
    print("Solicitando envio de fichero a SecureBox")

    url_publicKey = api_url + "/users/getPublicKey"
    message_encrypted = encrypt_sign(args.upload[0], args.dest_id[0], url_publicKey, token)
    url = api_url + "/files/upload"
    upload(message_encrypted, url, token)
    
if args.list_files:
    url = api_url + "/files/list"
    list_files(url, token)

if args.delete_file:
    url = api_url + "/files/delete"
    delete_file(args.delete_file[0], url, token)

if args.download:
    if not args.source_id:
        print("Escribe la ID del usuario que ha emitido este fichero con --dest_id")
        sys.exit()
    url_publicKey = api_url + "/users/getPublicKey"
    url = api_url + "/files/download"
    download(args.download[0], args.source_id[0], url, token, url_publicKey)



# Cifrado y firma de ficheros local

if args.encrypt:
    if not args.dest_id:
        print("Escribe la ID del usuario al que vas a enviar el fichero con --dest_id")
        sys.exit()

    url = api_url + "/users/getPublicKey"
    key = getPublicKey(args.dest_id[0], url, token)
    if key == None:
        sys.exit()
    
    encrypt(args.encrypt[0], key)

if args.sign:
    if not args.dest_id:
        print("Introduce la ID del usuario al que deseas enviarle con --dest_id")
        sys.exit()
    
    url = api_url + "/users/getPublicKey"
    key = getPublicKey(args.dest_id[0], url, token)
    if key == None:
        sys.exit()
    
    try:
        fichero = open(args.sign[0], "rb")
        message = fichero.read()
        fichero.close()
    except FileNotFoundError:
        print("Error, fichero no encontrado")
        sys.exit()
    sign(message)

if args.enc_sign:
    if not args.dest_id:
        print("Introduce la ID del usuario al que deseas enviarle con --dest_id")
        sys.exit()
    
    url = api_url + "/files/getPublicKey"
    url_publicKey = api_url + "/users/getPublicKey"
    encrypt_sign(args.enc_sign[0], args.dest_id[0], url_publicKey, token)
