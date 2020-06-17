from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import FloatField, StringField,IntegerField, TextField, SubmitField,SelectField,FileField,TextAreaField,PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo



class CreateCat(FlaskForm):
    nombre=StringField("Categoria", validators=[DataRequired("Por favor escriba una nueva categoria")])
    submit=SubmitField("Submit")

class DeleteForm(FlaskForm):
    si=SubmitField("Si" ,default=True)
    no=SubmitField("No" ,default=False)



                            
