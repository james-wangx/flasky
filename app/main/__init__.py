#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __init__.py - 2021年 九月 17日
# 主蓝本
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permission():
    """
    把 Permission 类加入模板上下文
    """
    return dict(Permission=Permission)
