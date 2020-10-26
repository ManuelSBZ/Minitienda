from flask import Blueprint

shopping_cart= Blueprint("shopping_cart",__name__,template_folder="templates")

from .views import *