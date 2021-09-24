#!/usr/bin/env python
# -*- coding: utf-8 -*-
# fake.py - 2021年 九月 24日
# 生成虚拟数据
from random import randint

from faker import Faker
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, Post


def users(count=100):
    """
    生成虚拟用户

    :param count: 用户数量
    :return:
    """
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        # 防止 email 和 username 重复
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    """
    生成虚拟文章

    :param count: 文章数
    :return:
    """
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
