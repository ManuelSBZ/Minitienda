from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import FloatField, StringField,IntegerField, TextField, SubmitField,SelectField,FileField,TextAreaField,PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo






class Carrito(FlaskForm):
    cantidad=SelectField("Cantidad" , coerce=int)
    submit=SubmitField("Submit")

                            
