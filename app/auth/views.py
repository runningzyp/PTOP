import json
from random import Random

from flask import render_template, request, flash
from flask import redirect, url_for, jsonify


from . import auth
from app import db, cache
from app.utils import send_email

from app.models import User


def random_str(randomlength=6):
    str = ""
    chars = "0123456789"
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        while True:
            userkey = random_str(6)
            user = User.query.filter_by(userkey=userkey).first()
            if user is None:
                break
        email = request.form["email"]
        username = request.form["username"]
        code = request.form["code"]
        password = request.form["password"]
        password2 = request.form["password2"]

        ver_username = User.query.filter_by(username=username).first()
        if ver_username is not None:
            flash("该用户名已被使用")
            return redirect(url_for("auth.register"))
        if password != password2:
            flash("两次密码不同")
            return redirect(url_for("auth.register"))

        ver_code = cache.get(email)
        if 1:
            new_user = User(
                email=email,
                username=username,
                userkey=userkey,
                password=password,
            )
            db.session.add(new_user)
            db.session.commit()
        else:
            flash("验证码不正确")
            return redirect(url_for("auth.register"))
        send_email.delay(
            email, "您的用户令牌", "auth/email/userkey", userkey=new_user.userkey
        )
        return render_template("auth/success.html", userkey=userkey)
    return render_template("auth/register.html")


@auth.route("/get-code", methods=["POST"])
def get_code():
    if request.method == "POST":
        data = json.loads(request.get_data().decode("utf8"))
        email = data["email"]
        user = User.query.filter_by(email=email).first()
        if user is not None:
            return jsonify({"status": 400, "message": "邮箱已经被使用"})
        ret = cache.get(email)
        if ret:
            send_email.delay(
                email,
                "请再次检查您的验证码",
                "auth/email/confirm",
                code=ret,
                email=email,
            )
            return jsonify({"status": 200, "message": "发送成功,在您的邮箱查看验证码"})

        else:
            try:
                code = random_str()
                send_email.delay(
                    email,
                    "请检查您的验证码",
                    "auth/email/confirm",
                    code=code,
                    email=email,
                )
                ret = cache.set(email, code)
            except Exception as e:
                print(e)
                return jsonify({"status": 400, "message": "检查邮箱格式"})
            else:
                return jsonify({"status": 200, "message": "发送成功,在您的邮箱查看验证码"})
