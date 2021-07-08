from datetime import datetime, timedelta
import hashlib
import imp
from werkzeug.security import generate_password_hash, check_password_hash

# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for

from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from flask_sqlalchemy import event

# from .decorators import admin_required

from .utils import ali_oss


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")
    aliconfig = db.relationship("AliConfig", backref="role", uselist=False)

    @staticmethod
    def insert_roles():
        roles = {
            "User": (
                Permission.FOLLOW
                | Permission.COMMENT
                | Permission.WRITE_ARTICLES,
                True,
            ),
            "Moderator": (
                Permission.FOLLOW
                | Permission.COMMENT
                | Permission.WRITE_ARTICLES
                | Permission.MODERATE_COMMENTS,
                False,
            ),
            "Administrator": (0xFF, False),
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
        return "<Role %r>" % self.name


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    userkey = db.Column(db.String(10), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    join_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    data = db.relationship("Data", backref="owner", lazy="dynamic")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(permissions=0xFF).first()
                self.userkey = None
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return (
            self.role is not None
            and (self.role.permissions & permissions) == permissions
        )

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(slef):
        raise AttributeError("密码不可读")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User %r>" % self.username

    def to_json(self):
        json_user = {
            "id": self.id,
            "username": self.username,
            "role_id": self.role_id,
            "role": self.role.name,
            "join_time": self.join_time,
        }
        return json_user


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    filename = db.Column(db.String(128), default=None)
    size = db.Column(db.String(128))
    url_prefix = db.Column(db.String(128))
    filetype = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @property
    def url(self):
        from .utils.ali_oss import get_bucket
        bucket = get_bucket()
        url = bucket.sign_url('GET', self.filename, 3000)
        return url


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    finish_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_change_time = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )
    article_type_id = db.Column(db.Integer, db.ForeignKey("articletypes.id"))
    body_origin = db.Column(db.Text)

    visit_num = db.Column(db.Integer, default=0)

    article_status = db.Column(db.String(12), default="submited")

    images = db.relationship("ArticleImage", backref="article", lazy="dynamic")
    # 评论
    comments = db.relationship(
        "Comment",
        backref="article",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def local_time(self):
        return (self.finish_time + timedelta(hours=8)).strftime(
            "%Y年%m月%d日 %H:%M"
        )

    def admin_to_json(self):
        json_article = {
            "id": self.id,
            "title": self.title,
            "finish_time": self.finish_time,
            "last_change_time": self.last_change_time,
            "type_id": self.article_type.id,
            "type_name": self.article_type.name,
            "url": url_for("main.blog", id=self.id, _external=True),
        }
        return json_article

    def to_json(self):
        json_article = {
            "id": self.id,
            "url": url_for("main.blog", id=self.id, _external=True),
            "title": self.title,
            "body_origin": self.body_origin,
            "finish_time": self.finish_time,
            "last_change_time": self.last_change_time,
            "article_type_id": self.article_type_id,
            "article_type": self.article_type.name,
        }
        return json_article

    def __repr__(self):
        return "<Article %s>" % self.title


class ArticleImage(db.Model):
    __tablename__ = "articleimages"
    id = db.Column(db.Integer, primary_key=True)

    origin_name = db.Column(db.String(128))
    full_path = db.Column(db.String(128))
    size = db.Column(db.String(128))
    image_url = db.Column(db.String(128))
    add_time = db.Column(db.DateTime, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"))


class ArticleType(db.Model):
    __tablename__ = "articletypes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship(
        "Article", backref="article_type", lazy="dynamic"
    )

    @staticmethod
    def insert():
        types = ("study", "essay", "funny")
        for t in types:
            _type = ArticleType.query.filter_by(name=t).first()
            if _type is None:
                _type = ArticleType(name=t)
            db.session.add(_type)
        db.session.commit()


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    email_hash = db.Column(db.String(64))
    name = db.Column(db.String(64))
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    reply = db.Column(db.Text)
    reply_confirm = db.Column(db.Boolean, default=False)
    article_id = db.Column(
        db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE")
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.email is not None and self.email_hash is None:
            self.email_hash = hashlib.md5(
                self.email.encode("utf-8")
            ).hexdigest()

    def to_json(self):
        json_article = {
            "id": self.id,
            "email": self.email,
            "hash_email": self.hash_email,
            "content": self.content,
            "time": self.time,
            "reply": self.reply,
            "article_id": self.article_id,
            "aricle_title": self.article.title,
        }
        return json_article

    @property
    def hash_email(self):
        return hashlib.md5(self.email.encode("utf-8")).hexdigest()

    @property
    def local_time(self):
        return self.time + timedelta(hours=8)


class AliConfig(db.Model):
    __tablename__ = "aliconfig"
    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String(32))

    access_key_id = db.Column(db.String(128))
    access_key_secret = db.Column(db.String(128))
    host = db.Column(db.String(128))
    bucket = db.Column(db.String(128))
    callback_url = db.Column(db.String(128))
    expire_time = db.Column(db.Integer)
    url_prefix = db.Column(db.String(128))

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))


# 验证码


class VerificationCode(db.Model):
    __tablename__ = "verificationcodes"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32))
    code = db.Column(db.String(6))
    expire_time = db.Column(
        db.DateTime,
        default=datetime.utcnow() + timedelta(minutes=30),
        index=True,
    )


class Settings(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    mail_username = db.Column(db.String(32))
    mail_password = db.Column(db.String(32))
    mail_post = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
