#!/usr/bin/env python
# -*- coding: utf-8 -*-
# models.py - 2021年 九月 16日
# 模型
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600) -> str:
        """
        生成安全令牌

        :param expiration: 过期时间默认为1小时
        :return: 令牌字符串
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # DeprecationWarning: JWS support is deprecated and will be removed in ItsDangerous 2.1.
        # Use a dedicated JWS/JWT library such as authlib.
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token: str) -> bool:
        """
        检验安全令牌

        :param token: 令牌字符串
        :return: True 或 False
        """
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.id:
            return False
        # 验证成功，将默认值 False 改为 True
        self.confirmed = True
        db.session.add(self)

        return True

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """
    将函数注册给 Flask-Login，供需要获取已登录用户信息时调用
    """
    return User.query.get(int(user_id))
