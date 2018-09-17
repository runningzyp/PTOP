from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, Equ
from wtforms import ValidationError
from ..models import User
