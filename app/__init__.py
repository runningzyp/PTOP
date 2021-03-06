from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.index'
login_manager.login_message = "请登录后 访问此页."


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config["default"])
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True  # 使用本地cdn
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .admin import admin as admin_blueprit
    app.register_blueprint(admin_blueprit, url_prefix='/admin')
    return app
