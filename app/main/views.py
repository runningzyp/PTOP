from flask import render_template, session, redirect, url_for, current_app
from flask import request, flash
from flask_login import login_user, logout_user, login_required, login_manager
from flask_login import current_user
from .. import db
from ..models import User, Data, Article, ArticleType
from ..email import send_email
from . import main
from .. import auth
from .form import ArticleForm
from flask import send_from_directory  # 文件下载
from flask import jsonify
import datetime
from werkzeug import secure_filename  # 安全的文件名
from . import send_key
import json
from ..decorators import admin_required

from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
import oss2


import os
UPLOAD_FOLDER = os.getcwd() + "/files/"


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


@main.route('/write-blog', methods=['POST', 'GET'])
@login_required
@admin_required
def write_blog():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(
            body=form.body.data, title=form.title.data,
            article_type_id=int(form.article_id.data))
        db.session.add(article)
        return redirect(url_for('.blogs'))
    return render_template('wirte_blog.html', form=form)


@main.route('/blogs')
def blogs():
    # flash('请输入正确的令牌')
    # articles = Article.query.order_by(Article.timestamp.desc()).all()
    essay_s = Article.query.filter_by(article_type_id='2').order_by(
        Article.timestamp.desc()).all()
    funny_s = Article.query.filter_by(article_type_id='3').order_by(
        Article.timestamp.desc()).all()
    study_s = Article.query.filter_by(article_type_id='1').order_by(
        Article.timestamp.desc()).all()
    article_essay = []
    article_funny = []
    article_study = []
    articles = [article_essay, article_funny, article_study]
    count_1 = Article.query.filter_by(article_type_id='2').count()
    count_2 = Article.query.filter_by(article_type_id='3').count()
    count_3 = Article.query.filter_by(article_type_id='1').count()

    for i in range(0, count_1, 4):
        article_essay.append(essay_s[i:i+4])
    for i in range(0, count_2, 4):
        article_funny.append(funny_s[i:i+4])
    for i in range(0, count_3, 4):
        article_study.append(study_s[i:i+4])
    return render_template('blogs.html', article_essay=article_essay,
                           article_funny=article_funny,
                           article_study=article_study)


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


@login_required
@main.route('/test', methods=['GET', 'POST'])
def test():
    access_key_id = 'LTAInn4CiOcTMupp'
    access_key_secret = 'YNHxZ7QdZ160zmMO0kmLu2QJ6MtA3A'
    bucket_name = 'zhanyunpeng1995'
    endpoint = 'oss-cn-shanghai.aliyuncs.com'
    sts_role_arn = 'acs:ram::1158764349830607:role/oss-scaner'
    token = send_key.fetch_sts_token(
        access_key_id, access_key_secret, sts_role_arn)
    print(token.access_key_id)
    print(token.access_key_secret)
    print(token.security_token)
    return 'hello'
# 未登录用户无法访问


@main.route('/register')
def turn():
    return redirect(url_for('auth.register'))


@main.route('/secret')
@login_required
def secret():
    return 'you can'
