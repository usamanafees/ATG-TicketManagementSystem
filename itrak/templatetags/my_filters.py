from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.core import signing
from django import template
from itrak.models import *
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Case, F, FloatField, IntegerField, Sum, When, Count
from django.db.models.functions import Cast
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import pytz, json

register = template.Library()

@register.filter(name='times')
def times(number):
    number=number-1
    return range(number)


@register.simple_tag
def to_dict_list(my_list, dict_key, dict_value):
    my_list = list(my_list)
    my_list = checDictListDuplication(my_list, dict_key)
    my_list.append({dict_key: dict_value})
    return my_list


@register.simple_tag
def pop_dict_list(my_list):
    # print('POP')
    # print(my_list)
    # print('POP')
    my_list = list(my_list)
    if len(my_list) > 0:
        my_list.pop()
    # print(my_list)
    # print('AFTER POP')
    return my_list


@register.simple_tag
def checDictListDuplication(my_list, dict_key):
    # print(my_list)
    my_list = list(my_list)
    for ele in my_list:
        for k, v in ele.items():
            if k == dict_key:
                # print('Duplicate')
                my_list = pop_dict_list(my_list)
    return my_list