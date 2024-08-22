from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "SECTRET_KEY"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .auth import auth
    from .sponsor import sponsor
    from .influencer import influencer
    from .admin import admin

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(sponsor, url_prefix="/sponsor")
    app.register_blueprint(influencer, url_prefix="/influencer")
    app.register_blueprint(admin, url_prefix="/admin")

    from .models import User

    with app.app_context():
        db.create_all()
    login_manager = LoginManager()
    login_manager.login_view = "routes.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("mad1/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
