from . import article
from ..models import Articulos,Categorias
from flask import current_app, render_template,abort,request,redirect, url_for
from flask_login import login_user,logout_user,current_user, login_required
from .forms import CreateForm, DeleteForm
from werkzeug.utils import secure_filename
from ..app import db#sustituir por db en ext
import os

# desacoplar loginmanager en ext 

@article.route("/inicio/create/article/", methods=["GET","POST"])
@login_required
def create_article():
    print("CONTROLADOR: CREATE_FORM")
    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")
    # instancio el formulario
    form=CreateForm()

    # se asignan las opciones dinamicas
    seleccion_cat=[(str(cat.id),cat.nombre) for cat in  Categorias.query.all()]
    form.CategoriaId.choices=seleccion_cat

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
        print(dt)

        # se crea articulo con la info ya procesada(validada,filtrada etc)
        # filestorage
        f=form.imagen.data
        # nombre del fichero imagen
        nombre_fichero=secure_filename(f.filename)

        juego=Articulos(**dt)

        if f:
            juego.imagen=nombre_fichero
            print()
            f.save(current_app.root_path + "/static/upload/" +nombre_fichero)
        else:
            juego.imagen="not-found.png"
        db.session.add(juego)
        db.session.commit()
        # print(f"objeto a enviar:{dt} \n \n objeto referencia:{Articulos.__dict__.keys()}")
        return redirect(url_for("view_inicio"))
    else:
        # form.categoria.choices=[(str(cat.id),cat.nombre) for cat in  Categorias.query.all()]
        return render_template("articuloform.html",form=form)


@article.route("/inicio/update/articulos/", methods=["GET","POST"])
@login_required
def update_form():
    #control de permiso de admin
    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")

    id=request.args.get("id")
    juego=Articulos.query.get(id)
    form=CreateForm(obj=juego)

    # se asignan las opciones dinamicas
    seleccion_cat=[(str(cat.id),cat.nombre) for cat in  Categorias.query.all()]
    form.CategoriaId.choices=seleccion_cat

    
    if form.validate_on_submit() and request.method=="POST":
        if form.imagen.data:
            if juego.imagen!="not-found.png":
                os.remove(current_app.root_path+"/static/upload/"+ secure_filename(juego.imagen))
            fileimagen=form.imagen.data
            nombre_fichero=secure_filename(fileimagen.filename)
            fileimagen.save(current_app.root_path + "/static/upload/" +nombre_fichero)      
        if not form.imagen.data.filename:
            nombre_fichero=juego.imagen
        # el dato id persiste en post, es decir en el segundo llamado
        Articulos.query.filter_by(id=id).update({a:b for a,b in form.data.items() if a != "submit" and a !="csrf_token" and a != "imagen"})
        juego.imagen=nombre_fichero
        db.session.commit()
        return redirect(url_for("view_inicio"))
    else:
        return render_template("articuloform.html" ,form=form, juego=juego,request=request )


@article.route("/inicio/delete/articulos/<int:id>", methods=["GET","POST"])
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

# # FILTRA ARTICULOS POR CATEGORIA MEDIANTE EL ID CATEGORIA (SOLO PRUEBA)
# @article.route("/articulos/")
# @article.route("/articulos/categorias/<id>")
# @article.route("/articulos/categorias/")
# def view_articulos(id=0):

#     respuesta=Articulos.query.all()

#     if request.environ["PATH_INFO"]==f"/articulos/categorias/{id}" and id!=0:
#         try:
#             respuesta=Articulos.query.filter_by(CategoriaId=id)
#         except:
#             return "el parametro id es un numero"
#         return render_template("template4.html",Articulos=respuesta)
        
    
#     return render_template("template2.html",Articulos=respuesta)
#usado por opcion inicion para retornar una lista filtrada de articulos segun la categoria seleccionada
@article.route("/inicio/filterby/categoria/<int:cid>")
def filter_articulos(cid):
    # lista de articulos filtrados por categoria
    articulos_filtrados=Articulos.query.filter_by(CategoriaId=cid).all()

    # todas las categorias para el menu en el front
    todas_categorias=Categorias.query.all()
    categoria_seleccionada=Categorias.query.get(cid)
    return render_template("inicio.html", articulos=articulos_filtrados, Categorias=todas_categorias,
    cat_selec=categoria_seleccionada)
        
 
