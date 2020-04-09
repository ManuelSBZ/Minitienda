from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import FloatField, StringField,IntegerField, TextField, SubmitField,SelectField,FileField,TextAreaField,PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from app.models import Categorias


class CreateForm(FlaskForm):
    nombre=StringField("Nombre",validators=[DataRequired("Este es un campo requerido")])
    
    precio=FloatField("Precio",validators=[DataRequired("Debe colocar un numero")])
    
    stock=IntegerField("Nro en Stock", validators=[DataRequired("Debe colocar un numero entero")])
    
    descripcion=TextAreaField("Descripcion", 
                            [Length(min=10,message=("La descripción debe tener mas de 10 caracteres"))
                            ,DataRequired("Este es un campo requerido")])
    # iva=IntegerField("Iva",validators=[DataRequired("Este es un campo requerido")])
    
    CategoriaId=SelectField("Categoria",
                            choices=[(str(cat.id),cat.nombre) for cat in  Categorias.query.all()])
    imagen=FileField("Imagen")

    submit=SubmitField("Submit")

class CreateCat(FlaskForm):
    nombre=StringField("Categoria", validators=[DataRequired("Por favor escriba una nueva categoria")])
    submit=SubmitField("Submit")

class DeleteForm(FlaskForm):
    si=SubmitField("Si" ,default=True)
    no=SubmitField("No" ,default=False)

class LoginForm(FlaskForm):
    username=StringField("Usuario",validators=[DataRequired("Usuario Incorrecto")])
    password=PasswordField("Contraseña", validators=[DataRequired("Contraseña Incorrecta")])
    submit=SubmitField("Submit")

class SigninForm(FlaskForm):
    username=StringField("Usuario",validators=[DataRequired("Usuario Incorrecto")])
    password=PasswordField("Contraseña", validators=[DataRequired(),Length(10,message="minimo 10 caracteres")])
    cpassword=PasswordField("Repita contraseña", validators=[DataRequired(),EqualTo(fieldname='password',message="las contraseñas no coinciden")])
    nombre=StringField("nombre",validators=[DataRequired("Usuario Incorrecto")])
    email=StringField("Email",validators=[Email(message="Por favor introduzca un email valido")])
    submit=SubmitField("Submit")
    
class CambiarContraseña(FlaskForm):
    password=PasswordField("Contraseña", validators=[DataRequired(),Length(10,message="minimo 10 caracteres")])
    cpassword=PasswordField("Repita contraseña", validators=[DataRequired(),EqualTo(fieldname='password',message="las contraseñas no coinciden")])
    submit=SubmitField("Submit")