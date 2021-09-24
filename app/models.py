#!/usr/bin/env python
# -*- coding: utf-8 -*-
# models.py - 2021年 九月 16日
# 模型
import hashlib
from datetime import datetime

import bleach
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Permission:
    FOLLOW = 1
    COMMIT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        """
        在数据库中创建角色
        :return:
        """
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMIT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMIT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMIT, Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

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
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    name = db.Column(db.String(64))  # 真实姓名
    location = db.Column(db.String(64))  # 所在地
    about_me = db.Column(db.Text())  # 自我介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 注册日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 最后访问日期

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 根据电子邮件将用户角色设为管理员或默认角色
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
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

    def generate_reset_token(self, expiration=3600) -> str:
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token: str, new_password: str) -> bool:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)

        return True

    def generate_email_change_token(self, new_email: str, expiration=3600) -> str:
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token: str) -> bool:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)

        return True

    def ping(self):
        """
        刷新用户的最后访问时间
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """
        使用 Gravatar 服务获取用户头像

        :param size: 图像尺寸
        :param default:默认头像生成方式，identicon 为几何图形
        :param rating: 图像级别
        :return: 头像 url
        """
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return f'{url}/{hash}?s={size}&d={default}&r={rating}'

    def __repr__(self):
        return f'<User {self.username}>'


class AnonymousUser(AnonymousUserMixin):
    """
    自定义匿名用户类
    """

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser  # 指定匿名用户类


@login_manager.user_loader
def load_user(user_id):
    """
    将函数注册给 Flask-Login，供需要获取已登录用户信息时调用
    """
    return User.query.get(int(user_id))


class Post(db.Model):
    """
    博客文章
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """
        自动将 MarkDown 转为 HTML
        """
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True
        ))


db.event.listen(Post.body, 'set', Post.on_changed_body)
