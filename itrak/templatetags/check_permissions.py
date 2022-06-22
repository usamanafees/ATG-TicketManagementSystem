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

@register.filter(name='check_action_permission')
def check_action_permission(slug, user_id):
    check_slug_id = PermissionAction.objects.filter(perm_act_slug=slug).values_list('perm_act_id',flat=True)    
    if(check_slug_id.exists()):
        check_slug_id = check_slug_id[0]
        hasUserPermissions = UserActionPermission.objects.filter(user_id=user_id, perm_act_id=check_slug_id).exists()
        user_groups = UserGroupMembership.objects.filter(m_user_id= user_id,is_delete = 0)
        hasGroupPermissions = False
        for group in user_groups:
            groupPermissions = GroupActionPermission.objects.filter(group_id=group.m_group_id, perm_act_id=check_slug_id).exists()
            if groupPermissions:
                hasGroupPermissions = True
        if hasUserPermissions or hasGroupPermissions:
            print('True')
            return True
        else:
            print('False')
            return False
    print('Falsess')        
    return False
    
@register.filter(name='check_sub_action_permission')
def check_sub_action_permission(slug, user_id):
    check_slug_id = PermissionSubAction.objects.filter(perm_sub_act_slug=slug).values_list('sub_act_id',flat=True)    
    if(check_slug_id.exists()):
        check_slug_id = check_slug_id[0]
        hasUserPermissions = UserSubActionPermission.objects.filter(user_id=user_id, sub_act_id=check_slug_id).exists()
        user_groups = UserGroupMembership.objects.filter(m_user_id= user_id,is_delete = 0)
        hasGroupPermissions = False
        for group in user_groups:
            groupPermissions = GroupSubActionPermission.objects.filter(group_id=group.m_group_id, sub_act_id=check_slug_id).exists()
            if groupPermissions:
                hasGroupPermissions = True
        if hasUserPermissions or hasGroupPermissions:
            return True
        else:
            return False
    return False

@register.filter(name='check_email_notification_permission')
def check_email_notification_permission(client_id, action_id):
    check = ClientEmailNotificationPermission.objects.filter(client_id=client_id,t_action_id=action_id,email=1).exists()
    return check

@register.filter(name='check_mobile_notification_permission')
def check_mobile_notification_permission(client_id, action_id):
    check = ClientEmailNotificationPermission.objects.filter(client_id=client_id, t_action_id=action_id, mobile=1).exists()
    return check

@register.filter(name='check_Org_email_notification_permission')
def check_Org_email_notification_permission(org_id, action_id):
    check = OrganizationEmailNotificationPermission.objects.filter(org_id=org_id,t_action_id=action_id,email=1).exists()
    return check

@register.filter(name='check_Dep_email_notification_permission')
def check_Dep_email_notification_permission(dep_id, action_id):
    check = DepartmentEmailNotificationPermission.objects.filter(dep_id=dep_id,t_action_id=action_id,email=1).exists()
    return check
