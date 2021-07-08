from datetime import datetime

from flask import current_app, render_template
from flask_mail import Message, current_app
from .. import mail, celery
from .. import db


@celery.task
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["FLASKY_MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    print("邮件开始发送....")
    mail.send(msg)
    print("邮件发送结束！")


@celery.task(name="clear_verify_code")
def clear_verify_code():
    print("here")
    from ..models import VerificationCode

    codes = VerificationCode.query.filter(
        datetime.utcnow() > VerificationCode.expire_time
    )
    if codes is not None:
        codes.delete()
        db.session.commit()
