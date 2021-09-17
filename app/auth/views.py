#!/usr/bin/env python
# -*- coding: utf-8 -*-
# views.py - 2021年 九月 17日
# 身份验证的路由的视图函数
from flask import render_template

from . import auth


@auth.route('/login')
def login():
    return render_template('auth/login.html')
