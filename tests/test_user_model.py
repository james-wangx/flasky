#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test_user_model.py - 2021年 九月 17日
# 测试用户模型
import unittest

from app.models import User


class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self) -> None:
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self) -> None:
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self) -> None:
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self) -> None:
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)
