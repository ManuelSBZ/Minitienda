
def create_app(configfile):
    
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(configfile)


    from .articles import article
    from .categories import category
    from .session_user import session_user
    from .shopping_cart import shopping_cart
    
    app.register_blueprint(article)
    app.register_blueprint(category)
    app.register_blueprint(session_user)
    app.register_blueprint(shopping_cart)

    from .ext import api,db,ma,migrate
    db.init_app(app)
    ma.init_app(app)
    api.init_app(app,api_v1)
    migrate.init_app(app,db)

    return app