from flask import render_template, session, redirect, url_for, current_app
from flask import request
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        username = request.form.get('ID')
        print('hello')
        print(type(username))
        print(username)
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = username
        return redirect(url_for('main.user', username=username))

    return render_template('index.html',
                           name=session.get('name'),
                           known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)
