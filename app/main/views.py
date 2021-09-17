#!/usr/bin/env python
# -*- coding: utf-8 -*-
# views.py - 2021年 九月 17日
# 路由
from datetime import datetime

from flask import render_template

from . import main


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())
