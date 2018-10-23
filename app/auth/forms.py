from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import TextAreaField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class RegisterForm(FlaskForm):
    email = StringField('<span class="glyphicon glyphicon-envelope"></span> 邮箱',
                        validators=[Required(), Length(1, 64),
                                    Email()])

    username = StringField('<span class="glyphicon glyphicon-user"></span> 用户名',
                           validators=[Required(), Length(
                               1, 64), Regexp('^[A-Za-z][A-Za-z0-9.]*$', 0,
                                              '用户名只能是字母数字或点')])
    password = PasswordField(
        '<span class="glyphicon glyphicon-lock"></span> 密码',
        validators=[Required(), EqualTo('password2', message='密码必须相同')])
    password2 = PasswordField(
        '<span class="glyphicon glyphicon-lock"></span> 重复密码',
        validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被使用')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    password = PasswordField('密码', validators=[Required()])

    remember_me = BooleanField('保持在线')

    submit = SubmitField('登录')
