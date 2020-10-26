
def create_app(configfile):
    
    from flask import Flask
    app = Flask(__name__)
    app.config.from_pyfile(configfile)

    from .models import Usuarios
    from .articles import article
    from .categories import category
    from .session_user import session_user
    from .shopping_cart import shopping_cart
    from .main import main
    
    app.register_blueprint(article)
    app.register_blueprint(category)
    app.register_blueprint(session_user)
    app.register_blueprint(shopping_cart)
    app.register_blueprint(main)
    @app.route("/login/", methods=['GET','POST'])
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
                next=request.args.get('next')
                return redirect(next or url_for("view_inicio"))
            else:
                form.password.errors.append("Contraseña incorrecta, por favor intente de nuevo")
        return render_template("login.html", form =form, url= 'log_in')


    from .ext import db,migrate,login_manager
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    login_manager.login_view="log_in"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuarios.query.get(int(user_id))
    

    return app