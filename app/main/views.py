from flask import render_template, session, redirect, url_for, current_app
from flask import request, flash
from flask_login import login_user, logout_user, login_required, login_manager, current_user
from .. import db
from ..models import User, Data
from ..email import send_email
from . import main
from .forms import NameForm
from flask import send_from_directory  # 文件下载
from flask import jsonify
import datetime
from werkzeug import secure_filename  # 安全的文件名

import os
UPLOAD_FOLDER = os.getcwd() + "/app/static/files/"


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
            return redirect(url_for('main.user', username=user.username))
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

    data = user.data.order_by(Data.timestamp.asc()).all()
    return render_template('user.html', data=data, user=user)


@main.route('/_sendmessage')
@login_required
def sendmessage():
    text = request.args.get('text', '')
    device_type = request.args.get('device_type', '')
    if text is not None:
        data = Data(text=text, device_type=device_type,
                    author=current_user._get_current_object())
        db.session.add(data)
    return jsonify(result='success')


@main.route('/_sendfile', methods=['GET', 'POST'])
@login_required
def sendfile():
    if request.method == "POST":
        try:
            dt = datetime.datetime.utcnow()
            sec_key = dt.strftime("%Y-%m-%d-%H-%M-%S")
            file = request.files['file']
            device_type = request.args.get('device_type', '')
            filename = file.filename
            sec_filename = '['+sec_key + ']' + filename
            persional_folder = UPLOAD_FOLDER
            file.save(os.path.join(persional_folder, sec_filename))
            data = Data(filename=filename, sec_filename=sec_filename,
                        device_type=device_type,
                        author=current_user._get_current_object())
            db.session.add(data)
        except:
            file = None
        return jsonify({'name': filename, 'url': sec_filename})


@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER,
                               filename)

# 未登录用户无法访问


@main.route('/secret')
@login_required
def secret():
    return 'you can'
