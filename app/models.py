
import bleach
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from markdown import markdown

from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
#from .decorators import admin_required


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    userkey = db.Column(db.String(10), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    data = db.relationship('Data', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # print(current_app.config['FLASKY_ADMIN'])
            #print(self.email == current_app.config['FLASKY_ADMIN'])
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                self.userkey = None
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    filename = db.Column(db.String(128), default=None)
    sec_filename = db.Column(db.String(128), default=None)
    filetype = db.Column(db.String(10), default=None)
    device_type = db.Column(db.String(10), default=None)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    blog_images = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    article_type_id = db.Column(db.Integer, db.ForeignKey('articletypes.id'))
    body_html = db.Column(db.Text)

    def to_json(self):
        json_article = {
            'id': self.id,
            'url': url_for('main.blog', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'blog_imgaes': self.blog_images
        }
        return json_article

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiaor):
        allow_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                      'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'br',
                      'table', 'tr', 'td']
        # 转换markdown为html，并清洗html标签
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,
                     extensions=['markdown.extensions.toc',
                                 'markdown.extensions.tables'],
                     output_form='html'),
            tags=allow_tags, strip=True,
            attributes={
                '*': ['class'],
                'a': ['href', 'rel'],
                'img': ['src', 'alt'],  # 支持<img src …>标签和属性
            }
        ))

    def __repr__(self):
        return '<Article %s>' % self.title
    '''
    @staticmethod
    def generate_fake(count=100):
        
        # 测试数据,生产环境不需要
        
        from random import seed
        from random import randint
        import forgery_py

        seed()
        for i in range(count):
            a = Article(title=forgery_py.lorem_ipsum.title(),
                        body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),
                        article_type_id=randint(1, 3),
                        body_html=None
                        )
            db.session.add(a)
            db.session.commit()
    '''


db.event.listen(Article.body, 'set', Article.on_changed_body)


class ArticleType(db.Model):
    __tablename__ = 'articletypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship(
        'Article', backref='article_type', lazy='dynamic')

    @staticmethod
    def insert():
        types = ('study', 'essay', 'funny')
        for t in types:
            _type = ArticleType.query.filter_by(name=t).first()
            if _type is None:
                _type = ArticleType(name=t)
            db.session.add(_type)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
