import os
import json
from datetime import timedelta
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))

with open("config.json", 'r')as f:
    flag = json.loads(f.read())
dev_env = flag["dev"]
pro_env = flag['pro']
admin = flag['admin']
curr_secret_key = flag['secret_key']
mail_username = flag['mail_username']
mail_password = flag['mail_password']
mail_port = flag['mail_port']
mail_server = flag['mail_server']


class Config:

    SECRET_KEY = curr_secret_key
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 数据库修改，模型自动修改 False
    SQLALCHEMY_ECH0 = False  # 查询时显示原生sql语句
    MAIL_SERVER = mail_server
    MAIL_PORT = mail_port
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = mail_username
    MAIL_PASSWORD = mail_password
    FLASKY_MAIL_SUBJECT_PREFIX = '[香菜花]'
    FLASKY_MAIL_SENDER = mail_username
    FLASKY_ADMIN = admin
    UPLOAD_FOLDER = os.getcwd() + "/files/"  # 用户上传目录
    FLASKY_ARTICLE_PER_PAGE = 1  # 每页显示数量

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    RESULT_BACKEND = 'redis://localhost:6379/0' # celery 

    VERIFY_CODE_EXPIRE = 300  # 验证吗过期时间
    # gunicorn
    daemon = True

    # celery
    BEAT_SCHEDULE = {
        # 定义任务名称：import_data
        # 执行规则：每天运行一次
        "clear_code": {
            'task': 'clear_verify_code',
            'schedule': crontab(minute=0, hour=0)
        }
    }

    # flask-caching
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    '''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'data-dev.sqlite')
    '''
    SQLALCHEMY_DATABASE_URI = dev_env


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = pro_env


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
