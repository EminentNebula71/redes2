import sys

user_info = {
    'nick': None, 'ip': None, 'port':None
}

called_user = {
    'nick': None, 'ip': None, 'port':None
}

global enLlamada 
global enPausa 

enLlamada = False
enPausa = False


def set_user_info(nick, ip, port):
    user_info['nick']= nick
    user_info['ip']= ip
    user_info['port']= port

def set_called_user(nick, ip, port):
    called_user['nick']= nick
    called_user['ip']= ip
    called_user['port']= port


def get_user_info():
    return user_info

def get_called_user():
    return called_user