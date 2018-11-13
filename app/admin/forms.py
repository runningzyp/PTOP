from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('<span class="glyphicon glyphicon-envelope"></span> 邮箱',
                        validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('<span class="glyphicon glyphicon-lock"></span> 密码',
                             validators=[Required()])

    remember_me = BooleanField('保持在线')

    submit = SubmitField('登录')


class ArticleForm(FlaskForm):
    body = TextAreaField('今天心情怎么样', validators=[Required()])
    article_type_id = SelectField(
        choices='', coerce=int)
    title = StringField('请输入标题')
    submit = SubmitField("提交")
