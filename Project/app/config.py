import os 

SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

PWD=os.getcwd()

DEBUG=True
FLASK_ENV="Development"
#para que funcione @login_required de Flask-Login
# LOGIN_DISABLED=False

# SQLALCHEMY_DATABASE_URI ='mysql+pymysql://msb:qwe@localhost/Minitienda?charset=utf8mb4'
# SQLALCHEMY_DATABASE_URI ='postgres://postgres:redsony10@localhost/db_mvc'
# SQLALCHEMY_DATABASE_URI ='sqlite:///{}/dbase.db'.format(PWD)
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", None)
SQLALCHEMY_TRACK_MODIFICATIONS=False

