#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flasky.py - 2021年 九月 17日
# 主脚本
import os

from flask_migrate import Migrate

from app import create_app, db
from app.models import User, Role, Permission, Post, Follow

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """
    注册一个 shell 上下文管理器，启动 flask shell 时可以自动导入数据库实例和模型
    """
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post, Follow=Follow)


@app.cli.command()
def test():
    """
    启动单元测试
    """
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
