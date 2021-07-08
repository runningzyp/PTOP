from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config, Config
from flask_login import LoginManager
from flask_caching import Cache

from celery import Celery  # 后台任务

app = Flask(__name__)


cache = Cache()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)  # 创建celery实例


login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "main.index"
login_manager.login_message = "请登录后 访问此页."


def filter_double_sort(ls):
    return ls.split["/"][-1]


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config["default"])

    app.add_template_filter(filter_double_sort, "last")

    app.config["BOOTSTRAP_SERVE_LOCAL"] = True  # 使用本地cdn
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    celery.conf.update(app.config)  # celery配置

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    from .admin import admin as admin_blueprit

    app.register_blueprint(admin_blueprit, url_prefix="/admin")
    return app
