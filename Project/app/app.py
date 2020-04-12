from flask import Flask, render_template,jsonify,Response, request, url_for, redirect, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
# from app.login import set_login, set_logout
from flask_login import LoginManager,login_user,logout_user,current_user, login_required
import json
import os

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view="log_in"

Bootstrap(app) 

from forms import CreateForm,CreateCat,DeleteForm,SigninForm, LoginForm, CambiarContraseña
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
    articulos=Articulos.query.all()
    cat_list=Categorias.query.all()
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
            print("LOGUEADO?")
            login_user(usuario)
            print(f"RESPUESTA:{current_user.is_authenticated}")
            return redirect(url_for("view_categorias"))
        else:
            form.password.errors.append("Contraseña incorrecta, por favor intente de nuevo")
    return render_template("login.html", form =form, url='log_in')

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
    if usuario is None:
        abort(404, "usuario no existe")
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

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))
