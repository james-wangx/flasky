#!/usr/bin/env python
# -*- coding: utf-8 -*-
# decorators.py - 2021年 九月 19日
# 检查用户权限的自定义装饰器
from functools import wraps

from flask_login import current_user
from werkzeug.exceptions import abort

from app.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
