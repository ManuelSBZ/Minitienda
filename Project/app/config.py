import os 

SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

PWD=os.getcwd()

DEBUG=True

SQLALCHEMY_DATABASE_URI ='sqlite:///{}/dbase.db'.format(PWD)
# SQL_ALCHEMY_URI='sqlite:///C:/Users/Manuel/Desktop/Flask/Minitienda/Develop_env/Project/dbase.db'
SQLALCHEMY_TRACK_MODIFICATIONS=False

