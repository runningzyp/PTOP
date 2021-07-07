import json
import datetime
import uuid

from flask import render_template, request, flash
from flask import redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from flask import jsonify

from . import admin
from .forms import LoginForm, ArticleForm
from .. import db
from ..models import User, Article, ArticleType, AliConfig, ArticleImage, Comment
from random import Random
from ..decorators import admin_required

from ..utils import ali_oss


@admin.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            remember_me = request.form['switch']
            ret = True
        except Exception as e:
            ret = False

        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            login_user(user, ret)
            return redirect(request.args.get('next') or url_for('admin.admin'))
        flash('禁止登录')
    return render_template('admin/admin_login.html')


@admin.route('/admin-logout')
@admin_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.admin'))


@admin.route('/get-token', methods=['POST'])
@admin_required
def get_token():
    user_dir = 'blogimages'
    aliconfig = current_user.role.aliconfig
    if request.method == 'POST':
        return ali_oss.get_token(aliconfig, user_dir)


# 获取文章列表
@admin.route('/blogs', methods=['GET', 'POST'])
@admin_required
def blogs():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        page = data['page']
        limit = data['limit']
        pagination = Article.query.filter_by(
            article_status='submited').order_by(
            Article.finish_time.desc()).paginate(
            page, per_page=limit, error_out=False)

        articles = pagination.items
        return jsonify({'status': 200,
                        'message': 'success',
                        'count': pagination.total,
                        'data': [article.admin_to_json()
                                 for article in articles],
                        })
    return render_template('admin/blog_mg/blogs.html')


# 获取回收站列表
@admin.route('/recycle-bin', methods=['GET', 'POST'])
@admin_required
def recycle_bin():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        page = data['page']
        limit = data['limit']
        pagination = Article.query.filter_by(
            article_status='recycling').order_by(
            Article.finish_time.desc()).paginate(
            page, per_page=limit, error_out=False)

        articles = pagination.items
        return jsonify({'status': 200,
                        'message': 'success',
                        'count': pagination.total,
                        'data': [article.admin_to_json()
                                 for article in articles],
                        })
    return render_template('admin/blog_mg/recycle_bin.html')

# 草稿箱


@admin.route('/draft', methods=['GET', 'POST'])
@admin_required
def draft():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        page = data['page']
        limit = data['limit']
        pagination = Article.query.filter_by(
            article_status='draft').order_by(
            Article.finish_time.desc()).paginate(
            page, per_page=limit, error_out=False)

        articles = pagination.items
        return jsonify({'status': 200,
                        'message': 'success',
                        'count': pagination.total,
                        'data': [article.admin_to_json()
                                 for article in articles],
                        })
    return render_template('admin/blog_mg/draft.html')

# 博客处理


@admin.route('/manage-blogs', methods=['GET', 'POST'])
@admin_required
def delete_blog():
    aliconfig = current_user.role.aliconfig
    bucket = ali_oss.get_bucket(aliconfig)

    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        # 放入回收站
        if data['operation'] == 'recycle':
            print(data['objects'])
            for id in data['objects']:
                article = Article.query.get(id)
                if article is not None:
                    article.article_status = 'recycling'
            db.session.commit()
            return jsonify({
                'status': 200,
                'message': '放入回收站成功'
            })
        elif data['operation'] == 'delete':
            print(data['objects'])
            for id in data['objects']:
                article = Article.query.get(id)
                if article is not None:
                    images = article.images
                    imagesList = [image.full_path for image in images]
                    try:
                        bucket.batch_delete_objects(imagesList)
                    except Exception as e:
                        print(e)
                    db.session.delete(article)
            db.session.commit()
            return jsonify({
                'status': 200,
                'message': '删除成功'
            })
        elif data['operation'] == 'recovery':
            print(data['objects'])
            for id in data['objects']:
                article = Article.query.get(id)
                if article is not None:
                    article.article_status = 'submited'
            db.session.commit()
            return jsonify({
                'status': 200,
                'message': '恢复成功'
            })


# 上传图片

@admin.route('/upload-blog-image', methods=['POST', 'GET'])
@login_required
@admin_required
def upload_blog_img():
    if request.method == "POST":
        aliconfig = current_user.role.aliconfig

        prefix_url = 'http://'+aliconfig.bucket + \
            '.'+aliconfig.host.split('//')[-1]+'/'
        print(prefix_url)

        bucket = ali_oss.get_bucket(aliconfig)  # 从工具模块获取 bucket访问授权

        dt = datetime.datetime.utcnow()
        sec_key = dt.strftime("%Y-%m-%d-%H-%M-%S")

        # requests.get返回的是一个可迭代对象（Iterable）
        # 此时Python SDK会通过Chunked Encoding方式上传。

        img = request.files['image']

        origin_name = img.filename

        img.filename = str(uuid.uuid1()) + '.' + img.filename.split('.')[-1]
        upload_folder = 'blogimages' + '/' + \
                        datetime.datetime.now().strftime('%m-%d-%Y') + '/'  # 日期表示文件夹
        full_path = upload_folder + img.filename  # 完整路径
        try:
            bucket.put_object(upload_folder + img.filename, img)
        except Exception as e:
            print(e)
        else:
            imagemeta = bucket.get_object_meta(full_path)
            size = imagemeta.headers['Content-Length']
            image = ArticleImage(origin_name=origin_name, full_path=full_path,
                                 size=size, image_url=prefix_url + full_path)
            db.session.add(image)
            return jsonify({"status": "200",
                            "url": prefix_url + full_path
                            })
        return jsonify({
            "status": "400",
            "message": "could not upload this image"

        })


# 编写文章


@admin.route('/write-blog', methods=['POST', 'GET'])
@admin_required
def write_blog():

    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf8'))
        title = data['title']
        body_origin = data['body_origin']
        article_type_id = data['type']
        if data['status'] == "submited":
            article = Article(title=title, body_origin=body_origin,
                              article_type_id=article_type_id)
        if data['status'] == "draft":
            article = Article(title=title, body_origin=body_origin,
                              article_type_id=article_type_id, article_status="draft")

        db.session.add(article)
        db.session.commit()

        images = ArticleImage.query.filter_by(article_id=None).all()
        if images:
            for image in images:
                image.article_id = article.id
            db.session.commit()
        return jsonify({
            'status': '200',
            'id': article.id
        })

    aliconfig = current_user.role.aliconfig
    bucket = ali_oss.get_bucket(aliconfig)
    images = ArticleImage.query.filter_by(article_id=None)

    for image in images:
        print(image.full_path)
    imagesList = [image.full_path for image in images]
    if imagesList:
        try:
            print('Here')
            bucket.batch_delete_objects(imagesList)
        except Exception as e:
            print(e)
        images.delete()
    form = ArticleForm()
    types = ArticleType.query.all()
    return render_template('admin/blog_mg/write_blog.html', form=form, types=types)


# 更新文章


@admin.route('/update-blog/<int:id>', methods=['POST', 'GET'])
@admin_required
def update_blog(id):
    '''
    更新博客文章
    '''
    article = Article.query.get_or_404(id)
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf8'))
        print(">>>>>>>>>>>>>>>>>>>>>>>>.")
        print(data['type'])
        article.title = data['title']
        article.article_type_id = data['type']
        article.body_origin = data['body_origin']
        if article.article_status == "draft":
            article.finish_time = datetime.datetime.utcnow()
        article.article_status = 'submited'
        article.last_change_time = datetime.datetime.utcnow()
        db.session.commit()
        print(article.article_type_id)
        images = ArticleImage.query.filter_by(article_id=None).all()
        if images:
            for image in images:
                image.article_id = article.id
            db.session.commit()
        return jsonify({
            'status': '200',
            'id': article.id
        })

    form = ArticleForm()
    types = ArticleType.query.all()
    return render_template('admin/blog_mg/update_blog.html', form=form,
                           types=types, article=article,)


###############################################################################

# 用户

###############################################################################


@admin.route('/get-users', methods=['POST', 'GET'])
@admin_required
def users():
    if request.method == 'POST':
        data = json.loads(request.get_data().decode('utf-8'))
        page = data['page']
        pagination = User.query.order_by(
            User.join_time.desc()).paginate(
            page, per_page=data['limit'], error_out=False)
        users = pagination.items
        return jsonify({'status': 200,
                        'message': 'success',
                        'count': pagination.total,
                        'data': [user.to_json()
                                 for user in users],
                        })
    return render_template('admin/user_mg/users.html')


###############################################################################

# 评论

###############################################################################


@admin.route('/comments', methods=['POST', 'GET'])
@admin_required
def comments():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        page = data['page']
        limit = data['limit']
        pagination = Comment.query.order_by(
            Comment.time.desc()).paginate(
            page, per_page=limit, error_out=False)

        comments = pagination.items
        return jsonify({'status': 200,
                        'message': 'success',
                        'count': pagination.total,
                        'data': [comment.to_json()
                                 for comment in comments],
                        })
    return render_template('admin/comments_mg/comments.html')


@admin.route('/delete-comments', methods=['GET', 'POST'])
@admin_required
def delete_comment():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        # 删除评论
        for id in data['objects']:
            comment = Comment.query.get(id)
            if comment is not None:
                try:
                    db.session.delete(comment)
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    return jsonify({
                        'status': 400,
                        'message': '删除失败'
                    })
                else:
                    db.session.commit()
            return jsonify({
                'status': 200,
                'message': '删除成功'
            })


@admin.route('/reply-comments', methods=['GET', 'POST'])
@admin_required
def reply_comment():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        # 删除评论
        id = data['id']
        reply_content = data['reply_content']
        comment = Comment.query.get(id)
        if comment is not None:
            try:
                comment.reply = reply_content
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'status': 400,
                    'message': '回复失败'
                })
            else:
                db.session.commit()
        return jsonify({
            'status': 200,
            'message': '回复成功'
        })


###############################################################################

# 其他

###############################################################################


@admin.route('/ali-settings', methods=['GET', 'POST'])
@admin_required
def ali_settings():
    if request.method == 'POST':
        id = request.form['id']
        config = AliConfig.query.get(id)
        if config is not None:
            config.access_key_id = request.form['access_key_id']
            config.access_key_secret = request.form['access_key_secret']
            config.host = request.form['host']
            config.bucket = request.form['bucket']
            config.expire_time = request.form['expire_time']
            config.url_prefix = request.form['url_prefix']
            db.session.commit()

    configs = AliConfig.query.all()
    return render_template('admin/other/ali_settings.html', configs=configs)


@admin.route('/test', methods=['GET', 'POST'])
def test():
    return render_template("admin/test.html")


@admin.route('/', methods=['POST', 'GET'])
@admin_required
def admin():
    blog_count = Article.query.count()
    user_count = User.query.count()
    return render_template('admin/main.html', blog_count=blog_count,
                           user_count=user_count)
