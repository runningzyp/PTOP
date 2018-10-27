import os
import json
import datetime

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

from werkzeug import secure_filename  # 安全的文件名

from ..decorators import admin_required

from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
import oss2

from ..net_tools import appserver

# 阿里云模块

import time
import base64
UPLOAD_FOLDER = os.getcwd() + "/files/"
BLOG_IMAGE = ''


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
    global BLOG_IMAGE

    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(
            body=form.body.data, title=form.title.data,
            blog_images=BLOG_IMAGE,
            article_type_id=int(form.article_id.data))
        db.session.add(article)
        return redirect(url_for('.blogs'))
    print(BLOG_IMAGE)
    BLOG_IMAGE = ''
    return render_template('wirte_blog.html', form=form)


@main.route('/upload_blog_img', methods=['POST', 'GET'])
@login_required
@admin_required
def upload_blog_img():
    if request.method == "POST":
        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        auth = oss2.Auth('LTAIB5vPYWqfntRP', 'MGrtfdOjsjhf38xfLeLajRBp9iolTa')
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(
            auth, 'http://oss-cn-shanghai.aliyuncs.com',
            'xiangcaihua-blog')

        dt = datetime.datetime.utcnow()
        sec_key = dt.strftime("%Y-%m-%d-%H-%M-%S")

        # requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
        img = request.files['editormd-image-file']
        filename = img.filename
        sec_filename = '[' + sec_key + ']' + filename

        bucket.put_object(sec_filename, img)
        global BLOG_IMAGE
        BLOG_IMAGE += sec_filename+"<->"
        print(BLOG_IMAGE)

        img_address = "https://xiangcaihua-blog.oss-cn-shanghai.aliyuncs.com/" + sec_filename
        back = {
            "success": 1,
            "message": "提示的信息",
            "url": img_address
        }
        return json.dumps(back)


@main.route('/blogs', methods=['POST', 'GET'])
def blogs():
    if request.method == "POST":
        page = request.form.get('page', 1, type=int)
        article_type = request.form.get('article_type', 3, type=int)

        pagination = Article.query.filter_by(article_type_id=article_type).paginate(
            page, per_page=current_app.config['FLASKY_ARTICLE_PER_PAGE'],
            error_out=False)
        articles = pagination.items
        article = articles[0]
        print(article)
        print(type(article))
        print(article.to_json())
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
    page = 1
    article_type = 3
    pagination = Article.query.filter_by(article_type_id=article_type).paginate(
        page, per_page=current_app.config['FLASKY_ARTICLE_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    count = pagination.total
    print(count)
    return render_template('blogs.html', articles=articles, count=count)
    # flash('请输入正确的令牌')
    # articles = Article.query.order_by(Article.timestamp.desc()).all()
    # essay_s = Article.query.filter_by(article_type_id='2').order_by(
    #     Article.timestamp.desc()).all()
    # funny_s = Article.query.filter_by(article_type_id='3').order_by(
    #     Article.timestamp.desc()).all()
    # study_s = Article.query.filter_by(article_type_id='1').order_by(
    #     Article.timestamp.desc()).all()
    # article_essay = []
    # article_funny = []
    # article_study = []
    # articles = [article_essay, article_funny, article_study]
    # count_1 = Article.query.filter_by(article_type_id='2').count()
    # count_2 = Article.query.filter_by(article_type_id='3').count()
    # count_3 = Article.query.filter_by(article_type_id='1').count()

    # for i in range(0, count_1, 4):  # 每页显示4个数据,下同
    #     article_essay.append(essay_s[i:i+4])
    # for i in range(0, count_2, 4):
    #     article_funny.append(funny_s[i:i+4])
    # for i in range(0, count_3, 4):
    #     article_study.append(study_s[i:i+4])
    # return render_template('blogs.html', article_essay=article_essay,
    #                        article_funny=article_funny,
    #                        article_study=article_study,
    #                        test={'a': 2, 'b': 3})


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


@main.route('/register')
def turn():
    return redirect(url_for('auth.register'))


@main.route('/secret')
@login_required
def secret():
    return 'you can'
