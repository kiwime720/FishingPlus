from flask import Blueprint

fishingPlace_bp = Blueprint('fishingPlace', __name__, url_prefix='/fisingPlace')

from .views import *