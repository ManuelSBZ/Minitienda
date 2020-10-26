from . import main
from ..models import Articulos, Categorias
from flask import current_app, render_template,abort,request,redirect, url_for
import json
from flask_login import login_user,logout_user,current_user, login_required
from .forms import Carrito
from ..ext import db, login_manager #sustituir por db en ext

# operación comprar en la pagina de inicio. crea cookie de usuario con articulos
@main.route("/inicio/")
def view_inicio():
    print(current_user.__dict__)
    articulos=Articulos.query.all()
    cat_list=Categorias.query.all()
    print(current_user.is_authenticated)
    return render_template('inicio.html', articulos=articulos, Categorias=cat_list)

#usado por opcion inicion para retornar una lista filtrada de articulos segun la categoria seleccionada
@main.route("/inicio/filterby/categoria/<int:cid>")
def filter_articulos(cid):
    try:
        # lista de articulos filtrados por categoria
        articulos_filtrados=Articulos.query.filter_by(CategoriaId=cid).all()

        # todas las categorias para el menu en el front
        todas_categorias=Categorias.query.all()
        categoria_seleccionada=Categorias.query.get(cid)
        return render_template('inicio.html', 
                                articulos=articulos_filtrados, 
                                Categorias=todas_categorias,
                                cat_selec=categoria_seleccionada)
    except: pass