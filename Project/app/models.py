from sqlalchemy import String,Integer,Boolean,Float,ForeignKey, Column
from sqlalchemy.orm import relationship
from app.app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Categorias(db.Model):
    # nombre que se debe poner, sino genera conflictos al importarlo
    __tablename__='Categorias'
    #Primary key como atributo
    id=Column(Integer, primary_key=True)
    nombre=Column(String(100), nullable=False)
    articulo=relationship("Articulos",backref="categoria")

class Articulos(db.Model):
    __tablename__="Articulos"
    id=Column(Integer,nullable=False, primary_key=True)
    nombre=Column(String(50),nullable=False)
    precio=Column(Float,nullable=False)
    iva=Column(Integer,default=21)
    descripcion=Column(String(255))
    imagen=Column(String(255))
    stock=Column(Integer,default=0)
    CategoriaId = Column(Integer, ForeignKey('Categorias.id'), nullable=False)
    #padre= object class Categorias

class Usuarios(db.Model):
    __tablename__="Usuarios"
    id=Column(Integer,nullable=False, primary_key=True)
    username=Column(String(50),unique=True,nullable=False)
    password_hash=Column(String(255),unique=True,nullable=False)
    nombre=Column(String(50),nullable=False)
    email=Column(String(50),nullable=False)
    admin=Column(Boolean(),default=False)

    @property
    def password(self):
        raise AttributeError("no esta permitido ver la contraseña")
    
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)







