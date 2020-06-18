from . import session_user
from ..models import Usuarios
from flask import current_app, render_template,abort,request,redirect, url_for
from flask_login import login_user,logout_user,current_user, login_required
from .forms import SigninForm,LoginForm, CambiarContraseña
from ..ext import db#sustituir por db en ext


@session_user.route("/signin/", methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("main.view_inicio"))

    form= SigninForm()
    if form.validate_on_submit():
        print("comprobacion de usuario")
        usuario_existe: list = Usuarios.query.filter_by(username=form.username.data).all()
        
        if len(usuario_existe)==0 :
            print("creando usuario")  
            data_form={key:value 
                        for k in Usuarios.__dict__.keys() for key,value in form.data.items()
                        if key==k}
            print(data_form)
            nuevo_usuario=Usuarios(**data_form)
            nuevo_usuario.admin=False
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for("main.view_inicio"))
        else:
            print("usuario existe")
            existe=True
            return render_template("signin.html", form=form, url='session_user.signin',existe=existe)
    print("no se ha enviado nada")
    return render_template("signin.html", form=form, url='session_user.signin')

# login
@session_user.route("/login/", methods=['GET','POST'])
def log_in():
    if current_user.is_authenticated:
        abort(404, "ya esta logueado")
    
    form=LoginForm()

    if form.validate_on_submit():
        usuario=Usuarios.query.filter_by(username=form.username.data).first()
        if usuario==None:
            form.username.errors.append(f"usuario {form.username.data} no existe")
            return render_template("login.html", form =form, url='log_in')
        print(form.data)
        if usuario.verify_password(form.password.data):
            #crea la session de usuario con los datos del usuario y carga con info del usuario a @login_manager.userloader 
            login_user(usuario)
            # apunta a un controlador de un template que requiere estar logueado.
            next=request.args.get('next')
            return redirect(next or url_for("main.view_inicio"))
        else:
            form.password.errors.append("Contraseña incorrecta, por favor intente de nuevo")
    return render_template("login.html", form =form, url= 'log_in')

@session_user.route("/logout/", methods=['GET','POST'])
def log_out():
    logout_user()
    return redirect(url_for("main.view_inicio"))

@session_user.route("/editar/perfil/<int:id_usuario>", methods=["GET","POST"])
@login_required
def editar_perfil(id_usuario):
    usuario=Usuarios.query.get(id_usuario)
    form=SigninForm(request.form,obj=usuario)
    del form.password
    del form.cpassword
    if usuario is None:
        abort(404,message='usuario no existe')
    if form.validate_on_submit():
        data_form={key:value 
                        for k in Usuarios.__dict__.keys() for key,value in form.data.items() if key==k}
        try:
            Usuarios.query.filter_by(id=id_usuario).update(data_form)
            db.session.commit()
            login_user(usuario)
            return redirect(url_for('main.view_inicio'))
        except:
            form.username.errors.append("username ya existente")
            
    return render_template("signin.html", form=form, editar=True, url="session_user.editar_perfil")

@session_user.route("/editar/contraseña/<int:id_usuario>", methods=['GET','POST'])
@login_required
def editar_contraseña(id_usuario):
    form=CambiarContraseña()
    usuario=Usuarios.query.get(id_usuario)
    if usuario.id != current_user.id:
        abort(404, "usuario no coincide")
    if form.validate_on_submit():
        data_form={key:value 
                    for k in Usuarios.__dict__.keys() for key,value in form.data.items() if key==k}
        print(f'la dataaa : {data_form.keys()}')
        usuario.password=data_form["password"]
        # print(f"datos = {form.data}")
        # usuario=Usuarios.query.get(id_usuario)
        # form.populate_obj(usuario)
        db.session.commit()
        return redirect(url_for("main.view_inicio"))
    return render_template("cambiarcontraseña.html", form=form)
