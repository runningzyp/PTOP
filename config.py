import os
import json
basedir = os.path.abspath(os.path.dirname(__file__))


with open("config.json", 'r')as f:
    flag = json.loads(f.read())
DEV_ENV = flag["dev"]
PRO_ENV = flag['pro']
ADMIN = flag['admin']
CURR_SECRET_KEY = flag['secret_key']

class Config:

    SECRET_KEY = CURR_SECRET_KEY
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'zhanyunpeng1996@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'zhanyunpeng1996@163.com'
    FLASKY_ADMIN = ADMIN
    UPLOAD_FOLDER = os.getcwd() + "/files/"  # 用户上传目录
    FLASKY_ARTICLE_PER_PAGE = 1  # 每页显示数量

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    '''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'data-dev.sqlite')
    '''
    SQLALCHEMY_DATABASE_URI = DEV_ENV


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = PRO_ENV


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
