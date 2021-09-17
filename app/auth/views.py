#!/usr/bin/env python
# -*- coding: utf-8 -*-
# views.py - 2021年 九月 17日
# 身份验证的路由的视图函数
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user

from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    """
    form = LoginForm()

    # POST 请求进入验证逻辑
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # 验证成功，正式登录
            login_user(user, form.remember_me.data)
            # 如果用户尝试访问未授权的 URL，Flask-Login 会把此 URL 存在 next 中
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        # 验证失败，闪现错误提示
        flash('Invalid username or password.')

    # GET 请求直接返回登录页面
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')

    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)
