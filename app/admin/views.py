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
        pagination = Article.query.filter_by(is_submit=True).order_by(
            Article.finish_time.desc()).paginate(
            page, per_page=10, error_out=False)
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
        img = request.files['upload']

        img.filename = str(uuid.uuid1())+'.'+img.filename.split('.')[-1]
        upload_folder = 'blogimages'+'/' +\
            datetime.datetime.now().strftime('%Y-%m-%d')+'/'  # 日期表示文件夹
        full_path = upload_folder + img.filename  # 完整路径
        try:
            bucket.put_object(upload_folder+img.filename, img)
        except Exception as e:
            print(e)
        else:
            return jsonify({"uploaded": "true",
                            "url": "https://xiangcaihua-blog.oss-cn-shanghai.aliyuncs.com/"+full_path})
        return jsonify({"uploaded": "false", "message": "wrong"})


# @admin.route('/post-blog', methods=['POST'])
# @admin_required
# def post_blog():
#     data = json.loads(request.get_data().decode('utf-8'))
#     print(session['current_article'])
#     try:
#         print(session['current_article'])
#         artilce = Article.query.get(
#             session['current_article'])  # 从seeion获取当前编辑文章ID
#         artilce.title = data['title']
#         artilce.body = data['body']
#         article.article_type_id = data('type')
#         article.last_change_time = datetime.datetime.utcnow()
#         if artilce.finish is None:
#             artilce.finish = datetime.datetime.utcnow()
#         article.is_submit = True
#         db.session.commit()
#     except Exception as e:
#         print(e)
#         return jsonify({
#             'status': '400',
#             'message': 'failed'
#         })
#     else:
#         url = request.url_root+"admin"
#         return jsonify({
#             'status': '200',
#             'message': 'success',
#             'url': url
#         })

# 初始化草稿


@admin.route('/write-blog', methods=['POST', 'GET'])
@admin_required
def write_blog():
    form = ArticleForm()
    types = ArticleType.query.all()
    if request.method == "POST":
        title = request.form.get('title')
        body_html = request.form.get('body')
        aritcle_type_id = request.form.get('type')
        article = Article(title=title, body_html=body_html,
                          article_type_id=aritcle_type_id)
        db.session.add(article)
        db.session.commit()
        print(article.finish_time)
        return redirect(url_for('main.blog', id=article.id))
    return render_template('admin/write_blog.html', form=form, types=types)


@admin.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        data = request.get_data()

        print('hello')


@admin.route('/', methods=['POST', 'GET'])
@admin_required
def admin():
    return render_template('admin/main.html')
