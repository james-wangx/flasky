#!/usr/bin/env python
# -*- coding: utf-8 -*-
# views.py - 2021年 九月 17日
# 路由
from datetime import datetime

from flask import render_template

from . import main
from ..models import User


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)
