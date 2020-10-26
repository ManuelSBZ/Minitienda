from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import FloatField, StringField,IntegerField, TextField, SubmitField,SelectField,FileField,TextAreaField,PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo



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

# acoplado con app principal por choices
class CambiarContraseña(FlaskForm):
    password=PasswordField("Contraseña", validators=[DataRequired(),Length(10,message="minimo 10 caracteres")])
    cpassword=PasswordField("Repita contraseña", validators=[DataRequired(),EqualTo(fieldname='password',message="las contraseñas no coinciden")])
    submit=SubmitField("Submit")
