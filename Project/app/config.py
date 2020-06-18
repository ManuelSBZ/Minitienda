import os 

SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

PWD=os.getcwd()

DEBUG=True
ENV="Development"
#para que funcione @login_required de Flask-Login
# LOGIN_DISABLED=False

# SQLALCHEMY_DATABASE_URI ='mysql+pymysql://msb:qwe@localhost/Minitienda?charset=utf8mb4'
SQLALCHEMY_DATABASE_URI ='postgres://postgres:rareware@localhost/Minitienda'
# SQLALCHEMY_DATABASE_URI ='sqlite:///{}/dbase.db'.format(PWD)
# SQL_ALCHEMY_URI='sqlite:///C:/Users/Manuel/Desktop/Flask/Minitienda/Develop_env/Project/dbase.db'
SQLALCHEMY_TRACK_MODIFICATIONS=False

