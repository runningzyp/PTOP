from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, SelectField
from wtforms import ValidationError
from wtforms.validators import Required


class ArticleForm(FlaskForm):
    body = TextAreaField("今天心情怎么样", validators=[Required()])
    article_id = SelectField(choices=[("2", "随想"), ("3", "趣事"), ("1", "技术")])
    title = StringField("请输入标题")
    submit = SubmitField("提交")
