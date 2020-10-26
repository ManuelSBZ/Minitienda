from flask_script import Manager
from entrypoint import app
from app.models import *
from getpass import getpass
import os
# Wrapper del app flask para usar meta comandos sobre este, tal como sigue adelante.
instance_manager = Manager(app)
app.config['DEBUG'] = True
# app.config['ENV']= "Development" 

# crea tablas basandose en los modelos en models.py
@instance_manager.command
def create_tables():
    "Create relational database tables."
    #se genera la base de datos en el motor especificado y en la carpeta especificada en el config de la app flask
    db.create_all()
    print("Esquema de datos creado")

# elimina todas las tablas
@instance_manager.command
def drop_tables():
    "Drop all project relational database tables. THIS DELETES DATA."
    db.drop_all()
    
    print("Esquema de datos eliminado")
@instance_manager.command
def rollback():
    "Drop all project relational database tables. THIS DELETES DATA."
    db.session.rollback()
    print("roll_back done")

# agrega data de juegos en tablas
@instance_manager.command
def add_data_tables():
    db.create_all()
    categorias = ("Deportes", "Arcade", "Carreras", "Acción")
    for cat in categorias:
        categoria = Categorias(nombre=cat)
        db.session.add(categoria)
        db.session.commit()
    juegos = [
        {"nombre": "Fernando Martín Basket", "precio": 12, "descripcion":
         "Fernando Martín Basket Master es un videojuego de baloncesto, uno "
         "contra uno, publicado por Dinamic Software en 1987", "stock": 10,
         "CategoriaId": 1},
        {"nombre": "Hyper Soccer", "precio": 10, "descripcion": "Konami Hyper "
         "Soccer fue el primer videojuego de fútbol de Konami para una consola"
         " Nintendo, y considerado la semilla de las posteriores sagas "
         "International Superstar Soccer y Winning Eleven.", "stock": 7,
         "CategoriaId": 1},
        {"nombre": "Arkanoid", "precio": 15, "descripcion": "Arkanoid es un "
         "videojuego de arcade desarrollado por Taito en 1986. Está basado en "
         "los Breakout de Atari de los años 70.", "stock": 1,
         "CategoriaId": 2},
        {"nombre": "Tetris", "precio": 6, "descripcion": "Tetris es un "
         "videojuego de puzzle originalmente diseñado y programado por Alekséi"
         " Pázhitnov en la Unión Soviética.", "stock": 5, "CategoriaId": 2},
        {"nombre": "Road Fighter", "precio": 15, "descripcion": "Road Fighter "
         "es un videojuego de carreras producido por Konami y lanzado en los "
         "arcades en 1984. Fue el primer juego de carreras desarrollado por "
         "esta compañía.", "stock": 10, "CategoriaId": 3},
        {"nombre": "Out Run", "precio": 10, "descripcion": "Out Run es un "
         "videojuego de carreras creado en 1986 por Yū Suzuki y Sega-AM2, y "
         "publicado inicialmente para máquinas recreativas.", "stock": 3,
         "CategoriaId": 3},
        {"nombre": "Army Moves", "precio": 8, "descripcion": "Army Moves es un"
         " arcade y primera parte de la trilogía Moves diseñado por Víctor "
         "Ruiz, de Dinamic Software para Commodore Amiga, Amstrad CPC, Atari "
         "ST, Commodore 64, MSX y ZX Spectrum en 1986.", "stock": 8,
         "CategoriaId": 4},
        {"nombre": "La Abadia del Crimen", "precio": 4, "descripcion": "La "
         "Abadía del Crimen es un videojuego desarrollado inicialmente de "
         "forma freelance y publicado por la Academia Mister Chip en noviembre"
         " de 1987, posteriormente se publica bajo el sello de Opera Soft ya "
         "entrado 1988.", "stock": 10, "CategoriaId": 4}, ]
    for jue in juegos:
        juego = Articulos(**jue)
        db.session.add(juego)
        db.session.commit()


# metodo para actualizar en la plantilla
@instance_manager.command
def update_images():
    path=os.getcwd()
    # se enlista los nombres de todos los archivos en ese directorio en tipo string
    lista_imagenes=os.listdir(path+'/app/static/upload/')
    # se almacena todos los articulos en la tabla
    lista_articulos=Articulos.query.all()

    # logica que actualiza todas las imagenes con coincidan con los juegos.
    for juego in lista_articulos:
        for imagen in lista_imagenes:
            print("segundo for")

            # basicamente se ve si parte o algo del nombre de las imagenes coincide con el nombre del juego
            # se le resta 5 para eliminar la terminacion ".jpg"    
            if imagen[:len(imagen)-5].replace(" ","").lower() in juego.nombre.replace(" ","").lower():
                print("se cuestiono si el nombre de la foto esta en en el nombre del articulo")
                art= Articulos.query.filter_by(**{'nombre':juego.nombre}).update({"imagen":imagen})
                db.session.commit()
                break
            else:
                juego.imagen="not-found.png"
                db.session.commit()

@instance_manager.command
def create_admin():
    datos={"nombre":input("Nombre:"),
            "username":input("Username:"),
            "password":getpass("Password: "),
            "email":input("Email:"),
            "admin":True}       
    admin=Usuarios(**datos)
    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    instance_manager.run()
