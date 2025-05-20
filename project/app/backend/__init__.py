# backend/__init__.py

from flask import Flask
from .config     import DevelopmentConfig, ProductionConfig
from .extensions import db, migrate, ma

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.config.from_pyfile('config.py', silent=True)

    # 확장(Extension) 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # Blueprint 등록
    from .main.views          import main_bp
    from .weather.views       import weather_bp
    from .fish.views          import fish_bp
    from .fishingPlace.views  import fishing_place_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(fish_bp)
    app.register_blueprint(fishing_place_bp)

    return app
