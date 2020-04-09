from flask import session, redirect
from typing import Optional


def set_login(Usuario: object = ...) -> None :

    """ Este metodo setea keys en el objeto session de Flask como 
        id , username , admin"""

    session["id"]=Usuario.id
    session["username"]=Usuario.username
    session["admin"]=Usuario.admin

def set_logout() -> None :
    """ Este metodo elimina con pop las keys id, username y admin de 
        session de flask """
    session.pop("id")
    session.pop("username")
    session.pop("admin")

def is_login() -> bool:

    """ Mediante la variable session de flask, esta funcion informa si hay un
        usuario logueado """

    if "id" in session:
        return True
    else:
        return False

def is_admin() -> bool:

    """ Metodo que dice si el usuario logueado es Admin o nó """
    return session.get("admin")

# Estas Funciones se llaman cuando cualquier template es renderizado. 
# Introduciendo las variables expuestas en el diccionario retornado.
# @app.context_processor
# def login () -> dict:
#     if "id" in session:
#         return {"is_login":True}
#     else:
#         return {"is_login":False}
# @app.context_processor
# def admin() -> dict:
#     return {"is_login":session.get("admin")}

