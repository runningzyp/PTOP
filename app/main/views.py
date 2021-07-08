import json
import os
import io

from flask import (
    request,
    flash,
    jsonify,
    redirect,
    render_template,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.utils import secure_filename
from app.main import main
from app import db
from app.models import Article, ArticleType, Data, User, Comment
from app.utils.ali_oss import get_bucket


UPLOAD_FOLDER = "files"

ROOT_DIR = os.path.join("/", *os.path.abspath(__file__).split("/")[:-3])


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        userkey = request.form.get("ID")
        user = User.query.filter_by(userkey=userkey).first()
        if user is not None:
            login_user(user, True)  # true 记住用户
            return redirect(url_for("main.user", username=user.username))
        flash("请输入正确的令牌")
    return render_template("index.html")


@main.route("/blogs", methods=["POST", "GET"])
def blogs():
    if request.method == "POST":
        data = json.loads(request.get_data().decode("utf8"))
        article = (
            Article.query.filter_by(
                article_status="submited", article_type_id=data["type"]
            )
            .order_by(Article.finish_time.desc())
            .paginate(data["page"], 5, error_out=False)
        )
        try:
            data = [item.to_json() for item in article.items]
        except IndexError as e:
            return jsonify({"status": "400", "data": str(e)})
        except Exception as e:
            return jsonify({"status": "400", "data": str(e)})
        else:
            return jsonify({"status": "200", "data": data})

    articletypes = ArticleType.query.order_by(ArticleType.id.asc()).all()
    print(articletypes)
    counts = [articletype.articles.count() for articletype in articletypes]

    return render_template("blogs.html", counts=counts)


@main.route("/blog/<int:id>")
def blog(id):
    blog = Article.query.get_or_404(id)
    blog.visit_num += 1
    db.session.commit()
    comments = blog.comments.order_by(Comment.time.desc())
    return render_template("blog.html", blog=blog, comments=comments)


@main.route("/blog/add-comment", methods=["POST"])
def add_comment():
    if request.method == "POST":
        data = json.loads(request.get_data().decode("utf-8"))
        email = data["email"]
        print(email)
        name = data["name"]
        content = data["comment"]
        article_id = data["article_id"]
        try:
            print(">>>>>>" + email)
            new_comment = Comment(
                email=email, name=name, content=content, article_id=article_id
            )
            db.session.add(new_comment)
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "400", "message": e})
        else:
            db.session.commit()
            return jsonify(
                {
                    "status": "200",
                    "message": "回复成功",
                    "time": new_comment.time,
                    "email": new_comment.email,
                    "content": new_comment.content,
                }
            )


@main.route("/userlogout")
@login_required
def userlogout():
    logout_user()
    return redirect(url_for("main.index"))


@main.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user(username):
    print(current_user.role)
    user = User.query.filter_by(username=username).first()
    if username != current_user.username:
        return render_template("404.html"), 404

    data = user.data.order_by(Data.timestamp.asc()).all()
    return render_template("user.html", data=data, user=user)


@main.route("/_sendmessage")
@login_required
def sendmessage():
    text = request.args.get("text", "")
    if text is not None:
        data = Data(text=text, owner=current_user._get_current_object())
        db.session.add(data)
    return jsonify(result="success")


@main.route("/files", methods=["POST"])
@login_required
def sendfile():
    file = request.files["file"]
    user = User.query.filter_by(username=current_user.username).first()
    key = user.email + "/" + file.filename

    bio = io.BytesIO()
    file.save(bio)

    bucket = get_bucket()
    try:
        bucket.put_object(key, bio.getvalue())
    except Exception:
        url = None
    else:
        url = bucket.sign_url('GET', key, 3000)
    data = Data(
        filename=key,
        filetype=file.mimetype,
        owner=current_user._get_current_object(),
    )
    db.session.add(data)

    return jsonify({"name": file.filename, "url": url})


@main.route("/register")
def turn():
    return redirect(url_for("auth.register"))


@main.route("/secret")
@login_required
def secret():
    return "you can"


@main.route("/about-me")
def about():
    return render_template("about_me.html")


@main.route("/test")
def test():
    return render_template("test.html", a=[1, 2, 3, 4])
