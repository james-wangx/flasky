#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __init__.py - 2021年 九月 17日
# 主蓝本
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
