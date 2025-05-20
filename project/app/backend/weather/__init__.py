# app/weather/__init__.py
from flask import Blueprint

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

# 블루프린트가 사용할 뷰 함수(들)를 import
from .views import *
