from flask import Blueprint

article= Blueprint("article",__name__,template_folder="templates")

from .views import *