# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # backend/.env 로부터 환경 변수 로드

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///:memory:')
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False

    API_KEYS = {
        'weather': os.getenv('WEATHER_API_KEY', ''),
        'fish':    os.getenv('FISH_API_KEY',    ''),
        'sites':   os.getenv('SITES_API_KEY',   ''),
    }

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(BaseConfig):
    DEBUG = False
