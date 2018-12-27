import json
import datetime

from flask import render_template, request, flash
from flask import redirect, url_for
from flask_login import login_user, logout_user, login_required
from flask import jsonify

from .import admin
from .forms import LoginForm, ArticleForm
from .. import db
from ..models import User, Article, ArticleType
from random import Random
from ..decorators import admin_required
import oss2

BLOG_IMAGE = ''


@admin.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data, password=form.password.data).first()
        print(user)
        if user is not None:
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next')or url_for('admin.admin'))
        flash('禁止登录')
    return render_template('admin/admin_login.html', form=form)


@admin.route('/admin-logout')
@admin_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.admin'))


# 获取文章列表
@admin.route('/get-blog', methods=['GET', 'POST'])
@admin_required
def get_blog():
    if request.method == "POST":
        data = json.loads(request.get_data())
        page = int(data['page'])
        pagination = Article.query.order_by(Article.timestamp.desc()).paginate(
            page, per_page=10, error_out=False)
        articles = pagination.items
        return jsonify({
            'article': [article.to_json() for article in articles],
            'count': pagination.total,
            'pages': pagination.pages
        })


# 获取用户列表
@admin.route('/get-user', methods=['GET', 'POST'])
@admin_required
def get_user():
    if request.method == "POST":
        data = json.loads(request.get_data())
        page = int(data['page'])
        pagination = User.query.paginate(
            page, per_page=10, error_out=False)
        users = pagination.items
        return jsonify({
            'user': [user.to_json() for user in users],
            'count': pagination.total,
            'pages': pagination.pages
        })


@admin.route('/upload_blog_img', methods=['POST', 'GET'])
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


@admin.route('/', methods=['POST', 'GET'])
@admin_required
def admin():
    global BLOG_IMAGE

    form = ArticleForm()
    form.article_type_id.choices = [(v.id, v.name)
                                    for v in ArticleType.query.all()]
    if form.validate_on_submit():

        article = Article(
            body=form.body.data,
            title=form.title.data,
            blog_images=BLOG_IMAGE,
            # timestamp=datetime.utcnow(),
            article_type_id=int(form.article_type_id.data))
        db.session.add(article)
        return redirect(url_for('main.blogs'))
    print(BLOG_IMAGE)
    BLOG_IMAGE = ''
    article_pagination = Article.query.paginate(
        1, per_page=10, error_out=False)
    user_pagination = User.query.paginate(
        1, per_page=10, error_out=False)
    article_pages = [x+1 for x in range(article_pagination.pages)]
    user_pages = [x+1 for x in range(user_pagination.pages)]
    return render_template('admin/admin.html', form=form,
                           article_pages=article_pages, user_pages=user_pages)
