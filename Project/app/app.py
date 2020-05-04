from flask import Flask, render_template,jsonify,Response, request, url_for, redirect, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
# from app.login import set_login, set_logout
from flask_login import LoginManager,login_user,logout_user,current_user, login_required
import json
import os
import requests

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

Bootstrap(app) 

from forms import CreateForm,CreateCat,DeleteForm,SigninForm, LoginForm, CambiarContraseña, Carrito
from app.models import Articulos,Categorias,Usuarios


# FILTRA ARTICULOS POR CATEGORIA MEDIANTE EL ID CATEGORIA (SOLO PRUEBA)
@app.route("/articulos/")
@app.route("/articulos/categorias/<id>")
@app.route("/articulos/categorias/")
def view_articulos(id=0):

    respuesta=Articulos.query.all()

    if request.environ["PATH_INFO"]==f"/articulos/categorias/{id}" and id!=0:
        try:
            respuesta=Articulos.query.filter_by(CategoriaId=id)
        except:
            return "el parametro id es un numero"
        return render_template("template4.html",Articulos=respuesta)
        
    
    return render_template("template2.html",Articulos=respuesta)

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

#MUESTRA CATEGORIAS 
@app.route("/categorias")
def view_categorias():
    lista_categorias=Categorias.query.all()
    return render_template('template3.html', categorias=lista_categorias)

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
@app.route("/inicio/")
def view_inicio():
    print(current_user.__dict__)
    articulos=Articulos.query.all()
    cat_list=Categorias.query.all()
    print(current_user.is_authenticated)
    return render_template('inicio.html', articulos=articulos, Categorias=cat_list)

#usado por opcion inicion para retornar una lista filtrada de articulos segun la categoria seleccionada
@app.route("/inicio/filterby/categoria/<int:cid>")
def filter_articulos(cid):
    try:
        # lista de articulos filtrados por categoria
        articulos_filtrados=Articulos.query.filter_by(CategoriaId=cid).all()

        # todas las categorias para el menu en el front
        todas_categorias=Categorias.query.all()
        categoria_seleccionada=Categorias.query.get(cid)
        return render_template("inicio.html", articulos=articulos_filtrados, Categorias=todas_categorias,
         cat_selec=categoria_seleccionada)
        
    except:
        return "Categoria no Valida en backend"
    
#COMENTARIO ACERCA DE LOS OBJETOS REGISTROS DEL ORM
#Para actualizar un articulo se debe traer del objetotemporal Articulos que representa la tabla
#luego usando filter_by para filtrar por un valor especifico de algun campo en ella. Luego traer el primer
# elemento en la lista hay dos opciones usar update luego de encontrado por filterby o obtener el
# directamente usando alternativamente a update el metodo all() obteniendo una lista con los parametros 
# en filter_by se indexa generalmente el primer elemento con [0] y se le asignan los nuevos valores a los 
#, travez

@app.route("/inicio/create/form/", methods=["GET","POST"])
@login_required
def create_form():
    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")
    # instancio el formulario
    form=CreateForm()
    # verifico la informacion enviada segun lo estipulado en tipos de campos y validadores
    if form.validate_on_submit():
        # álmaceno la informaion enviada por este formulario en forma dict
        inform=form.data

        # creo diccionario vacio para almacenar respuesta acondicionada para crear articulo
        dt={}

        # proceso de comparacion de los campos de la tabla y las llaves de la entrada que pretende crear el 
        # articulo
        for e in Articulos.__dict__.keys():
            for k,v in inform.items():
                if k==e:
                    dt[k]=v
                    break

        # se crea articulo con la info ya procesada(validada,filtrada etc)
        # filestorage
        f=form.imagen.data
        # nombre del fichero imagen
        nombre_fichero=secure_filename(f.filename)

        juego=Articulos(**dt)

        if f:
            juego.imagen=nombre_fichero
            f.save(app.root_path + "/static/upload/" +nombre_fichero)
        else:
            juego.imagen="not-found.png"

        db.session.add(juego)
        db.session.commit()

        # print(f"objeto a enviar:{dt} \n \n objeto referencia:{Articulos.__dict__.keys()}")
        return redirect(url_for("view_inicio"))
    else:
        # form.categoria.choices=[(str(cat.id),cat.nombre) for cat in  Categorias.query.all()]
        return render_template("articuloform.html",form=form)

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

@app.route("/inicio/update/articulos/", methods=["GET","POST"])
@login_required
def update_form():
    #control de permiso de admin
    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")

    id=request.args.get("id")
    juego=Articulos.query.get(id)
    form=CreateForm(obj=juego)
    
    if form.validate_on_submit() and request.method=="POST":
        if form.imagen.data:
            if juego.imagen!="not-found":
                os.remove(app.root_path+"/static/upload/"+ secure_filename(juego.imagen))
            fileimagen=form.imagen.data
            nombre_fichero=secure_filename(fileimagen.filename)
            fileimagen.save(app.root_path+"/static/upload/"+ nombre_fichero)      
        if juego.imagen:
            nombre_fichero="not-found.png"
        print(f"form.data:{form.data}")
        # el dato id persiste en post, es decir en el segundo llamado
        Articulos.query.filter_by(id=id).update({a:b for a,b in form.data.items() if a != "submit" and a !="csrf_token" and a != "imagen"})
        form.imagen=nombre_fichero
        db.session.commit()
        return redirect(url_for("view_inicio"))
    else:
        return render_template("articuloform.html" ,form=form, juego=juego,request=request )

            
@app.route("/inicio/create/categorias/", methods=["GET","POST"])
@login_required
def create_cat():

    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")

    form=CreateCat()
    
    if form.validate_on_submit():
        data={a:b for a,b in form.data.items() if a != "submit" and a !="csrf_token"}
        categoria = Categorias(**data)
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for("view_categorias")) 
    else:
        return render_template("categoriaform.html", form=form )

   
@app.route("/inicio/delete/articulos/<int:id>", methods=["GET","POST"])
@login_required
def delete_articulo(id):

    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")

    form=DeleteForm()
    juego=Articulos.query.get(id)
    if juego==None:
        return redirect(url_for("view_inicio"))
    
    if form.validate_on_submit():
        if form.si.data==True:
            juego=Articulos.query.get(id)
            db.session.delete(juego)
            db.session.commit()
            return render_template("eliminado.html", juego=juego)     
        else:
            return redirect(url_for("view_inicio"))
    
    return render_template("deleteformjuego.html",id=id,juego=juego, form=form)

@app.route("/inicio/delete/categorias/<int:id>", methods=["GET","POST"])
@login_required
def delete_categoria(id):

    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")

    form=DeleteForm()
    cat=Categorias.query.get(id)
    if cat==None:
        return redirect(url_for("view_categorias"))
    
    if form.validate_on_submit():
        if form.data.get("si")==True:
            try:
                db.session.delete(cat)
                db.session.commit()
            except:
                return abort(400,"Categoria tiene articulos relacionado, no se puede eliminar" )
            return render_template("eliminado.html", juego=cat, form=form)
        else:
            categorias=Categorias.query.all()
            
            return render_template("template3.html", categorias=categorias)
    return render_template("deleteformcat.html", cat=cat, form=form)

@app.route("/signin/", methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("view_inicio"))

    form= SigninForm()
    if form.validate_on_submit():
        print("comprobacion de usuario")
        usuario_existe: list = Usuarios.query.filter_by(username=form.username.data).all()
        
        if len(usuario_existe)==0 :
            print("creando usuario")  
            data_form={key:value 
                        for k in Usuarios.__dict__.keys() for key,value in form.data.items()
                        if key==k}
            print(data_form)
            nuevo_usuario=Usuarios(**data_form)
            nuevo_usuario.admin=False
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for("view_inicio"))
        else:
            print("usuario existe")
            existe=True
            return render_template("signin.html", form=form, url='signin',existe=existe)
    print("no se ha enviado nada")
    return render_template("signin.html", form=form, url='signin')

# login
@app.route("/login/", methods=['GET','POST'])
def log_in():

    if current_user.is_authenticated:
        abort(404, "ya esta logueado")
    
    form=LoginForm()

    if form.validate_on_submit():
        usuario=Usuarios.query.filter_by(username=form.username.data).first()
        if usuario==None:
            form.username.errors.append(f"usuario {form.username.data} no existe")
            return render_template("login.html", form =form, url='log_in')
        print(form.data)
        if usuario.verify_password(form.password.data):
            #crea la session de usuario con los datos del usuario y carga con info del usuario a @login_manager.userloader 
            login_user(usuario)
            next=request.args.get('next')
            return redirect(next or url_for("view_inicio"))
        else:
            form.password.errors.append("Contraseña incorrecta, por favor intente de nuevo")
    return render_template("login.html", form =form, url= 'log_in')

@app.route("/logout/", methods=['GET','POST'])

def log_out():
    logout_user()
    return redirect(url_for("view_inicio"))



@app.route("/editar/perfil/<int:id_usuario>", methods=["GET","POST"])
@login_required
def editar_perfil(id_usuario):
    usuario=Usuarios.query.get(id_usuario)
    form=SigninForm(request.form,obj=usuario)
    del form.password
    del form.cpassword
    if usuario is None:
        abort(404,message='usuario no existe')
    if form.validate_on_submit():
        data_form={key:value 
                        for k in Usuarios.__dict__.keys() for key,value in form.data.items() if key==k}
        try:
            Usuarios.query.filter_by(id=id_usuario).update(data_form)
            db.session.commit()
            login_user(usuario)
            return redirect(url_for('view_inicio'))
        except:
            form.username.errors.append("username ya existente")
            
    return render_template("signin.html", form=form, editar=True, url="editar_perfil")

@app.route("/editar/contraseña/<int:id_usuario>", methods=['GET','POST'])
@login_required
def editar_contraseña(id_usuario):
    form=CambiarContraseña()
    usuario=Usuarios.query.get(id_usuario)
    if usuario.id != current_user.id:
        abort(404, "usuario no coincide")
    if form.validate_on_submit():
        data_form={key:value 
                    for k in Usuarios.__dict__.keys() for key,value in form.data.items() if key==k}
        print(f'la dataaa : {data_form.keys()}')
        usuario.password=data_form["password"]
        # print(f"datos = {form.data}")
        # usuario=Usuarios.query.get(id_usuario)
        # form.populate_obj(usuario)
        db.session.commit()
        return redirect(url_for("view_inicio"))
    return render_template("cambiarcontraseña.html", form=form)

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

# VER Y ELIMINAR COOKIES
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


# operación comprar en la pagina de inicio. crea cookie de usuario con articulos
@app.route("/add/articulo/<int:id>", methods=["POST","GET"])
@login_required
def comprar(id):

    # para pintar el formulario
    form=Carrito()

    #para traer datos del articulo seleccionado
    art=Articulos.query.get(id)

    # se asignan las opciones dinamicas segun el numero de stock (SelectField)
    lista_cantidad=[(a,f"{a}") for a in range(art.stock + 1)]
    form.cantidad.choices=lista_cantidad
    form.cantidad.choices.pop(0)

    if form.validate_on_submit():
        # validadndo cantidad vs stock disponible
        
        # se verifica si la cantidad de articulos solicitados para comprar no supera el stock en la tienda.
        if form.cantidad.data <=  art.stock:
            print("hay en stock")
            # definicion de la estructura de la cookie para el carrito.
            articulo_c=[{"nombre":art.nombre, "precio":art.precio, "cantidad":form.cantidad.data,
                        "precio_total":round(art.precio_con_iva()*form.cantidad.data,2), "id":art.id}]
            print("added cookie")
            # cookie lista del usuario en str.
            cookie=request.cookies.get(str(current_user.id))
            # lista de diccionarios articulos por usuario version objeto python.
            try:
                cookie=json.loads(cookie)
            except:
                cookie=None

        # si la cookie no es nula llama la cookie del usuario 
            if cookie:
                print("cookie ya esta definida")
                
                # se verifica si esta el mismo articulo para sobreescribirlo
                for index,c in enumerate(cookie):
                    # for key,value in c.items():
                    print(f"c:{c}, type:{type(c)}")
                    if c["nombre"] == articulo_c[0]["nombre"]:
                        print(f"indice={index}, item: {c}")
                        repetido=True
                        indice=cookie.index(c)
                        break
                    else:
                        repetido=False
                # se agrega el articulo si esta no esta repetido.
                if repetido==False:
                    cookie.extend(articulo_c)
                    art_json=json.dumps(cookie)
                    print(f"se agrega nueva cookie:{articulo_c[0]}")
                    redirectx=app.make_response(redirect(url_for("view_inicio")))
                    redirectx.set_cookie(str(current_user.id),art_json)
                    return redirectx
                # sino se sustituye el articulo repetido
                else:
                    print(f"se sobreescribe cookie:{articulo_c}")
                    cookie.pop(indice)
                    cookie.insert(indice,articulo_c[0])
                    art_json=json.dumps(cookie)
                    print(f"sobrescribiendo con : {art_json}")
                    redirectx=app.make_response(redirect(url_for("view_inicio")))
                    redirectx.set_cookie(str(current_user.id),art_json)
                    print(f"el response {redirectx}")
                    return redirectx
            # si no hay cookie definida se crea una nueva para el usuario con el articulo respectivo
            else:
                content=bytes(json.dumps(articulo_c), "UTF-8")
                print("creando cookie")
                response=app.make_response(redirect(url_for("view_inicio")))
                response.set_cookie(f"{current_user.id}",content)
                return response
    return render_template("FormCarrito.html", form=form,nombre=Articulos.query.get(id).nombre )

@app.route("/inicio/carrito", methods=["GET","POST"])
@login_required
def carro():

    try:
        cookie=json.loads(request.cookies.get(str(current_user.id)))
        precio=0
        for item in cookie:
            precio = round(precio+item["precio_total"], 2)
            
    except:
        cookie=None
        precio=0
    

    return render_template("carrito.html", cookie=cookie, precio=precio)

@app.route("/delete/carrito/<int:id>", methods=["GET","POST"])
@login_required
def carro_delete(id):
    try:
        # se intenta obtener el objeto de la cookie del usuario, una lista de juegos.
        cookie=json.loads(request.cookies.get(str(current_user.id)))
        # se reccorre la lista de juego 
        for juego in cookie:
            # ... Y se pregunta si el id del juego actual es el id del juego que se quiere eliminar.
            if juego.get("id")==id:
                # se pregunta el indice del juego en la lista.
                indice=cookie.index(juego)
                # se usa el indice del juego para eliminarlo con pop.
                cookie.pop(indice)
        # se crea la respuesta
        respuesta= redirect(url_for("carro"))
        # se setean las nuevas cookies resultado del proceso anterior, se usa json.dumps para hacerlo
        # una cadena
        respuesta.set_cookie(str(current_user.id), json.dumps(cookie))
        return respuesta
    except:
        return redirect(url_for("carro")) 

@app.route("/inicio/FinalizarPedido/", methods=["POST","GET"])
@login_required
def pedido():

    try:
        # lista de juegos del carrito del usuario.
        print(1)
        articulos_carrito= json.loads(request.cookies.get(str(current_user.id)))
        #descuento de los juegos del carrito de los articulos en la pagina(base de datos)
        print(2)
        for articulo_carrito in articulos_carrito: 
            print("hee")
            Articulos.query.get(articulo_carrito["id"]).stock-=articulo_carrito["cantidad"]
            db.session.commit()
        print(3)
        respuesta= app.make_response(render_template("pedido.html"))
        respuesta.set_cookie(str(current_user.id),"",expires=0)
        return respuesta           
                    
    except:
        abort(404, "No hay pedido")

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
                for fuego in cookie:
                    cantidad_juegos=len(cookie)
            except:
                cantidad_juegos = 0 
        
            return {"cantidad_juegos":cantidad_juegos}
        except:
            print("exceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeept")
            return {"cantidad_juegos":"E0"}
    return {"cantidad_juegos":"E1"}
@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))
