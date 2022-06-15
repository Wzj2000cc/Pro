from flask import Blueprint
from .views import *

index_blu = Blueprint('index', __name__, template_folder='templates', static_folder='static')

