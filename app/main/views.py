import os
import json
import datetime
import time

from flask import render_template, session, redirect, url_for, current_app
from flask import request, flash
from flask_login import login_user, logout_user, login_required, login_manager
from flask_login import current_user
from .. import db
from ..models import User, Data, Article, ArticleType
from ..email import send_email
from . import main
from .. import auth
from .forms import ArticleForm
from flask import send_from_directory  # 文件下载
from flask import jsonify

from werkzeug import secure_filename  # 安全的文件名

from ..decorators import admin_required


from ..net_tools import ali_oss




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
            login_user(user, True)  # true 记住用户
            return redirect(url_for('main.user', username=user.username))
        flash('请输入正确的令牌')
    return render_template('index.html')


@main.route('/blogs', methods=['POST', 'GET'])
def blogs():
    if request.method == "POST":
        type_dic = {
            'study': 1,
            'essay': 2,
            'funny': 3
        }
        data = json.loads(request.get_data().decode('utf8'))
        print(data)
        page = data['page']
        article_type = data['article_type']
        print(article_type)
        article_type_id = type_dic[article_type]

        pagination = Article.query.filter_by(article_type_id=article_type_id).paginate(
            page, per_page=current_app.config['FLASKY_ARTICLE_PER_PAGE'],
            error_out=False)
        articles = pagination.items
        article = articles[0]

        prev = None
        if pagination.has_prev:
            prev = url_for('main.blogs', page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('main.blogs', page=page+1, _external=True)
        return jsonify({
            'article': article.to_json(),
            'prev': prev,
            'next': next,
            'count': pagination.total
        })
    page = 1  # 默认第一页
    articles = []
    counts = []
    for i in range(3):
        pagination = Article.query.filter_by(article_type_id=i+1).paginate(
            page, per_page=current_app.config['FLASKY_ARTICLE_PER_PAGE'],
            error_out=False)
        articles.append(pagination.items)
        print(pagination.items)
        counts.append(pagination.total)
    return render_template('blogs.html', articles=articles, counts=counts)


@main.route('/blog/<int:id>')
def blog(id):
    blog = Article.query.get_or_404(id)
    return render_template('blog.html', blog=blog)


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
    host = ali_oss.get_host()+'/'
    return render_template('user.html', data=data, user=user, host=host)


@main.route('/get-token', methods=['POST', 'GET'])
def get_token():
    user_dir = current_user.email+"/"
    if request.method == 'POST':
        return ali_oss.get_token(user_dir)


@main.route('/call-back', methods=['POST', 'GET'])
def call_back():
    if request.method == 'POST':

        host = ali_oss.get_host()

        sec_filename = request.form.get('filename')
        filename = sec_filename.split('/')[-1]
        email = sec_filename.split('/')[0]
        user = User.query.filter_by(email=email).first()
        bucket = request.form.get('bucket')
        filetype = request.form.get('mimeType')  # 文件类型
        
        dt = datetime.datetime.utcnow()
        
        data = Data(filename=filename, sec_filename=sec_filename,
                    filetype=filetype,
                    author=user)
        db.session.add(data)
        
        url = host+'/' + sec_filename
        return json.dumps({'filename': filename, 'url': url})
    return 'success'


@main.route('/_sendmessage')
@login_required
def sendmessage():
    text = request.args.get('text', '')
    device_type = request.args.get('device_type', '')
    if text is not None:
        data = Data(text=text,
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

            user = User.query.filter_by(username=current_user.username).first()
            persional_folder = UPLOAD_FOLDER+user.email
            print(persional_folder)
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
    user = User.query.filter_by(username=current_user.username).first()
    persional_folder = UPLOAD_FOLDER+user.email
    return send_from_directory(persional_folder,
                               filename)


@main.route('/register')
def turn():
    return redirect(url_for('auth.register'))


@main.route('/secret')
@login_required
def secret():
    return 'you can'


@main.route('/about_me')
def about():
    return render_template('about_me.html')
