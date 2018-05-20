from flask import render_template, session, redirect, url_for, current_app
from flask import request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User, Data
from ..email import send_email
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        userkey = request.form.get('ID')
        print('hello')
        print(type(userkey))
        print(userkey)
        user = User.query.filter_by(userkey=userkey).first()
        print(user)
        if user is not None:
            login_user(user, True)
            return redirect(request.args.get('next')or url_for('main.user', username=user.username))
        flash('请输入正确的令牌')
    return render_template('index.html')


@main.route('/userlogout')
@login_required
def userlogout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if username != current_user.username:
        return render_template('404.html'), 404
    if request.method == 'POST':
        text = request.form.get('text')
        data = Data(text=text,
                    author=current_user._get_current_object())
        db.session.add(data)
        return redirect(url_for('.user', username=current_user.username))

    data = user.data.order_by(Data.timestamp.asc()).all()
    return render_template('user.html', data=data, user=user)


# 未登录用户无法访问
@main.route('/secret')
@login_required
def secret():
    return 'you can'
