import os


global nick
global enPausa
global enLlamada

nick = ' '
enPausa = False
enLlamada = False


def set_nick(name):
    nick=name

def get_nick():
    return nick