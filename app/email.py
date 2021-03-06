#!/usr/bin/env python
# -*- coding: utf-8 -*-
# email.py - 2021年 九月 16日
# 发邮件
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    """
    异步发送邮件
    """
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs) -> Thread:
    """
    发送电子邮件

    :param to: 收件人
    :param subject: 主题
    :param template: Jinja2模板
    :param kwargs: 关键字参数
    :return:
    """
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

    return thr
