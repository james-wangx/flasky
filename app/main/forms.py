#!/usr/bin/env python
# -*- coding: utf-8 -*-
# forms.py - 2021年 九月 17日
# 表单
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
