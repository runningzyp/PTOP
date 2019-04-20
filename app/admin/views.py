import json
import datetime

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
            Article.timestamp.desc()).paginate(
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


# 获取用户列表
@admin.route('/get-user', methods=['GET', 'POST'])
@admin_required
def get_user():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        page = int(data['page'])
        pagination = User.query.paginate(
            page, per_page=10, error_out=False)
        users = pagination.items
        return jsonify({
            'user': [user.to_json() for user in users],
            'count': pagination.total,
            'pages': pagination.pages
        })


@admin.route('/upload-blog-img', methods=['POST', 'GET'])
@login_required
@admin_required
def upload_blog_img():
    if request.method == "POST":

        bucket = ali_oss.get_bucket()
        dt = datetime.datetime.utcnow()
        sec_key = dt.strftime("%Y-%m-%d-%H-%M-%S")

        # requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。

        article = Article.query.get(session['current_article'])
        index = article.id
        img = request.files['editormd-image-file']
        filename = img.filename
        sec_filename = "blogimages" + \
            str(index) + '/[' + sec_key + ']' + filename
        try:
            bucket.put_object(sec_filename, img)
        except Exception as e:
            print(e)
        else:
            image = ArticleImage(imagename=sec_filename)
            db.session.add(image)

            article.articleimages.append(image)
            img_address = "https://xiangcaihua-blog.oss-cn-shanghai.aliyuncs.com/" + sec_filename
        back = {
            "success": 1,
            "message": "提示的信息",
            "url": img_address
        }
        return json.dumps(back)


@admin.route('/post-blog', methods=['POST'])
@admin_required
def post_blog():
    data = json.loads(request.get_data().decode('utf-8'))
    print(session['current_article'])
    try:
        print(session['current_article'])
        artilce = Article.query.get(
            session['current_article'])  # 从seeion获取当前编辑文章ID
        artilce.title = data['title']
        artilce.body = data['body']
        article.article_type_id = data('type')
        article.last_change_time = datetime.datetime.utcnow()
        if artilce.finish is None:
            artilce.finish = datetime.datetime.utcnow()
        article.is_submit = True
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({
            'status': '400',
            'message': 'failed'
        })
    else:
        url = request.url_root+"admin"
        return jsonify({
            'status': '200',
            'message': 'success',
            'url': url
        })

# 初始化草稿


@admin.route('/write-blog', methods=['POST', 'GET'])
@admin_required
def write_blog():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf8'))
        article = Article.query.get(data['id'])
        if article is not None:
            db.session.delete(article)
        newarticle = Article(is_submit=False)
        session['current_article'] = newarticle.id  # 会话中session加入本篇文章ID
        print(">>>>>>>>>>>>>"+session['current_article'])
        db.session.add(newarticle)
        return jsonify({"status": "200", "message": "success"})

    types = ArticleType.query.all()
    draft = Article.query.filter_by(is_submit=False).first()
    pre_article = Article(is_submit=False)
    session['current_article'] = pre_article.id
    db.session.add(pre_article)
    print(session['current_article'])
    if draft is not None:
        draft_url = request.url_root+"admin/update-blog/"+str(draft.id)
        return render_template('admin/write_blog.html',
                               types=types, draft=draft.id, draft_url=draft_url)
    else:
        return render_template('admin/write_blog.html',
                               types=types)


@admin.route('/update-blog/<int:id>', methods=['POST', 'GET'])
@admin_required
def update_blog(id):
    article = Article.query.get_or_404(id)
    article.is_submit = False
    session['current_article'] = article.id
    print(session['current_article'])
    db.session.commit()
    types = ArticleType.query.all()

    return render_template('admin/update_blog.html',
                           types=types, article=article)


@admin.route('/', methods=['POST', 'GET'])
@admin_required
def admin():
    return render_template('admin/main.html')
    # global BLOG_IMAGE

    # form = ArticleForm()
    # form.article_type_id.choices = [(v.id, v.name)
    #                                 for v in ArticleType.query.all()]
    # if form.validate_on_submit():
    #     article = Article(
    #         body=form.body.data,
    #         title=form.title.data,
    #         blog_images=BLOG_IMAGE,
    #         # timestamp=datetime.utcnow(),
    #         article_type_id=int(form.article_type_id.data))
    #     db.session.add(article)
    #     return redirect(url_for('main.blogs'))
    # print(BLOG_IMAGE)
    # BLOG_IMAGE = ''
    # article_pagination = Article.query.paginate(
    #     1, per_page=10, error_out=False)
    # user_pagination = User.query.paginate(
    #     1, per_page=10, error_out=False)
    # article_pages = [x+1 for x in range(article_pagination.pages)]
    # user_pages = [x+1 for x in range(user_pagination.pages)]
    # return render_template('admin/admin.html', form=form,
    #                        article_pages=article_pages, user_pages=user_pages)
