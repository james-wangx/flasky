#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __init__.py - 2021年 九月 17日
# 身份验证蓝本
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
