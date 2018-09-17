from flask import render_template, request, flash, redirect, url_for
from .import auth
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
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        sel = User.query.filter_by(email=email).first()
        if sel is not None:
            print('存在')
            flash('该用户已被注册')
            return redirect(url_for('auth.register'))
        while (True):
            userkey = random_str(6)
            user = User.query.filter_by(userkey=userkey).first()
            if user is None:
                break
        newuser = User(userkey=userkey, username=username,
                       password=password, email=email)
        db.session.add(newuser)
        path = UPLOAD_FOLDER + email
        print(path)
        if (not os.path.exists(path)):
            os.makedirs(path)
        return render_template('auth/success.html', userkey=userkey)
    return render_template('auth/register.html')
