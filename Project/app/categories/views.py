from . import category
from ..models import Articulos,Categorias
from flask import current_app, render_template,abort,request,redirect, url_for
from flask_login import login_user,logout_user,current_user, login_required
from .forms import CreateCat, DeleteForm
from ..ext import db#sustituir por db en ext


#MUESTRA CATEGORIAS 
@category.route("/categorias")
def view_categorias():
    lista_categorias=Categorias.query.all()
    return render_template('template3.html', categorias=lista_categorias)

@category.route("/inicio/create/categorias/", methods=["GET","POST"])
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
        return redirect(url_for("category.view_categorias")) 
    else:
        return render_template("categoriaform.html", form=form )

@category.route("/inicio/delete/categorias/<int:id>", methods=["GET","POST"])
@login_required
def delete_categoria(id):

    if not current_user.is_admin():
        abort(404, "no es admin, no tiene permiso")

    form=DeleteForm()
    cat=Categorias.query.get(id)
    if cat==None:
        return redirect(url_for("category.view_categorias"))
    
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
