from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from itrak.models import Organization, Client, User, Menus
from django.template.loader import render_to_string, get_template
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from itrak.views.Load import *
from itrak.views.Email import *
from django.core import serializers
import json
from pprint import pprint
from django.urls import reverse
from datetime import datetime
import pytz
from django.contrib import messages



# Create your views here.


#Home/Empty Request#
user_login_required = user_passes_test(lambda user: user.is_active, login_url='/') #Here user_passes_test decorator designates the user is active.

# def active_user_required(view_func):
#     decorated_view_func = login_required(user_login_required(view_func))
#     return decorated_view_func
from functools import wraps
def active_user_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        else:
            if request.user.user_org.org_is_delete==False:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('signout')
    decorated_view_func = login_required(user_login_required(view_func))
    return wraps(decorated_view_func)(wrapped)

# def permission_required(arg_name, layer):
#     def decorator(view):
#         def wrapper(request, *args, **kwargs):
#             action_id = kwargs.get(arg_name)
#             user = request.user
#             print(user.id)
#             print(action_id)
#             if layer == 'menu':
#                 id = Menus.objects.values_list('menu_id', flat=True).get(menu_link=arg_name)
#                 is_permit = UserMenuPermissions.objects.filter(user_id=user.id).filter(menu_id=id).exists()
#             else:
#                 id = SubMenus.objects.values_list('submenu_id', flat=True).get(submenu_link=arg_name)
#                 is_permit = UserMenuPermissions.objects.filter(user_id=user.id).filter(submenu_id=id).exists()
#             if is_permit:
#                 return view(request, *args, **kwargs)
#             else:
#                 return redirect('signout') # 403 Forbidden is better than 404
#         return wrapper
#     return decorator

def permission_required(arg_name, layer):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            action_id = kwargs.get(arg_name)
            user = request.user
            if layer == 'menu':
                Menu_List = get_sidebar_menus_access(request, user.id)
                id = Menus.objects.values_list('menu_id', flat=True).get(menu_link=arg_name)
                is_permit = None
                for Menu in Menu_List:
                    if id == Menu:
                        is_permit = True
            else:
                SubMenu_List = get_sidebar_submenus_access(request, user.id)
                id = SubMenus.objects.values_list('submenu_id', flat=True).get(submenu_link=arg_name)
                is_permit = None
                for subMenu in SubMenu_List:
                    if id == subMenu:
                        is_permit = True
            if is_permit:
                return view(request, *args, **kwargs)
            else:
                return redirect('signout') # 403 Forbidden is better than 404
        return wrapper
    return decorator

@active_user_required
@permission_required('home', 'submenu')
def home(request):
    # sections = get_sections(request)
    # menus = get_menus(request)
    # sub_menus = get_sub_menus(request)
    load_sidebar = get_sidebar(request)
    # message = []
    # message.append("" + str(load_sidebar) + "")
    
    panel_left = DashboardSettings.objects.values('d_panel__panelGraph_text','d_panel__panelGraph_url','d_column_side','d_setting_id','d_expanded','d_data_display').filter(d_user_id=request.user.id).filter(d_column_side=0)
    panel_right = DashboardSettings.objects.values('d_panel__panelGraph_text','d_panel__panelGraph_url','d_column_side','d_setting_id','d_expanded','d_data_display').filter(d_user_id=request.user.id).filter(d_column_side=1)
    timezone_count = MySettings.objects.filter(m_user_id=request.user.id).count()
    timezone = MySettings.objects.filter(m_user_id=request.user.id).first()
    if timezone.m_time_zone != 'NULL' and timezone_count > 0:
        eastern = pytz.timezone(timezone.m_time_zone)
        time = datetime.now(eastern)
        time = time.strftime('%m/%d/%Y %I:%M:%S %p')
        reload_time = timezone.m_dashboard_reload
        show_reload = timezone.m_show_reload
    else:
        time = ''
        reload_time = ''
        show_reload = ''

    context = {
        # 'sections': sections,
        # 'menus': menus,
        # 'submenus': sub_menus,
        'sidebar': load_sidebar,
        'panel_left': panel_left,
        'panel_right': panel_right,
        'time': time,
        'timezone_count': timezone_count,
        'reload_time': reload_time,
        'show_reload': show_reload,
        # 'load_sidebar': message
    }
    return render(request, 'itrak/dashboard.html', context)

#Home/Empty Request Ends Here#


# def get_sidebar(request):
#     menus = Menus.objects.filter(menu_is_active=True).filter(menu_id=2)
#     return {'menus': menus}
