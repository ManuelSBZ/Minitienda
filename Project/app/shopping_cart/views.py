from . import shopping_cart
from ..models import Articulos
from flask import current_app, render_template,abort,request,redirect, url_for
import json
from flask_login import login_user,logout_user,current_user, login_required
from .forms import Carrito
from ..ext import db#sustituir por db en ext

# operación comprar en la pagina de inicio. crea cookie de usuario con articulos
@shopping_cart.route("/add/articulo/<int:id>", methods=["POST","GET"])
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
                    redirectx=current_app.make_response(redirect(url_for("main.view_inicio")))
                    redirectx.set_cookie(str(current_user.id),art_json)
                    return redirectx
                # sino se sustituye el articulo repetido
                else:
                    print(f"se sobreescribe cookie:{articulo_c}")
                    cookie.pop(indice)
                    cookie.insert(indice,articulo_c[0])
                    art_json=json.dumps(cookie)
                    print(f"sobrescribiendo con : {art_json}")
                    redirectx=current_app.make_response(redirect(url_for("main.view_inicio")))
                    redirectx.set_cookie(str(current_user.id),art_json)
                    print(f"el response {redirectx}")
                    return redirectx
            # si no hay cookie definida se crea una nueva para el usuario con el articulo respectivo
            else:
                content=bytes(json.dumps(articulo_c), "UTF-8")
                print("creando cookie")
                response=current_app.make_response(redirect(url_for("main.view_inicio")))
                response.set_cookie(f"{current_user.id}",content)
                return response
    return render_template("FormCarrito.html", form=form,nombre=Articulos.query.get(id).nombre )

@shopping_cart.route("/inicio/carrito", methods=["GET","POST"])
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

@shopping_cart.route("/delete/carrito/<int:id>", methods=["GET","POST"])
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
        respuesta= redirect(url_for("shopping_cart.carro"))
        # se setean las nuevas cookies resultado del proceso anterior, se usa json.dumps para hacerlo
        # una cadena
        respuesta.set_cookie(str(current_user.id), json.dumps(cookie))
        return respuesta
    except:
        return redirect(url_for("shopping_cart.carro")) 

@shopping_cart.route("/inicio/FinalizarPedido/", methods=["POST","GET"])
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
        respuesta= current_app.make_response(render_template("pedido.html"))
        respuesta.set_cookie(str(current_user.id),"",expires=0)
        return respuesta           
                    
    except:
        abort(404, "No hay pedido")


# se envia a contexto el numero de articulos del usuario
@shopping_cart.app_context_processor
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