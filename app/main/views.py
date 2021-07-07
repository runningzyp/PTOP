import datetime
import json
import os
import time

from flask import send_from_directory  # 文件下载
from flask import (current_app, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_login import (current_user, login_manager, login_required,
                         login_user, logout_user)

from . import main
from .. import auth, db
from ..models import Article, ArticleType, Data, User, AliConfig, Comment
from ..utils import ali_oss
from .forms import ArticleForm


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        userkey = request.form.get('ID')
        user = User.query.filter_by(userkey=userkey).first()
        if user is not None:
            login_user(user, True)  # true 记住用户
            return redirect(url_for('main.user', username=user.username))
        flash('请输入正确的令牌')
    return render_template('index.html')


@main.route('/blogs', methods=['POST', 'GET'])
def blogs():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf8'))
        article = Article.query.filter_by(article_status='submited',
                                          article_type_id=data['type']).order_by(
            Article.finish_time.desc()).paginate(data['page'],
                                                 5, error_out=False)
        try:
            data = [item.to_json() for item in article.items]
        except IndexError as e:
            return jsonify({'status': '400', 'data': str(e)})
        except Exception as e:
            return jsonify({'status': '400', 'data': str(e)})
        else:
            return jsonify({
                'status': '200',
                'data': data
            })

    articletypes = ArticleType.query.order_by(ArticleType.id.asc()).all()
    print(articletypes)
    counts = [articletype.articles.count() for articletype in articletypes]

    return render_template("blogs.html", counts=counts)


@main.route('/blog/<int:id>')
def blog(id):
    blog = Article.query.get_or_404(id)
    blog.visit_num += 1
    db.session.commit()
    comments = blog.comments.order_by(Comment.time.desc())
    return render_template('blog.html', blog=blog, comments=comments)


@main.route('/blog/add-comment', methods=["POST"])
def add_comment():
    if request.method == "POST":
        data = json.loads(request.get_data().decode('utf-8'))
        email = data['email']
        print(email)
        name = data['name']
        content = data['comment']
        article_id = data['article_id']
        try:
            print(">>>>>>"+email)
            new_comment = Comment(email=email, name=name,
                                  content=content, article_id=article_id)
            db.session.add(new_comment)
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "400",
                "message": e
            })
        else:
            db.session.commit()
            return jsonify({
                "status": "200",
                "message": "回复成功",
                "time": new_comment.time,
                'email': new_comment.email,
                "content": new_comment.content
            })


@main.route('/userlogout')
@login_required
def userlogout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    print(current_user.role.aliconfig)
    user = User.query.filter_by(username=username).first()
    if username != current_user.username:
        return render_template('404.html'), 404

    data = user.data.order_by(Data.timestamp.asc()).all()
    return render_template('user.html', data=data, user=user)


@main.route('/get-token', methods=['POST', 'GET'])
def get_token():
    user_dir = current_user.email
    aliconfig = current_user.role.aliconfig
    if request.method == 'POST':
        return ali_oss.get_token(aliconfig, user_dir)


@main.route('/call-back', methods=['POST', 'GET'])
def call_back():
    if request.method == 'POST':
        aliconfig = current_user.role.aliconfig
        aliconfig.host

        sec_filename = request.form.get('filename')
        print(sec_filename)
        filename = sec_filename.split('/')[-1]
        print(filename)
        email = sec_filename.split('/')[0]
        print(email)

        bucket = request.form.get('bucket')
        filetype = request.form.get('mimeType')  # 文件类型

        dt = datetime.datetime.utcnow()

        return json.dumps({'filename': filename, 'url': "baidu.com"})
    return 'success'


@main.route('/_sendmessage')
@login_required
def sendmessage():
    text = request.args.get('text', '')
    device_type = request.args.get('device_type', '')
    if text is not None:
        data = Data(text=text,
                    owner=current_user._get_current_object())
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
                        owner=current_user._get_current_object())
            db.session.add(data)
        except:
            file = None
        return jsonify({'name': filename, 'url': sec_filename})


@main.route('/register')
def turn():
    return redirect(url_for('auth.register'))


@main.route('/secret')
@login_required
def secret():
    return 'you can'


@main.route('/about-me')
def about():
    return render_template('about_me.html')


@main.route('/test')
def test():
    return render_template('test.html', a=[1, 2, 3, 4])
