from flask import Blueprint
fish_bp = Blueprint('fish', __name__)
from .views import *