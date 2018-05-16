from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class DataForm(FlaskForm):
    text = TextAreaField('说什么', validators=[Required()])
    submit = SubmitField('发表')
