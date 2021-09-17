#!/usr/bin/env python
# -*- coding: utf-8 -*-
# forms.py - 2021年 九月 17日
# 登录表单
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = StringField('Password', validators=[(DataRequired())])
    remember_me = BooleanField('Keep me login in')  # 复选框
    submit = SubmitField('Log in')
