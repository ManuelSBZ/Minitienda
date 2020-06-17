from flask import Flask, render_template,jsonify,Response, request, url_for, redirect, abort
from flask_sqlalchemy import SQLAlchemy
# from app.login import set_login, set_logout
from flask_login import LoginManager,login_user,logout_user,current_user, login_required
import json
import os
# wrapper app flask que contiene todos los atributos,  metodos y directrices para crear el proyecto segun las
# especificaciones del framework.
app = Flask(__name__)

# se anexa la configuracion config.py en el objeto del proyecto
app.config.from_pyfile("config.py")

# wrapper del app obtject que da los metodos ORM para interactuar con la capa de datos
db = SQLAlchemy(app)

# wrapper para implementar sistema de autenticacion en app flask.
login_manager=LoginManager(app)
# seteando el wrapper para legueo con view del login. Su utilidad es para la redirecciones automaticas
# a dicha vista.
login_manager.login_view="log_in" 

from app.models import Articulos,Categorias,Usuarios

from .articles import article
from .categories import category
from .session_user import session_user
from .shopping_cart import shopping_cart

app.register_blueprint(article)
app.register_blueprint(category)
app.register_blueprint(session_user)
app.register_blueprint(shopping_cart)



# RETORNA JSON DE LISTA DE ARTICULOS
@app.route("/api/articulos/")
def api_articulos():
    lista=Articulos.query.all()
    lista_json=[]
    for e in lista:
        
        articulos_dict={
            'nombre': e.nombre,
            'precio':e.precio,
            'categoria':e.categoria.nombre
        }
        lista_json.append(articulos_dict)

    return jsonify({"Juegos":lista_json})

# CREATE articulo enviando json
@app.route("/api/create/", methods=["POST"])
def api_create():
    articulo={
        'nombre':request.json['nombre'],
        'precio':request.json['precio'],
        'stock':request.json['stock']
    }
    juego_creado=Articulos(**articulo)
    categoria=Categorias.query.filter_by(nombre=request.json['categoria']).all()[0]
    categoria.articulo.append(juego_creado)
    db.session.add(categoria)
    db.session.commit()
    return jsonify({'mesagge':'creado'})

# UPDATE usando post enviando json 

@app.route("/api/update/articulos/<string:k>/<int:v>", methods=["POST"])
def api_update(k,v):
    db.session.rollback()
    art=Articulos.query.filter_by(**{k:v}).all()[0]
    print(art)
    categoria=Categorias.query.filter_by(nombre=request.json['categoria']).all()[0]
    categoria.articulo.append(art)
    db.session.commit()
    return jsonify({"message":"register updated","register":str({"nombre":art.nombre, 
    "categoria":art.categoria.nombre,"id":art.categoria.id, "precio":art.precio, "stock":art.stock})})


# DELETE elimina registro seleccionando tabla(e), campo(k), valor de campo(v)

@app.route("/delete/<string:e>/<string:k>/<string:v>")
def delete(e,k,v):
    art=eval(e).query.filter_by(**{k:eval(v)}).all()[0]
    print(f"el resultado:{art.nombre}")
    db.session.delete(art)
    db.session.commit()
    return redirect(url_for("view_inicio"))



    
# funciones de pagina web de venta


            #inicio INICIO

# pagina de inicio.
@app.route("/inicio/")
def view_inicio():
    print(current_user.__dict__)
    articulos=Articulos.query.all()
    cat_list=Categorias.query.all()
    print(current_user.is_authenticated)
    return render_template('inicio.html', articulos=articulos, Categorias=cat_list)

   
#COMENTARIO ACERCA DE LOS OBJETOS REGISTROS DEL ORM
#Para actualizar un articulo se debe traer del objeto-mapper Articulos que representa la tabla
#luego usando filter_by para filtrar por un valor especifico de algun campo en ella. Luego traer el primer
# elemento en la lista hay dos opciones usar update luego de encontrado por filterby o obtener el
# directamente usando alternativamente a update el metodo all() obteniendo una lista con los parametros 
# en filter_by se indexa generalmente el primer elemento con [0] y se le asignan los nuevos valores a los 
#, travez


# @app.route("/inicio/update/articulos/", methods=["GET","POST"])
# def update_form():
   
#     form=CreateForm()
    
#     if request.args:
#         id=request.args.get("id")

#         if form.validate_on_submit():
#             print("paso por if validate form")
#             print(f"id:{id} \n tipo:")
#             inform=form.data
#             print(f"{inform} \n")
#             dt={}
#             for e in Articulos.__dict__.keys():
#                 for k,v in inform.items():
#                     if k==e and k!="imagen":
#                         dt[k]=v
#                         break
#             print(f"dt: \n{dt}")
#             # imagen_anterior=juego.imagen
#             # actualizando atributos menos el de imagen
#             juego=Articulos.query.filter_by(id=id).update(dt)
#             # actualizando a nueva imagen si la tiene
#             if form.imagen.data:
#                 juego=Articulos.query.get(id)
#                 file_storage=form.imagen.data
#                 nombre_fichero=secure_filename(file_storage.filename)
#                 file_storage.save(app.root_path + "/static/upload/" +nombre_fichero)
#                 juego.imagen=nombre_fichero
#             db.session.commit()
#             return redirect(url_for("view_inicio"))
#         else:
#             if not form.validate_on_submit(): 
#                 print(f"form['nombre']:{form['nombre']}\n type(form):{type(form)}")
#             juego= Articulos.query.filter_by(id=id).all()[0]
#             return render_template("template6.html",form=form, request=request, juego=juego)

#COOKIES 

# SETEA COOKIES DE PRUEBA(CARACTER DIDACTICO)
@app.route("/SetCookies")
def set_cookies():
    art=Articulos.query.get(1)
    content=json.dumps([{"nombre":art.nombre, "precio":art.precio, "cantidad":8}])
    print(content)
    content=bytes(content,"UTF-8")
    response=app.make_response(redirect(url_for("view_inicio")))
    response.set_cookie("1",content)
    return response

# VER Y ELIMINAR COOKIES(prueba)
@app.route("/SeeCookies")
@app.route("/DeleteCookies")
def see_cookies():
    if request.path=="/DeleteCookies":
        cookies=request.cookies
        response=app.make_response("cookies deleted")
        for key,values in cookies.items():
            try:
                response.set_cookie(key,"", expires=0)
                print(f"work with {key}")
            except:
                print(f"la llave que No funciono: {key}")
        # response.set_cookies(,)
        return response
    try:
        obj=request.cookies
        print(f"haaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:{obj}")
    except:
        return bytes("No hay Cookies", "UTF-8")
    
    return f"type:{obj}"

# @app.route("/ModifyCookies")
# def Modify_cookies():
#     message="coockies seteada"
#     response=app.make_response(message)
#     response.set_cookie("articulos",json.dumps([{"art2":"XBOX 360"},{"art1":"1TRILLION DOLLARS"}]))
#     return response

# COOKIES DE LA APLICACION CARRITO





# se envia a contexto el numero de articulos del usuario
@app.context_processor
def numero_articulos():
    if current_user.is_authenticated:
        try:
            cantidad_juegos=0
            print("PRIMER ESCALON")
            try:
                cookie=json.loads(request.cookies.get(str(current_user.id)))
                print(f"SEGUNDO ESCALON")
                cantidad_juegos=len(cookie)
            except:
                cantidad_juegos = 0 
        
            return {"cantidad_juegos":cantidad_juegos}
        except:
            return {"cantidad_juegos":"E0"}
    return {"cantidad_juegos":"E1"}
    
@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))
