from django.utils.deprecation import MiddlewareMixin
try: # Django 2.0
    from django.urls import reverse, resolve, Resolver404
except: # Django < 2.0
    from django.core.urlresolvers import reverse, resolve, Resolver404
from itrak.models import *
from itrak.views.Load import *
from django.contrib import messages

class UserPageRequest(MiddlewareMixin):
    def process_request(self, request):
        if not request.is_ajax() and not request.method == 'POST' and request.user.is_authenticated:
            match = resolve(request.path)
            url = match.url_name
            is_permit = None
            user = request.user

            if url != None:
                if not "mySettings" in url:
                    settings = MySettings.objects.filter(m_user_id=user.id).exists()
                    mysett = MySettings.objects.filter(m_user_id=user.id).latest('m_setting_id')
                    if settings == False:
                        messages.error(request, 'SYSTEM SETTINGS MISSING!!! Please provide below details First.')
                        return redirect('mySettings')
                    if settings == True and mysett.m_time_zone == 'NULL':   
                        messages.error(request, 'SYSTEM SETTINGS MISSING!!! Please provide below details First.')
                        return redirect('mySettings')

            permit_menus = Menus.objects.values_list('menu_link', flat=True).filter(menu_is_active=1).filter(menu_is_delete=0).filter(menu_permit_active=1).exclude(menu_link=0)
            permit_submenus = SubMenus.objects.values_list('submenu_link', flat=True).filter(submenu_is_active=1).filter(submenu_is_delete=0).filter(submenu_permit_active=1)
            is_permit_urls = list(chain(permit_menus, permit_submenus))
            if url in is_permit_urls:
                if SubMenus.objects.filter(submenu_link = url).exists():
                    SubMenu_List = list(get_sidebar_submenus_access(request, user.id))
                    id = SubMenus.objects.values_list('submenu_id', flat=True).get(submenu_link=url)
                    if id in SubMenu_List:
                        is_permit = True
                    else:
                        return redirect('mySettings')
                elif Menus.objects.filter(menu_link = url).exists():
                    Menu_List = list(get_sidebar_menus_access(request, user.id))
                    id = Menus.objects.values_list('menu_id', flat=True).get(menu_link=url)
                    if id in Menu_List:
                        is_permit = True
                    else:
                        return redirect('mySettings')
                if is_permit is None:
                    return redirect('signout')
