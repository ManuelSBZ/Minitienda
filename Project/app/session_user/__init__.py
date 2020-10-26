from flask import Blueprint

session_user= Blueprint("session_user",__name__,template_folder="templates")

from .views import *