from flask import render_template, request, flash
from flask import redirect, url_for
from flask_login import login_user
from .import auth
from .forms import RegisterForm, LoginForm
from .. import db
from ..models import User
from random import Random

import os
UPLOAD_FOLDER = os.getcwd() + "/files/"


def random_str(randomlength=6):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        while (True):
            userkey = random_str(6)
            user = User.query.filter_by(userkey=userkey).first()
            if user is None:
                break
        newuser = User(userkey=userkey, username=form.username.data,
                       password=form.password.data, email=form.email.data)
        db.session.add(newuser)
        path = UPLOAD_FOLDER + newuser.email
        print(path)
        if os.path.exists(path) is False:
            os.makedirs(path)
        return render_template('auth/success.html', userkey=userkey)
    return render_template('auth/register.html', form=form)

