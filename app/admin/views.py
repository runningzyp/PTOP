import json
import datetime
import uuid

from flask import render_template, request, flash
from flask import redirect, url_for, session
from flask_login import login_user, logout_user, login_required
from flask import jsonify

from .import admin
from .forms import LoginForm, ArticleForm
from .. import db
from ..models import User, Article, ArticleType, ArticleImage
from random import Random
from ..decorators import admin_required
import oss2
from ..net_tools import ali_oss


@admin.route('/test/<int:id>', methods=['GET'])
def test(id):
    blog = Article.query.get(id).body_origin
    return render_template('test.html', blog=blog)


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
@admin.route('/get-blogs', methods=['GET', 'POST'])
@admin_required
def get_blogs():
    if request.method == "POST":
        print('hello')
        data = json.loads(request.get_data().decode('utf-8'))
        page = data['page']
        pagination = Article.query.order_by(
            Article.finish_time.desc()).paginate(
            page, per_page=data['limit'], error_out=False)

        articles = pagination.items
        return jsonify({'status': 200,
                        'message': 'success',
                        'count': pagination.total,
                        'data': [article.admin_to_json()
                                 for article in articles],
                        })
    return render_template('admin/get_blogs.html')


@admin.route('/delete-blog', methods=['GET', 'POST'])
@admin_required
def delete_blog():
    if request.method == "POST":

        bucket = ali_oss.get_bucket()

        data = json.loads(request.get_data().decode('utf-8'))
        id = data['id']
        aritcle = Article.query.get(id)
        if aritcle is not None:
            db.session.delete(aritcle)
            try:
                bucket.delete_object(str(aritcle.id)+'/')
            except Exception as e:
                print(e)
            else:
                return jsonify({
                    'status': 200,
                    'message': '删除成功'
                })


@admin.route('/upload-blog-image', methods=['POST', 'GET'])
@login_required
@admin_required
def upload_blog_img():
    if request.method == "POST":

        bucket = ali_oss.get_bucket()  # 从工具模块获取 bucket访问授权
        dt = datetime.datetime.utcnow()
        sec_key = dt.strftime("%Y-%m-%d-%H-%M-%S")

        # requests.get返回的是一个可迭代对象（Iterable）
        # 此时Python SDK会通过Chunked Encoding方式上传。

        img = request.files['image']

        img.filename = str(uuid.uuid1())+'.'+img.filename.split('.')[-1]
        upload_folder = 'blogimages'+'/' +\
            datetime.datetime.now().strftime('%Y-%m-%d')+'/'  # 日期表示文件夹
        full_path = upload_folder + img.filename  # 完整路径
        try:
            bucket.put_object(upload_folder+img.filename, img)
        except Exception as e:
            print(e)
        else:
            return jsonify({"status": "200",
                            "url": "https://xiangcaihua-blog.oss-cn-shanghai.aliyuncs.com/"+full_path
                            })
        return jsonify({
            "status": "400",
            "message": "could not upload this image"

        })


@admin.route('/write-blog', methods=['POST', 'GET'])
@admin_required
def write_blog():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf8'))
        title = data['title']
        body_origin = data['body_origin']
        body_html = data['body']

        # 第一次清洗contenteditable标签
        body_html = ''.join(body_html.split("contenteditable=\"true\""))
        # 第二次清洗table标签
        body_html = ''.join(body_html.split(
            "class=\"ck-editor__editable ck-editor__nested-editable\""))

        aritcle_type_id = data['type']
        article = Article(title=title, body_html=body_html, body_origin=body_origin,
                          article_type_id=aritcle_type_id)
        db.session.add(article)
        db.session.commit()
        return jsonify({
            'status': '200',
            'id':  article.id
        })
    form = ArticleForm()
    types = ArticleType.query.all()
    return render_template('admin/write_blog.html', form=form,
                           types=types, articlel=None, have_article=False)


@admin.route('/update-blog/<int:id>', methods=['POST', 'GET'])
@admin_required
def update_blog(id):
    '''
    更新博客文章
    '''
    article = Article.query.get_or_404(id)
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf8'))

        body_origin = data['body_origin']
        body_html = data['body']
        # 第一次清洗contenteditable标签
        body_html = ''.join(body_html.split("contenteditable=\"true\""))
        # 第二次清洗table标签
        body_html = ''.join(body_html.split(
            "class=\"ck-editor__editable ck-editor__nested-editable\""))

        article.title = data['title']
        article.aritcle_type_id = data['type']
        article.body_html = body_html
        article.body_origin = body_origin
        article.last_change_time = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({
            'status': '200',
            'id':  article.id
        })

    form = ArticleForm()
    types = ArticleType.query.all()
    return render_template('admin/write_blog.html', form=form,
                           types=types, article=article, have_article=True,)


@admin.route('/', methods=['POST', 'GET'])
@admin_required
def admin():
    blog_count = Article.query.count()
    user_count = User.query.count()
    return render_template('admin/main.html', blog_count=blog_count,
                           user_count=user_count)


###############################################################################
