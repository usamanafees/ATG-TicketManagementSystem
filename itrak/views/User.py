from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response,reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest, request
from itrak.models import Organization, Client, Group, Department, User, UserManger, UserMenuPermissions, UserGroupMembership
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils import timezone
import pytz
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.crypto import get_random_string
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from django.conf.urls import url
from django.template.loader import render_to_string, get_template
from itrak.views.Load import *
from itrak.views.Email import *
from django.db.models.query import QuerySet,RawQuerySet
from django.core import signing
from django.core.files.storage import FileSystemStorage
from django.db.models import CharField, Value
from django.db import connection



# Create your views here.

#Custom Decorator Start#

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
#Custom Decorator End#


# Client Add Request Start#

@active_user_required
def addUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
        # raise PermissionDenied("You are not allowed")
    user_id = request.user.id
    org_id = request.user.user_org_id
    global_user = isGlobalUser(request)
    # if request.user.user_type_slug != global_user:
    organizations = request.user.user_org_id
    departments = Department.objects.filter(d_is_delete=0).filter(user_org_id=org_id)
    # else:
    already_users = list(User.objects.filter(user_type=0,admin=1,is_superuser=0,is_staff=1,is_active=1,login_permit=1,is_delete=0).values_list('user_org_id', flat=True))
    print(already_users)
    organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
    print(organizations)
    # departments = Department.objects.filter(d_is_delete=0)
    clients = Client.objects.filter(cl_is_delete=0)
    permissions = PermissionSection.objects.filter(is_active = 1)
    disabled_actions=[1,2,3,4,5,6,7,11,40]
    disabled_sub_action=[1,2]
    load_sidebar = get_sidebar(request)
    context = {
        'organizations': organizations,
        'departments': departments,
        'clients': clients,
        'permissions': permissions,
        'sidebar': load_sidebar,
        'timezones': pytz.common_timezones,
        'disabled_actions': disabled_actions,
        'disabled_sub_action': disabled_sub_action,
        'user_id':user_id,
    }

    return render(request, 'itrak/User/user_add.html', context)

# Client Add Request End#


# User Save Request Start#

@active_user_required
def saveUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.user.user_org_id
        if 'user_type' in request.POST and request.POST['user_type']:
            user_type = request.POST.get('user_type')
        if 'user_cus_id' in request.POST:
            user_cus_id = request.POST.get('user_cus_id')
        if 'first_name' in request.POST and request.POST['first_name']:
            first_name = request.POST.get('first_name')
        if 'last_name' in request.POST and request.POST['last_name']:
            last_name = request.POST.get('last_name')
        if 'display_name' in request.POST:
            display_name = request.POST.get('display_name')
        if 'login_permit' in request.POST:
            login_permit = 'True'
        else:
            login_permit = 'False'
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
        if 'email' in request.POST:
            email = request.POST.get('email')
        if 'email' in request.POST:
            username = request.POST.get('email')
        if 'mob_sms_email' in request.POST:
            mob_sms_email = request.POST.get('mob_sms_email')
        if 'suppress_all_emails' in request.POST:
            suppress_all_emails = 'True'
        else:
            suppress_all_emails = 'False'
        if 'time_zone' in request.POST and request.POST['time_zone']:
            time_zone = request.POST.get('time_zone')
        else: 
            time_zone = 'NULL'
        # if 'org_id' in request.POST and request.POST['org_id']:
        #     org_id = request.POST.get('org_id')
        if 'dep_id' in request.POST:
            dep_id = request.POST.get('dep_id')
        # if 'client_id' in request.POST:
        #     client_id = request.POST.get('client_id')
        if 'address1' in request.POST:
            address1 = request.POST.get('address1')
        if 'address2' in request.POST:
            address2 = request.POST.get('address2')
        if 'city' in request.POST:
            city = request.POST.get('city')
        if 'state' in request.POST:
            state = request.POST.get('state')
        if 'zip' in request.POST:
            zip = request.POST.get('zip')
        if 'country' in request.POST:
            country = request.POST.get('country')
        if 'sub' in request.POST:
            submenus = request.POST.get('sub')
        if 'menu' in request.POST:
            menus = request.POST.get('menus')
        if 'default_home_page' in request.POST:
            default_home_page = request.POST.get('default_home_page')
        if 'redirect_to' in request.POST:
            redirect_to = request.POST.get('redirect_to')
         

        obj = User(user_type=user_type, username=username, first_name=first_name, last_name=last_name, display_name=display_name, login_permit=login_permit, phone_no=phone, email=email, mob_sms_email=mob_sms_email, suppress_email=suppress_all_emails, user_dep_id=dep_id, user_org_id=org_id, address1=address1, address2=address2, user_city=city, user_state=state, user_zip_code=zip, user_country=country, user_time_zone=time_zone)
        obj.default_password = randomString = get_random_string(length=8)
        obj.set_password(randomString)
        obj.save()


        # User Account Membership Start#
        cursor = connection.cursor()
        if 'account_ids' in request.POST:
            accountIDs = request.POST.getlist('account_ids')
            if accountIDs:
                for accountID in accountIDs:
                    query="insert into AT_UserAccountRelation(user_id, account_id) values(%s,%s)"
                    data_tuple=(obj.id,accountID)
                    cursor.execute(query,data_tuple)
        # User Account Membership End# 

        # User Group Membership Start#
        if 'group_membership' in request.POST:
            UserGroupMembership.objects.filter(m_user_id=obj.id).delete()
            group_membership = request.POST.getlist('group_membership')
            if group_membership:
                if 'multiselect-all' in group_membership:
                    group_membership.remove('multiselect-all')
            for group_id in group_membership:
                membership_obj = UserGroupMembership(m_user_id=obj.id, m_group_id=group_id, m_org_id=org_id)
                membership_obj.save()
        # User Group Membership End#   

        m = MySettings(m_user_id=obj.id, m_time_zone=time_zone, m_default_page=default_home_page, m_ticket_screen=0,m_redirect_to=redirect_to,
                       m_dashboard_reload=0, m_show_reload='False', m_phone=None, m_email=None,m_mob_sms_email=None, m_address1=None,
                       m_address2=None, m_user_city=None,m_user_state=None, m_user_zip_code=None, m_user_country=None, m_org_id=org_id)
        m.save()

        #EMAIL SENT on USER ADD Start#

        subject = 'Login Credentials'
        to = []
        to.append(obj.email)
        support_url = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/'
        obj1 = UserSentEmails(
                use_subject = subject,
                use_sent_to_id = obj.id,
                use_created_by_id = obj.id,
                use_org_id = org_id
            )
        obj1.save()
        insert_id = signing.dumps(UserSentEmails.objects.latest('pk').use_id, salt=settings.SALT_KEY)
        dynamic = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/resetPassword?userID=' + obj.username + '&password=' + randomString + '&msgID=' + str(insert_id) + ''

        params = {'company_name': 'ATG Extra', 'firstname': obj.first_name, 'lastname': obj.last_name,
                  'default_password': randomString, 'action_url': dynamic,
                  'support_url': support_url}  # Paramters for change in Template Context

        message = render_to_string('itrak/Email/Email-Template/signup_mail.html', params)

        send_email(to=to, subject=subject, message=message)
        # EMAIL SENT on USER ADD End#

        #Add User Menu Permision in DB Start#
        print(org_id)
        menu_ids = request.POST.getlist('menus')
        submenu_ids = request.POST.getlist('submenus')

        for id in submenu_ids:
            permit_obj = UserMenuPermissions(user_id= obj.id, submenu_id = id)
            permit_obj.save()

        for id in menu_ids:
            permit_obj = UserMenuPermissions(user_id= obj.id, menu_id = id)
            permit_obj.save()
        #Add User Menu Permision in DB End#

        #Adding Permission Actions to UserActionPermission table        
        permission_actions = request.POST.getlist('permission_action')
        permission_sub_actions = request.POST.getlist(' ')
        user = User.objects.get(pk=obj.id)
       
        for permission_action in permission_actions:
            # return HttpResponse(permission_action)
            permission_action_obj = PermissionAction.objects.get(perm_act_id=permission_action)
            user_act_obj = UserActionPermission(user_id=user.id, perm_act_id=permission_action_obj.perm_act_id, user_org_id=org_id)
            user_act_obj.save() 
        for permission_sub_action in permission_sub_actions:
            per_sub_action_obj = PermissionSubAction.objects.get(sub_act_id=permission_sub_action)
            user_act_obj = UserSubActionPermission(user_id=user.id, sub_act_id=per_sub_action_obj.sub_act_id)
            user_act_obj.save()
        #END Adding Permission Actions to UserActionPermission table 

        messages.success(request, 'Request Succeed! User added.')
        return redirect('addUser')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! User cannot be added.Please try again.')
        return redirect('addUser')
# User Save Request Start#


# User List Request Start#

@active_user_required
def listUsers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/User/user_list.html', context)

# User List Request End#


# User Edit Request Start#

@active_user_required
def editUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('UserID')
    user_type = userType(request)
    ut = 0
    if user_type == 'superadmin':
        ut = 1
    try:
        # if request.user.user_type_slug != 'global_user':
        user_id = signing.loads(id,salt=settings.SALT_KEY)
        data = User.objects.get(pk=user_id)
        data.allowed_groups = list(data.userMembership.filter(is_delete=0).values_list('m_group_id', flat=True))
        data.group_list = list(get_group_list(request, data.user_type))
        data.organizations = Organization.objects.filter(org_id = data.user_org_id).filter(org_is_active=1).filter(org_is_delete=0)
        data.departments = Department.objects.filter(user_org_id = data.user_org_id).filter(d_is_delete=0)
        data.clients= Client.objects.filter(cl_is_delete=0)
        settings1 = MySettings.objects.filter(m_user_id=user_id).first()
        time_zone = User.objects.values_list('user_time_zone').get(pk=user_id)
        permissions = PermissionSection.objects.filter(is_active=1).all()  
        # else:
        #     user_id = signing.loads(id,salt=settings.SALT_KEY)
        #     data = User.objects.get(pk=user_id)
        #     data.allowed_groups = list(data.userMembership.filter(is_delete=0).values_list('m_group_id', flat=True))
        #     data.group_list = list(get_group_list(request, data.user_type))
        #     data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
        #     print(data.organizations)
        #     data.departments = Department.objects.filter(d_is_delete=0)
        #     data.clients= Client.objects.filter(cl_is_delete=0)
        #     settings1 = MySettings.objects.filter(m_user_id=user_id).first()
        #     time_zone = User.objects.values_list('user_time_zone').get(pk=user_id)
        #     permissions = PermissionSection.objects.filter(is_active=1).all()  
        

    except User.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listUser')
    else:
        load_sidebar = get_sidebar(request)
        menus_allowed = list(get_user_menus_permit(request, user_id))
        submenus_allowed = list(get_user_submenus_permit(request, user_id))                      
        actions_list = user_action_permissions(request, data)
        sub_actions_list = user_sub_action_permissions(request, data)
        disabled_actions= permissions_not_allowed(request, data)
        disabled_sub_action= sub_permissions_not_allowed(request, data)
        
        context = {
            'sidebar': load_sidebar,
            'timezones': pytz.common_timezones,
            'menus_allowed': menus_allowed,
            'submenus_allowed': submenus_allowed,
            'settings1': settings1,
            'data': data,
            'permissions': permissions,
            'actions_list': actions_list,
            'sub_actions_list': sub_actions_list,
            'disabled_actions': disabled_actions,            
            'disabled_sub_action': disabled_sub_action,
            'time_zone':json.dumps(time_zone),
            'default_page':json.dumps('home') if settings1 is None else json.dumps(settings1.m_default_page) ,
            'redirect_to':json.dumps('home') if settings1 is None else json.dumps(settings1.m_redirect_to),
            'user_id':user_id,
            'what_type':ut    
        }
        return render(request, 'itrak/User/user_edit.html', context)

# User Edit Request End#


# Send Email Request End#

def send_email(to=['up.phpteam@gmail.com'], f_host=settings.EMAIL_HOST, f_name = settings.EMAIL_NAME,
               f_port=settings.EMAIL_PORT, f_user=settings.EMAIL_HOST_USER, f_passwd=settings.EMAIL_HOST_PASSWORD,
               subject='default subject', message='content message', fail_silently=False):

    smtpserver = smtplib.SMTP(f_host, f_port)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(f_user, f_passwd)  # from email credential

    # email = EmailMultiAlternatives(
    #     subject="Here's your coupon!",
    #     body=text_body,
    #     from_email='noreply@example.com',
    #     to=['someone@example.com', ]
    # )

    # email.attach_alternative(html_body, "text/html")
    # email.mixed_subtype = 'related'
    #
    # email.send(fail_silently=False)

    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['From'] = f_name
    msg['To'] = ','.join(to)
    smtpserver.sendmail(f_user, to, msg.as_string())  # you just need to add
    smtpserver.close()


# Send Email Request End#


#User Update Request Start
@active_user_required
def updateUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    if request.method == 'POST':
        id = request.POST.get('user_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        # test = request.POST.getlist('account_ids')
        # return HttpResponse(len(test))
        
        try:
            obj = User.objects.get(pk=id)
        except User.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listUser')
        else:
            try:
                settings = MySettings.objects.get(m_user_id=id)
            except:
                settings = None
            if 'user_type' in request.POST and request.POST['user_type']:
                obj.user_type = request.POST.get('user_type')
            if 'first_name' in request.POST and request.POST['first_name']:
                obj.first_name = request.POST.get('first_name')
            if 'last_name' in request.POST and request.POST['last_name']:
                obj.last_name = request.POST.get('last_name')
            if 'display_name' in request.POST:
                obj.display_name = request.POST.get('display_name')
            if 'is_active' in request.POST:
                obj.is_active = 'True'
            else:
                obj.is_active = 'False'
            if 'login_permit' in request.POST:
                obj.login_permit = 'True'
            else:
                obj.login_permit = 'False'
            # if 'sys_admin' in request.POST:
            #     obj.admin = 'True'
            # else:
            #     obj.admin = 'False'      
            if 'phone' in request.POST:
                obj.phone_no = request.POST.get('phone')
            if 'email' in request.POST:
                obj.email = request.POST.get('email')
            if 'email' in request.POST:
                obj.username = request.POST.get('email')
            if 'mob_sms_email' in request.POST:
                obj.mob_sms_email = request.POST.get('mob_sms_email')
            if 'suppress_all_emails' in request.POST:
                obj.suppress_emails = 'True'
            else:
                obj.suppress_emails = 'False'
            if 'time_zone' in request.POST and request.POST['time_zone']:
                obj.user_time_zone = request.POST.get('time_zone')
            if 'org_id' in request.POST and request.POST['org_id']:
                obj.user_org_id = request.POST.get('org_id')
            if 'dep_id' in request.POST:
                obj.user_dep_id = request.POST.get('dep_id')
            if 'client_id' in request.POST:
                obj.user_client_id = request.POST.get('client_id')
            if 'address1' in request.POST:
                obj.address1 = request.POST.get('address1')
            if 'address2' in request.POST:
                obj.address2 = request.POST.get('address2')
            if 'city' in request.POST:
                obj.user_city = request.POST.get('city')
            if 'state' in request.POST:
                obj.user_state = request.POST.get('state')
            if 'zip' in request.POST:
                obj.user_zip_code = request.POST.get('zip')
            if 'country' in request.POST:
                obj.user_country = request.POST.get('country')

            obj.save()

            # User Account Membership Start#
            cursor = connection.cursor()
            if 'account_ids' in request.POST:
                accountIDs = request.POST.getlist('account_ids')
                if accountIDs:
                    #Delete Already Existing Entries
                    cursor.execute("delete from AT_UserAccountRelation where user_id = %s", [id])
                    for accountID in accountIDs:
                        #Insert New Entries
                        query="insert into AT_UserAccountRelation(user_id, account_id) values(%s,%s)";
                        data_tuple=(obj.id,accountID)
                        cursor.execute(query,data_tuple)
            # User Account Membership End# 

            if not settings:
                m = MySettings(m_user_id=id, m_time_zone='NULL', m_default_page=request.POST.get('default_home_page'),
                               m_ticket_screen=0, m_redirect_to=request.POST.get('redirect_to'),
                               m_dashboard_reload=0, m_show_reload='False', m_phone=None, m_email=None,
                               m_mob_sms_email=None, m_address1=None, m_address2=None, m_user_city=None,
                               m_user_state=None, m_user_zip_code=None, m_user_country=None , m_org_id=org_id)
                m.save()
            else:
                if 'default_home_page' in request.POST:
                    settings.m_default_page = request.POST.get('default_home_page')
                if 'redirect_to' in request.POST:
                    settings.m_redirect_to = request.POST.get('redirect_to')
                settings.save()

            # Add User Menu Permision in DB Start#

            UserMenuPermissions.objects.filter(user_id=id).delete()
            menu_ids = request.POST.getlist('menus')
            submenu_ids = request.POST.getlist('submenus')
            print(menu_ids)
            print(submenu_ids)
            for submenuid in submenu_ids:
                permit_obj = UserMenuPermissions(user_id=id, submenu_id=submenuid)
                permit_obj.save()

            for menuid in menu_ids:
                permit_obj = UserMenuPermissions(user_id=id, menu_id=menuid)
                permit_obj.save()
            # Add User Menu Permision in DB End#

            # User Group Membership Start#

            UserGroupMembership.objects.filter(m_user_id=id).delete()
            group_membership = request.POST.getlist('group_membership')
            if group_membership:
                if 'multiselect-all' in group_membership:
                    group_membership.remove('multiselect-all')
            for group_id in group_membership:
                membership_obj = UserGroupMembership(m_user_id=id, m_group_id=group_id, m_org_id=org_id)
                membership_obj.save()

            # User Group Membership End#

            #Adding Permission Actions to UserActionPermission table            
            permission_actions = request.POST.getlist('permission_action')
            permission_sub_actions = request.POST.getlist('permission_sub_action')
            user = User.objects.get(pk=id)
            UserActionPermission.objects.filter(user_id=user).delete()
            UserSubActionPermission.objects.filter(user_id=user).delete()
            for permission_action in permission_actions:
                permission_action_obj = PermissionAction.objects.get(perm_act_id=permission_action)
                user_act_obj = UserActionPermission(user_id=user.id, perm_act_id=permission_action, user_org_id=org_id)
                user_act_obj.save()
            for permission_sub_action in permission_sub_actions:
                per_sub_action_obj = PermissionSubAction.objects.get(sub_act_id=permission_sub_action)
                user_act_obj = UserSubActionPermission(user_id=user.id, sub_act_id=permission_sub_action)
                user_act_obj.save()            
            #END Adding Permission Actions to UserActionPermission table 

            #EMAIL SENT on USER Update Start#
            subject = 'User Account Updated 😎'
            to = []
            to.append(obj.email)           
            message = 'Hi '+obj.first_name+', <br> Your account is successfully updated Please see the changes at ATG Extra Project <span style="font-size:20px">&#128525;</span>.<br><br> Thanks. <br> Regards, <br>World best known 😎, <br> ATG Extra Team.'
            send_email(to=to, subject=subject, message=message)
            # EMAIL SENT on USER Update End#

        messages.success(request, 'Request Succeed! User updated.')
        return redirect('listUser')
    else:
        messages.error(request, 'Request Failed! User cannot be updated.Please try again.')
        return redirect('listUser')

# User Update Request End#


# User Delete Request Start#

@active_user_required
def deleteUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    user_id = request.GET.get('UserID')
    try:
        id = signing.loads(user_id,salt=settings.SALT_KEY)
        obj = User.objects.get(pk=id)
    except User.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listUser')
    else:
        #Deleting Permission Actions to UserActionPermission table            
        user = User.objects.get(pk=id)
        UserActionPermission.objects.filter(user_id=user).delete()
        UserSubActionPermission.objects.filter(user_id=user).delete()
        #Deleting Permission Actions to UserActionPermission table 

        obj.is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! User deleted.')
        return redirect('listUser')

# User Delete Request End#


# User Add Request Start#

@active_user_required
def exportUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    return render(request, 'Organization/org_add.html')

# User Add Request End#


#Datatable Code Start Here#
class UserListJson(BaseDatatableView):
    # The model we're going to show
    model = User

    # define the columns that will be returned
    # columns = ['action', 'org_id', 'org_name', 'is_internal', 'display']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    # order_columns = ['', 'org_id', 'org_name', 'is_internal']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        # allUsers = User.objects.all().values('id', 'username','first_name','last_name','user_type','user_dep_id','email','phone_no').filter(is_delete=0).union(
        # UserTemplate.objects.all().values('user_temp_id', 'username', 'first_name', 'last_name').filter(is_delete=0).annotate(user_type=Value(3, output_field=IntegerField())).annotate(user_dep_id=Value(None, output_field=CharField())).annotate(email=Value(None, output_field=CharField())).annotate(phone_no=Value(None, output_field=CharField()))
        # )
        org_id = self.request.user.user_org_id
        # return User.objects.filter(is_delete=0)
        global_user = isGlobalUser(self.request)
        if self.request.user.user_type_slug != global_user:
            SQL = '''
            SELECT [AT_Users].[id], 
                [AT_Users].[username], 
                [AT_Users].[first_name], 
                [AT_Users].[last_name], 
                [AT_Users].[user_type], 
                [AT_Users].[user_dep_id], 
                [AT_Users].[email], 
                [AT_Users].[phone_no],
                [AT_Organizations].[org_name]  as org_name 
            FROM [AT_Users] 
            JOIN AT_Organizations on AT_Organizations.org_id=AT_Users.user_org_id
            WHERE [AT_Users].[is_delete] = 0 and user_org_id = '''+"'"+str(org_id)+"'"+''' 
            UNION 
            SELECT [AT_UserTemplates].[user_temp_id], 
                [AT_UserTemplates].[username], 
                [AT_UserTemplates].[first_name], 
                [AT_UserTemplates].[last_name], 
                2 AS [user_type], 
                NULL AS [user_dep_id], 
                NULL AS [email], 
                NULL AS [phone_no],
                NULL AS [template_org_id] 
            FROM [AT_UserTemplates] order by [AT_Organizations].[org_name]
            '''
        else:
            SQL = '''
            SELECT [AT_Users].[id], 
                [AT_Users].[username], 
                [AT_Users].[first_name], 
                [AT_Users].[last_name], 
                [AT_Users].[user_type], 
                [AT_Users].[user_dep_id], 
                [AT_Users].[email], 
                [AT_Users].[phone_no],
                [AT_Organizations].[org_name]  as org_name
            FROM [AT_Users] 
            JOIN AT_Organizations on AT_Organizations.org_id=AT_Users.user_org_id
            WHERE [AT_Users].[is_delete] = 0 and admin = 1 or user_org_id = '''+"'"+str(org_id)+"'"+'''
            UNION 
            SELECT [AT_UserTemplates].[user_temp_id], 
                [AT_UserTemplates].[username], 
                [AT_UserTemplates].[first_name], 
                [AT_UserTemplates].[last_name], 
                2 AS [user_type], 
                NULL AS [user_dep_id], 
                NULL AS [email], 
                NULL AS [phone_no],
                NULL AS [template_org_id] 
            FROM [AT_UserTemplates] order by [AT_Organizations].[org_name]
            '''
        return User.objects.raw(SQL)
        # return User.objects.raw("select * from AT_Users")
        # return allUsers
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.id,salt=settings.SALT_KEY)
        if column == 'action':
            # escape HTML for security reasons
            if row.user_type == 2:
                return ''
            else:
                if row.user_org_id != self.request.user.user_org_id:
                        return '<a href="Admin_UserEdit?UserID=' + str(rid) + '"><i class="fa fa-pencil"></i></a>  | <a href="Admin_UserAttachments?UserID=' + str(rid) + '"><i class="fa fa-paperclip"></i></a>'
                else:
                    return '<a href="Admin_UserEdit?UserID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_UserDel?UserID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></i></a> | <a href="Admin_UserAttachments?UserID=' + str(rid) + '"><i class="fa fa-paperclip"></i></a>'
        elif column == 'username': 
                return '<a class="ticket_id_link" href="Home_ViewUser?UserID=' + str(rid) + '">'+str(row.username)+'</a>'   
        elif column == 'display':
            return '<a href="viewUserTickets/' + str(row.id) + '" class="bg-warning text-white"> View Tickets </a>'
        elif column == 'user_type':
            if row.user_type == 0:
                return 'Agent'
            elif row.user_type == 1:
                return 'End User'
            else:
                return 'Template User'
        else:
            return super(UserListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            search = '%'+search+'%'
            qs = User.objects.raw('''
            SELECT a.id, 
                a.username, 
                a.first_name, 
                a.last_name, 
                a.user_type, 
                a.user_dep_id, 
                a.email, 
                a.phone_no 
            FROM AT_Users a
            WHERE a.is_delete = 0 
            and(
                a.username like %s
                or a.first_name like %s
                or a.last_name like %s
                or (
                    select count(*)
                    from AT_Departments d
                    where d.dep_id = a.user_dep_id
                    and d.dep_name like %s
                )>0
                or a.email like %s
                or a.phone_no like %s
            )
            UNION 
            SELECT b.user_temp_id, 
                b.username, 
                b.first_name, 
                b.last_name, 
                2 AS user_type, 
                NULL AS user_dep_id, 
                NULL AS email, 
                NULL AS phone_no 
            FROM AT_UserTemplates b
            Where 1=1
            and(
                b.username like %s
                or b.first_name like %s
                or b.last_name like %s
            )
            ''',[search,search,search,search,search,search,search,search,search])
            # print(qs)
            # org = user_org.org_name
            # qs = qs.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(user_dep__dep_name__icontains=search) | Q(email__icontains=search) | Q(phone_no__icontains=search))
            # qs = qs.filter(name__istartswith=search)

        # more advanced example using extra parameters
        # filter_customer = self.request.GET.get('customer', None)
        #
        # if filter_customer:
        #     customer_parts = filter_customer.split(' ')
        #     qs_params = None
        #     for part in customer_parts:
        #         q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
        #         qs_params = qs_params | q if qs_params else q
        #     qs = qs.filter(qs_params)
        return qs

        # def prepare_results(self, qs):
        #     # prepare list with output column data
        #     # queryset is already paginated here
        #     json_data = []
        #     for item in qs:
        #         json_data.append([
        #             escape("{0}".format('OK')),
        #             escape(item.org_id),  # escape HTML for security reasons
        #             escape(item.org_name),  # escape HTML for security reasons
        #             escape(item.is_internal),  # escape HTML for security reasons
        #             escape("{0}".format('OK'))
        #             # item.get_state_display(),
        #             # item.created.strftime("%Y-%m-%d %H:%M:%S"),
        #
        #         ])
        #     return json_data


#Datatable Code End Here#



#Validate Username for Uniqueness Start#

@csrf_exempt
def validate(request):
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        # probably you want to add a regex check if the username value is valid here
        if username:
            is_exist = User.objects.filter(username=username).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Username for Uniqueness End#


#SetTimeZone to the Current TimeZone on the Bases of Session Start#

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'itrak/User/user_add.html', {'timezones': pytz.common_timezones})


#SetTimeZone to the Current TimeZone on the Bases of Session End#

#clone user
@active_user_required
def cloneUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/User/clone_user.html', context)

@active_user_required
def userLookUp(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    if request.method == 'POST':
        lookupuser = request.POST.get('user_id')
        look_user_id = request.user.id
        look_org_id = request.user.user_org_id
        global_user = isGlobalUser(request)
        if request.user.user_type_slug != global_user:
            try:
                userid = User.objects.get(username=lookupuser).id
                rid = signing.dumps(userid)
                user_id = signing.loads(rid)
                data = User.objects.filter(user_org_id=look_org_id).get(pk=user_id)
                print(data)
                data.allowed_groups = list(data.userMembership.filter(is_delete=0).values_list('m_group_id', flat=True))
                data.group_list = list(get_group_list(request, data.user_type))
                data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0).filter(org_id=look_org_id)
                data.departments = Department.objects.filter(d_is_delete=0).filter(user_org_id=look_org_id)
                data.clients = Client.objects.filter(cl_is_delete=0)
                settings = MySettings.objects.filter(m_user_id=user_id).first()
            except:
                messages.error(request, 'No User Found!')
                return redirect(request.META['HTTP_REFERER'])
        else:
            try:
                userid = User.objects.get(username=lookupuser).id
                rid = signing.dumps(userid)
                user_id = signing.loads(rid)
                data = User.objects.get(pk=user_id)
                data.allowed_groups = list(data.userMembership.filter(is_delete=0).values_list('m_group_id', flat=True))
                data.group_list = list(get_group_list(request, data.user_type))
                data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
                data.departments = Department.objects.filter(d_is_delete=0)
                data.clients = Client.objects.filter(cl_is_delete=0)
                settings = MySettings.objects.filter(m_user_id=user_id).first()
            except:
                messages.error(request, 'No User Found!')
                return redirect(request.META['HTTP_REFERER'])
        if not data:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('userLookUp')
        else:
            load_sidebar = get_sidebar(request)
            menus_allowed = list(get_user_menus_permit(request, user_id))
            submenus_allowed = list(get_user_submenus_permit(request, user_id))
            # return HttpResponse(submenus_allowed)
            context = {
                'sidebar': load_sidebar,
                'timezones': pytz.common_timezones,
                'menus_allowed': menus_allowed,
                'submenus_allowed': submenus_allowed,
                'settings': settings,
                'data': data
            }
            # return render(request, 'itrak/User/user_edit.html', context)
            return redirect(reverse('cloneUserform') + '?UserID=' + str(rid))
            # return render(request, 'itrak/User/clone_user_form.html', context)

@active_user_required
def cloneUserform(request):
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('UserID')
    curr_user_id = request.user.id
    curr_user_org = request.user.user_org_id
    try:
        user_id = signing.loads(id)
        print(user_id)
        data = User.objects.get(pk=user_id)
        data.allowed_groups = list(data.userMembership.filter(is_delete=0).values_list('m_group_id', flat=True))
        data.group_list = list(get_group_list(request, data.user_type))
        global_user = isGlobalUser(request)
        if request.user.user_type_slug != global_user:
            data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0).filter(org_id=curr_user_org)
            data.departments = Department.objects.filter(d_is_delete=0).filter(user_org_id=curr_user_org)
        else:
            data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
            data.departments = Department.objects.filter(d_is_delete=0)
        data.clients = Client.objects.filter(cl_is_delete=0)
        settings = MySettings.objects.filter(m_user_id=user_id).first()
        permissions = PermissionSection.objects.all()  
    except User.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listUser')
    else:
        load_sidebar = get_sidebar(request)
        menus_allowed = list(get_user_menus_permit(request, user_id))
        submenus_allowed = list(get_user_submenus_permit(request, user_id))
        actions_list = user_action_permissions(request, data)
        sub_actions_list = user_sub_action_permissions(request, data)
        disabled_actions= permissions_not_allowed(request, data)
        disabled_sub_action= sub_permissions_not_allowed(request, data)
        # return HttpResponse(submenus_allowed)
        context = {
            'sidebar': load_sidebar,
            'timezones': pytz.common_timezones,
            'menus_allowed': menus_allowed,
            'submenus_allowed': submenus_allowed,
            'actions_list':actions_list,
            'sub_actions_list':sub_actions_list,
            'disabled_actions':disabled_actions,
            'disabled_sub_action':disabled_sub_action,
            'permissions':permissions,
            'settings': settings,
            'data': data,
            'user_id': user_id,
            'curr_user_id':curr_user_id,
        }
        return render(request, 'itrak/User/clone_user_form.html', context)
#clone user

#search user
@active_user_required
def searchUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
    departments = Department.objects.filter(d_is_delete=0)
    clients = Client.objects.filter(cl_is_delete=0)
    permissions = PermissionAction.objects.filter(is_delete=0)
    context = {
        'sidebar': load_sidebar,
        'organizations': organizations,
        'departments': departments,
        'permissions':permissions,
        'clients': clients,
    }
    return render(request, 'itrak/User/search_user.html', context)

@active_user_required
def userSearchResults(request):
    if request.method == 'POST':
        user_id = request.user.id
        org_id = request.user.user_org_id
        global_user = isGlobalUser(request)
        kwargs = {
            '{0}__{1}'.format('is_delete', 'iexact'): 0,

        }
        user_status_dict = {"0": "User"}
        user_type_dict = {"1":"EndUser","0":"Agent"}
        fielddict = {}
        if 'record_type' in request.POST and request.method == 'POST' and request.POST.get('record_type') != '':
            record_type = request.POST.get('record_type')
            # kwargs.setdefault('record_type__iexact', record_type)
            # fielddict.update({'User Status': user_status_dict[record_type]})
        if 'user_type' in request.POST and request.method == 'POST' and request.POST.get('user_type') != '':
            user_type = request.POST.get('user_type')
            kwargs.setdefault('user_type__iexact', user_type)
            fielddict.update({'User Type': user_type_dict[user_type]})
        # if 'username' in request.POST and request.method == 'POST' and request.POST.get('username') != '':
        #     username = request.POST.get('username')
        #     kwargs.setdefault('username__icontains', username)
        #     fielddict.update({'User ID': username})
        if 'email' in request.POST and request.method == 'POST' and request.POST.get('email') != '':
            username = request.POST.get('email')
            kwargs.setdefault('email__icontains', username)
            fielddict.update({'User ID': username})
        if 'first_name' in request.POST and request.method == 'POST' and request.POST.get('first_name') != '':
            first_name = request.POST.get('first_name')
            kwargs.setdefault('first_name__icontains', first_name)
            fielddict.update({'First Name': first_name})
        if 'last_name' in request.POST and request.method == 'POST' and request.POST.get('last_name') != '':
            last_name = request.POST.get('last_name')
            kwargs.setdefault('last_name__icontains', last_name)
            fielddict.update({'Last Name': last_name})
        if 'display_name' in request.POST and request.method == 'POST' and request.POST.get('display_name') != '':
            display_name = request.POST.get('display_name')
            kwargs.setdefault('display_name__icontains', display_name)
            fielddict.update({'Display Name': display_name})
        if 'phone' in request.POST and request.method == 'POST' and request.POST.get('phone') != '':
            phone = request.POST.get('phone')
            kwargs.setdefault('phone_no__startswith', phone)
            fielddict.update({'Phone No': phone})
        if 'email' in request.POST and request.method == 'POST' and request.POST.get('email') != '':
            email = request.POST.get('email')
            kwargs.setdefault('email__startswith', email)
            fielddict.update({'Email': email})
        if 'log_permit' in request.POST and request.method == 'POST' and request.POST.get('log_permit') != '':
            permission = request.POST.get('log_permit')
            kwargs.setdefault('login_permit__iexact', permission)
            global_user = isGlobalUser(request)
            if request.user.user_type_slug != global_user:
                if permission == '1' and 'is_active' in request.POST:
                    print('global not')
                    is_active = request.POST.get('is_active')
                    if is_active == '1':
                        log_permit = User.objects.filter(is_delete=0).filter(is_active=1).filter(user_org_id=org_id).filter(**kwargs).distinct().count()
                        fielddict.update({'User with Log In Permission': log_permit})
                    else:
                        log_permit = User.objects.filter(is_delete=0).filter(is_active=0).filter(user_org_id=org_id).filter(**kwargs).distinct().count()
                        fielddict.update({'User with Log In Permission': log_permit})
            else:
                if permission == '1' and 'is_active' in request.POST:
                    is_active = request.POST.get('is_active')
                    print('global')
                    if is_active == '1':
                        log_permit = User.objects.filter(is_delete=0).filter(is_active=1).filter(**kwargs).distinct().count()
                        fielddict.update({'User with Log In Permission': log_permit})
                    else:
                        log_permit = User.objects.filter(is_delete=0).filter(is_active=0).filter(**kwargs).distinct().count()
                        fielddict.update({'User with Log In Permission': log_permit})

        if 'perm_id' in request.POST and request.method == 'POST' and request.POST.get('perm_id') != '':
            perm_id = request.POST.get('perm_id')
            user_id = UserActionPermission.objects.filter(perm_act_id=perm_id).filter(is_delete=0).values_list('user_id')
            kwargs.setdefault('id__in', user_id)
            result = PermissionAction.objects.only('description').get(pk=perm_id).description
            fielddict.update({'Permission': result})
        
        if 'dep_id' in request.POST and request.method == 'POST' and request.POST.get('dep_id') != '':
            dep_id = request.POST.get('dep_id')
            kwargs.setdefault('user_dep_id', dep_id)
            global_user = isGlobalUser(request)
            if request.user.user_type_slug != global_user:
                print('global not')
                result = Department.objects.filter(user_org_id=org_id).only('dep_name').get(pk=dep_id).dep_name
            else:
                print('global')
                result = Department.objects.only('dep_name').get(pk=dep_id).dep_name
            fielddict.update({'Departments': result})
        if 'client_id' in request.POST and request.method == 'POST' and request.POST.get('client_id') != '':
            client_id = request.POST.get('client_id')
            kwargs.setdefault('user_client_id', client_id)
            result = Client.objects.only('client_name').get(pk=client_id).client_name
            fielddict.update({'Client': result})
        if 'org_id' in request.POST and request.method == 'POST' and request.POST.get('org_id') != '':
            org_id = request.POST.get('org_id')
            kwargs.setdefault('user_org_id', org_id)
            global_user = isGlobalUser(request)
            if request.user.user_type_slug != global_user:
                print('global not')
                result = Organization.objects.filter(org_id=org_id).only('org_name').get(pk=org_id).org_name
            else:
                print('global ')
                result = Organization.objects.only('org_name').get(pk=org_id).org_name
            fielddict.update({'Organization': result})
        if 'is_active' in request.POST and request.method == 'POST' and request.POST.get('is_active_rec') != '':
            is_active = request.POST.get('is_active')
            user_type = request.POST.get('user_type')
            # User.objects.filter(Q(user_type=user_type) | Q(**kwargs)).distinct().count()
            kwargs.setdefault('is_active__iexact', is_active)
            global_user = isGlobalUser(request)
            if request.user.user_type_slug != global_user:
                print('global not')
                if is_active == '1':
                    print(kwargs)
                    is_actives = User.objects.filter(user_org_id=org_id).filter(**kwargs).distinct().count()
                    fielddict.update({'Active User': is_actives})
                else:
                    is_actives = User.objects.filter(user_org_id=org_id).filter(**kwargs).distinct().count()
                    fielddict.update({'In Active User': is_actives})
            else:
                print('global ')
                if is_active == '1':
                    print(kwargs)
                    is_actives = User.objects.filter(**kwargs).distinct().count()
                    fielddict.update({'Active User': is_actives})
                else:
                    is_actives = User.objects.filter(**kwargs).distinct().count()
                    fielddict.update({'In Active User': is_actives})
        # if 'log_permit' in request.POST and request.method == 'POST' and request.POST.get('log_permit') != '':
        #     log_permit = request.POST.get('log_permit')
        #     print(log_permit)
        if 'output_view' in request.POST and request.method == 'POST' and request.POST.get('output_view') != '':
            output_view = request.POST.get('output_view')
        sortargs = []
        sortresponse = []
        sortdict = {
            "last_name": "Last Name",
            "first_name": "First Name",
            "display_name": "Display Name",
            "username": "User Id",
            "user_dep_id": "Department",
            "user_type": "User Type"
        }
        sortorder_dict = {
            "0": "Asc",
            "1": "Desc"
        }
        if 'sort_column1' in request.POST and request.method == 'POST' and request.POST.get('sort_column1') != '':
            sort_column1 = request.POST.get('sort_column1')
            sort_order1 = request.POST.get('sort_order1')
            if sort_order1 == '0':
                sort_value = sort_column1
            else:
                sort_value = '-' + sort_column1
            sortargs.append(sort_value)
            sortresponse.append(sortdict[sort_column1] + " , " + sortorder_dict[sort_order1])
            print(sortargs)
            print(sortresponse)
            
        # if not sortargs:
        if not output_view == 'BriefList':
            # if output_view == 'BriefList':
            #     if 'is_active' in request.POST and request.method == 'POST' and request.POST.get('is_active') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'user_type' in request.POST and request.method == 'POST' and request.POST.get('user_type') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'username' in request.POST and request.method == 'POST' and request.POST.get('username') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'first_name' in request.POST and request.method == 'POST' and request.POST.get('first_name') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'last_name' in request.POST and request.method == 'POST' and request.POST.get('last_name') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'display_name' in request.POST and request.method == 'POST' and request.POST.get('display_name') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'phone' in request.POST and request.method == 'POST' and request.POST.get('phone') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'email' in request.POST and request.method == 'POST' and request.POST.get('email') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'dep_id' in request.POST and request.method == 'POST' and request.POST.get('dep_id') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'client_id' in request.POST and request.method == 'POST' and request.POST.get('client_id') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()
            #     if 'org_id' in request.POST and request.method == 'POST' and request.POST.get('org_id') != '':
            #         if output_view == 'BriefList':
            #             users = User.objects.filter(**kwargs).distinct()

            if output_view == 'CountOnly':
                global_user = isGlobalUser(request)
                if request.user.user_type_slug != global_user:
                    is_count = User.objects.filter(user_org_id=org_id).filter(**kwargs).distinct().count()
                else:
                    is_count = User.objects.filter(**kwargs).distinct().count()
                context = {
                    'sortresponses': sortresponse,
                    'output_view': output_view,
                    'is_count': is_count
                }
                return render(request, 'itrak/User/user_search_list.html', context)
            if output_view == 'DetailExcel':
                print('excel')
                if request.user.user_type_slug != global_user:
                    users = User.objects.filter(user_org_id=org_id).filter(**kwargs).distinct()
                else:
                    users = User.objects.filter(**kwargs).distinct()
                return get_xls_from_user(request, list(users))
        else:
            if 'user_type' in request.POST and request.method == 'POST':
                if output_view == 'BriefList':
                    if request.user.user_type_slug != global_user:
                        print('global not else')
                        users = User.objects.filter(user_org_id = org_id).filter(**kwargs).distinct().order_by(*sortargs)
                    else:
                        print('global else')
                        users = User.objects.filter(**kwargs).distinct().order_by(*sortargs)
            if 'username' in request.POST and request.method == 'POST':
                if output_view == 'BriefList':
                    if request.user.user_type_slug != global_user:
                        users = User.objects.filter(user_org_id=org_id).filter(**kwargs).distinct().order_by(*sortargs)
                    else:
                        users = User.objects.filter(**kwargs).distinct().order_by(*sortargs)
            if 'first_name' in request.POST and request.method == 'POST':
                if output_view == 'BriefList':
                    if request.user.user_type_slug != global_user:
                        users = User.objects.filter(user_org_id = org_id).filter(**kwargs).distinct().order_by(*sortargs)
                    else:
                        users = User.objects.filter(**kwargs).distinct().order_by(*sortargs)
            if 'last_name' in request.POST and request.method == 'POST':
                if output_view == 'BriefList':
                    if request.user.user_type_slug != global_user:
                        users = User.objects.filter(user_org_id = org_id).filter(**kwargs).distinct().order_by(*sortargs)
                    else:
                        users = User.objects.filter(**kwargs).distinct().order_by(*sortargs)
            if 'display_name' in request.POST and request.method == 'POST':
                if output_view == 'BriefList':
                    if request.user.user_type_slug != global_user:
                        users = User.objects.filter(user_org_id = org_id).filter(**kwargs).distinct().order_by(*sortargs)
                    else:
                        users = User.objects.filter(**kwargs).distinct().order_by(*sortargs)
            if 'dep_id' in request.POST and request.method == 'POST':
                if output_view == 'BriefList':
                    if request.user.user_type_slug != global_user:
                        users = User.objects.filter(user_org_id = org_id).filter(**kwargs).distinct().order_by(*sortargs)
                    else:
                        users = User.objects.filter(**kwargs).distinct().order_by(*sortargs)

        context = {
            'users': users,
            'sortresponses': sortresponse,
            'output_view': output_view,
            'fielddict': fielddict
        }
        # print(kwargs)
        # print(fielddict)
        # print(users)
        return render(request, 'itrak/User/user_search_list.html',context)
#search user

#userID Maintaince start
@active_user_required
def userIDmaintenance(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/User/Admin_UserChangeUserID.html',context)

#userID Maintaince end

#userID Maintaince merge start
@active_user_required
def UserMerge(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    user_id = request.user.id
    org_id = request.user.user_org_id
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        users = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_org_id=org_id)
    else:
        users = User.objects.filter(is_active=1).filter(is_delete=0)
    context = {
        'sidebar': load_sidebar,
        'users':users,
    }
    return render(request, 'itrak/User/user_merge_duplicate.html',context)

#userID Maintaince merge end

#userID Maintaince merge update start
@active_user_required
def DuplicateUserMerge(request):
    if request.method == 'POST':
         
        # --------Variable prime_user is Secondary User------- #
        prime_user= request.POST.get('prime_usr_id')
        # --------Variable secon_user is Primary User------- #
        secon_user = request.POST.get('second_usr_id')
        # return HttpResponse(prime_user+'-'+secon_user)
        user_is_delete = request.POST.get('is_delete')
        primeuserData = User.objects.get(pk=prime_user)
        seconduserData = User.objects.get(pk=secon_user)

        if int(primeuserData.user_type) == 0 or int(seconduserData.user_type) == 0:
            primeuserData.user_type = 0
            primeuserData.save()
        

        UserMenuPermission = UserMenuPermissions.objects.filter(user_id=secon_user)
        UserGroupMemberships = UserGroupMembership.objects.filter(is_delete=0).filter(m_user_id=secon_user)
        UserTickets = Ticket.objects.filter(ticket_is_delete=0).filter(Q(ticket_caller_id=secon_user) | Q(ticket_next_action_id=secon_user) | Q(ticket_next_action_id=secon_user) | Q(ticket_next_action_by_id=secon_user) | Q(ticket_assign_to_id=secon_user) | Q(ticket_assign_by_id=secon_user) | Q(ticket_is_open_by_id=secon_user) | Q(ticket_is_close_by_id=secon_user) | Q(ticket_is_reopen_by_id=secon_user) | Q(ticket_created_by_id=secon_user) | Q(ticket_modified_by_id=secon_user) | Q(ticket_closed_by_id=secon_user))
        UserTicketNotes = TicketNote.objects.filter(note_is_delete=0).filter(Q(note_created_by_id=secon_user) | Q(note_modified_by_id=secon_user))
        UserTicketUserRoleLog = TicketUserRoleLog.objects.filter(Q(urlog_user_id=secon_user) | Q(urlog_created_by_id=secon_user) | Q(urlog_modified_by_id=secon_user))
        UserTaskGroupManager = TaskGroupManager.objects.filter(tmgrgp_is_delete=0).filter(Q(tg_task_assigned_to_id=secon_user) | Q(tg_task_created_by_id=secon_user) | Q(tg_task_modified_by_id=secon_user))
        UserTaskManager = TaskManager.objects.filter(tmgr_is_delete=0).filter(Q(task_assigned_to_id=secon_user) | Q(tmgr_completion_userId_id=secon_user) | Q(task_created_by_id=secon_user) | Q(task_modified_by_id=secon_user))
        UserTicketAttachments = TicketAttachments.objects.filter(attach_is_delete=0).filter(Q(attach_created_by_id=secon_user) | Q(attach_modified_by_id=secon_user))
        UserMySettings = MySettings.objects.filter(m_user_id=secon_user)
        UserTicketSavedSearch = TicketSavedSearch.objects.filter(Q(submitted_by_id=secon_user) | Q(note_entered_by_id=secon_user) | Q(entered_by_id=secon_user) | Q(assigned_by_id=secon_user) | Q(ticket_assigned_to_id=secon_user) | Q(next_action_id=secon_user) | Q(closed_by_id=secon_user) | Q(task_assigned_to_id=secon_user) | Q(save_modified_by_id=secon_user) | Q(save_modified_by_id=secon_user))
        UserTicketsRoles = TicketsRoles.objects.filter(t_is_deleted=0).filter(Q(t_created_by_id=secon_user) | Q(t_modified_by_id=secon_user))
        UserTicketsActions = TicketsActions.objects.filter(t_action_is_deleted=0).filter(Q(t_action_created_by_id=secon_user) | Q(t_action_modified_by_id=secon_user))
        UserTicketsEmailNotificationPermissions = TicketsEmailNotificationPermissions.objects.filter(t_email_is_deleted=0).filter(Q(t_email_created_by_id=secon_user) | Q(t_email_modified_by_id=secon_user))
        UserSavedQBQuries = SavedQBQuries.objects.filter(qb_query_is_delete=0).filter(Q(qb_created_by_id=secon_user) | Q(qb_modified_by_id=secon_user))
        UserSavedQBQuriesShareWith = SavedQBQuriesShareWith.objects.filter(qb_query_share_with_id=secon_user)
        UUserSentEmails = UserSentEmails.objects.filter(Q(use_sent_to_id=secon_user) | Q(use_created_by_id=secon_user))
        UserSavedRBReports = SavedRBReports.objects.filter(rb_report_is_delete=0).filter(Q(rb_created_by_id=secon_user) | Q(rb_modified_by_id=secon_user))
        UserSavedRBReportsShareWith = SavedRBReportsShareWith.objects.filter(rb_report_share_with_id=secon_user)
        UserScheduledReport = ScheduledReport.objects.filter(sch_rpt_is_delete=0).filter(Q(notify_error_id=secon_user) | Q(sch_rpt_created_by_id=secon_user) | Q(sch_rpt_modified_by_id=secon_user))
        UserOrginaztionContract = OrginaztionContract.objects.filter(org_contract_is_delete=0).filter(Q(org_contract_created_by_id=secon_user) | Q(org_contract_modified_by_id=secon_user))
        UserScheduleReportResp = ScheduleReportResp.objects.filter(sr_resp_recipt_user_id=secon_user)


        if UserMenuPermission:
            for ump in UserMenuPermission:
                # INSERT PERMISSION IF PRIMARY USER DOES NOT HAVE PERMISSION OF SECONDARY USER
                IsExist = UserMenuPermissions.objects.filter(user_id=prime_user).filter(menu_id=ump.menu_id).filter(submenu_id=ump.submenu_id).exists()
                if IsExist == False:
                    permit_obj = UserMenuPermissions(user_id=prime_user, menu_id=ump.menu_id, submenu_id=ump.submenu_id)
                    permit_obj.save()


        if UserGroupMemberships:
            for ugm in UserGroupMemberships:
                # ADD MEMBERSHIP IF PRIMARY USER DOES NOT HAVE MEMBERSHIP OF GROUP THAT SECONDARY USER HAVE
                IsExist = UserGroupMembership.objects.filter(m_user_id=prime_user).filter(m_group_id=ugm.m_group_id).exists()
                if IsExist == False:
                    group_membership_obj = UserGroupMembership(m_user_id=prime_user, m_group_id=ugm.m_group_id)
                    group_membership_obj.save()


        if UserTickets:
            for ut in UserTickets:
                if ut.ticket_caller_id == int(secon_user):
                    ut.ticket_caller_id = int(prime_user)
                    ut.save()
                if ut.ticket_next_action_id == int(secon_user):
                    ut.ticket_next_action_id = int(prime_user)
                    ut.save()
                if ut.ticket_next_action_by_id == int(secon_user):
                    ut.ticket_next_action_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_assign_to_id == int(secon_user):
                    ut.ticket_assign_to_id = int(prime_user)
                    ut.save()
                if ut.ticket_assign_by_id == int(secon_user):
                    ut.ticket_assign_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_is_open_by_id == int(secon_user):
                    ut.ticket_is_open_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_is_close_by_id == int(secon_user):
                    ut.ticket_is_close_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_is_reopen_by_id == int(secon_user):
                    ut.ticket_is_reopen_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_created_by_id == int(secon_user):
                    ut.ticket_created_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_modified_by_id == int(secon_user):
                    ut.ticket_modified_by_id = int(prime_user)
                    ut.save()
                if ut.ticket_closed_by_id == int(secon_user):
                    ut.ticket_closed_by_id = int(prime_user)
                    ut.save()


        
        if UserTicketNotes:
            for utn in UserTicketNotes:
                if utn.note_created_by_id == int(secon_user):
                    utn.note_created_by_id = int(prime_user)
                    utn.save()
                if utn.note_modified_by_id == int(secon_user):
                    utn.note_modified_by_id = int(prime_user)
                    utn.save()
        if UserTicketUserRoleLog:
            for utrl in UserTicketUserRoleLog:
                if utrl.urlog_user_id == int(secon_user):
                    utrl.urlog_user_id = int(prime_user)
                    utrl.save()
                if utrl.urlog_created_by_id == int(secon_user):
                    utrl.urlog_created_by_id = int(prime_user)
                    utrl.save()
                if utrl.urlog_modified_by_id == int(secon_user):
                    utrl.urlog_modified_by_id = int(prime_user)
                    utrl.save()
        if UserTaskGroupManager:
            for utgm in UserTaskGroupManager:
                if utgm.tg_task_assigned_to_id == int(secon_user):
                    utgm.tg_task_assigned_to_id = int(prime_user)
                    utgm.save()
                if utgm.tg_task_created_by_id == int(secon_user):
                    utgm.tg_task_created_by_id = int(prime_user)
                    utgm.save()
                if utgm.tg_task_modified_by_id == int(secon_user):
                    utgm.tg_task_modified_by_id = int(prime_user)
                    utgm.save()
        if UserTaskManager:
            for utm in UserTaskManager:
                if utm.task_assigned_to_id == int(secon_user):
                    utm.task_assigned_to_id = int(prime_user)
                    utm.save()
                if utm.tmgr_completion_userId_id == int(secon_user):
                    utm.tmgr_completion_userId_id = int(prime_user)
                    utm.save()
                if utm.task_created_by_id == int(secon_user):
                    utm.task_created_by_id = int(prime_user)
                    utm.save()
                if utm.task_modified_by_id == int(secon_user):
                    utm.task_modified_by_id = int(prime_user)
                    utm.save()
        if UserTicketAttachments:
            for uta in UserTicketAttachments:
                if uta.attach_created_by_id == int(secon_user):
                    uta.attach_created_by_id = int(prime_user)
                    uta.save()
                if uta.attach_modified_by_id == int(secon_user):
                    uta.attach_modified_by_id = int(prime_user)
                    uta.save()
        if UserTicketSavedSearch:
            for uts in UserTicketSavedSearch:
                if uts.submitted_by_id == int(secon_user):
                    uts.submitted_by_id = int(prime_user)
                    uts.save()
                if uts.note_entered_by_id == int(secon_user):
                    uts.note_entered_by_id = int(prime_user)
                    uts.save()
                if uts.entered_by_id == int(secon_user):
                    uts.entered_by_id = int(prime_user)
                    uts.save()
                if uts.assigned_by_id == int(secon_user):
                    uts.assigned_by_id = int(prime_user)
                    uts.save()
                if uts.ticket_assigned_to_id == int(secon_user):
                    uts.ticket_assigned_to_id = int(prime_user)
                    uts.save()
                if uts.next_action_id == int(secon_user):
                    uts.next_action_id = int(prime_user)
                    uts.save()
                if uts.closed_by_id == int(secon_user):
                    uts.closed_by_id = int(prime_user)
                    uts.save()
                if uts.task_assigned_to_id == int(secon_user):
                    uts.task_assigned_to_id = int(prime_user)
                    uts.save()
                if uts.save_created_by_id == int(secon_user):
                    uts.task_assigned_to_id = int(prime_user)
                    uts.save()
                if uts.save_modified_by_id == int(secon_user):
                    uts.save_modified_by_id = int(prime_user)
                    uts.save()
        if UserTicketsRoles:
            for utr in UserTicketsRoles:
                if utr.t_created_by_id == int(secon_user):
                    utr.t_created_by_id = int(prime_user)
                    utr.save()
                if utr.t_modified_by_id == int(secon_user):
                    utr.t_modified_by_id = int(prime_user)
                    utr.save()
        if UserTicketsActions:
            for uta in UserTicketsActions:
                if uta.t_action_created_by_id == int(secon_user):
                    uta.t_action_created_by_id = int(prime_user)
                    uta.save()
                if uta.t_action_modified_by_id == int(secon_user):
                    uta.t_action_modified_by_id = int(prime_user)
                    uta.save()
        if UserSavedQBQuries:
            for usQBq in UserSavedQBQuries:
                if usQBq.qb_created_by_id == int(secon_user):
                    usQBq.qb_created_by_id = int(prime_user)
                    usQBq.save()
                if usQBq.qb_modified_by_id == int(secon_user):
                    usQBq.qb_modified_by_id = int(prime_user)
                    usQBq.save()
        if UserSavedQBQuriesShareWith:
            for usQBsw in UserSavedQBQuriesShareWith:
                if usQBsw.qb_query_share_with_id == int(secon_user):
                    usQBsw.qb_query_share_with_id = int(prime_user)
                    usQBsw.save()
        if UUserSentEmails:
            for uuse in UUserSentEmails:
                if uuse.use_sent_to_id == int(secon_user):
                    uuse.use_sent_to_id = int(prime_user)
                    uuse.save()
                if uuse.use_created_by_id == int(secon_user):
                    uuse.use_created_by_id = int(prime_user)
                    uuse.save()
        if UserSavedRBReports:
            for usRBr in UserSavedRBReports:
                if usRBr.rb_created_by_id == int(secon_user):
                    usRBr.rb_created_by_id = int(prime_user)
                    usRBr.save()
                if usRBr.rb_modified_by_id == int(secon_user):
                    usRBr.rb_modified_by_id = int(prime_user)
                    usRBr.save()
        if UserSavedRBReportsShareWith:
            for usRBrsw in UserSavedRBReportsShareWith:
                if usRBrsw.rb_report_share_with_id == int(secon_user):
                    usRBrsw.rb_report_share_with_id = int(prime_user)
                    usRBrsw.save()
        if UserScheduledReport:
            for usr in UserScheduledReport:
                if usr.notify_error_id == int(secon_user):
                    usr.notify_error_id = int(prime_user)
                    usr.save()
                if usr.sch_rpt_created_by_id == int(secon_user):
                    usr.sch_rpt_created_by_id = int(prime_user)
                    usr.save()
                if usr.sch_rpt_modified_by_id == int(secon_user):
                    usr.sch_rpt_modified_by_id = int(prime_user)
                    usr.save()
        if UserOrginaztionContract:
            for uoc in UserOrginaztionContract:
                if uoc.org_contract_created_by_id == int(secon_user):
                    uoc.org_contract_created_by_id = int(prime_user)
                    uoc.save()
                if uoc.org_contract_modified_by_id == int(secon_user):
                    uoc.org_contract_modified_by_id = int(prime_user)
                    uoc.save()
        if UserScheduleReportResp:
            for usrr in UserScheduleReportResp:
                if usrr.sr_resp_recipt_user_id == int(secon_user):
                    uoc.org_contract_modified_by_id = int(prime_user)
                    uoc.save()

        if UserTicketsEmailNotificationPermissions:
            for utenp in UserTicketsEmailNotificationPermissions:
                if utenp.t_email_created_by_id == int(secon_user):
                    utenp.t_email_created_by_id = int(secon_user)
                    utenp.save()
                if utenp.t_email_modified_by_id == int(secon_user):
                    utenp.t_email_modified_by_id = int(secon_user)
                    utenp.save()
        

        # if UserTicketsEmailNotificationPermissions:
        #     for ugm in UserTicketsEmailNotificationPermissions:
        #         # INSERT EMAIL NOTIFICATIOn PERMISSION IF PRIMARY USER DOES NOT HAVE PERMISSION OF SECONDARY USER
        #         IsExist = UserGroupMembership.objects.filter(m_user_id=prime_user).filter(m_group_id=ugm.m_group_id).exists()
        #         if IsExist == False:
        #             group_membership_obj = UserGroupMembership(m_user_id=prime_user, m_group_id=ugm.m_group_id)
        #             group_membership_obj.save()



        if 'is_delete' in request.POST:
            print('delete')
            #----Deleting Secondary User but variable name is primeuserData----#
            seconduserData.is_delete = 1
            seconduserData.save()
        messages.success(request, 'Request Succeed! User Merged Succussfully.')
        return redirect('UserMerge')


#userID Maintaince merge update end

#userID change page start
@active_user_required
def UserChangeID(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/User/user_change_userID.html',context)

#userID change page end

#userID change  start
@active_user_required
def userChangeIDupdate(request):
    if request.method == 'POST':
        orginal_user_id = request.POST.get('orginal_user_id')
        new_user_id = request.POST.get('new_user_id')
        user_id = request.user.id
        org_id = request.user.user_org_id
        global_user = isGlobalUser(request)
        if request.user.user_type_slug != global_user:
            userdata = User.objects.filter(user_org_id=org_id).filter(username=orginal_user_id,email=orginal_user_id).values('id').first()
        else:
            userdata = User.objects.filter(username=orginal_user_id,email=orginal_user_id).values('id').first()
        if userdata:
            id = userdata["id"]
            # obj =User.objects.filter(pk=id)
            try:
                obj = User.objects.get(pk=id)
            except User.DoesNotExist:
                return render_to_response('itrak/page-404.html')
            # If Object Response is Empty
            if not obj:
                messages.error(request, 'Request Failed! No Record Found.')
                return redirect('UserChangeID')
            else:
                if 'new_user_id' in request.POST:
                    obj.username = request.POST.get('new_user_id')
                    obj.email = request.POST.get('new_user_id')
                obj.save()
            # updateUserdata = User(username=new_user_id)
            # updateUserdata.save()
            messages.success(request, 'Request Succeed! User updated.')
            return redirect('UserChangeID')
        else:
            messages.error(request, 'Request Failed! No Record Found.')
            return redirect('UserChangeID')
    else:
        messages.error(request, 'Request Failed!')
        return redirect('UserChangeID')
#userID change  end

#user Summary start
@active_user_required
def userSummary(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    org_id = request.user.user_org_id
    user_id = request.user.id
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        agentsCount = User.objects.filter(user_org_id=org_id).filter(user_type =0).filter(is_active=1).filter(is_delete=0).distinct().count()
        endUsers = User.objects.filter(user_org_id=org_id).filter(user_type =1).filter(is_active=1).filter(is_delete=0).distinct().count()
        activeUser = User.objects.filter(user_org_id=org_id).filter(is_active=1).filter(user_type__in = [1, 0]).filter(is_delete=0).distinct().count()
        inactiveUser = User.objects.filter(user_org_id=org_id).filter(is_active=0).filter(is_delete=0).distinct().count()
        totalUser = User.objects.filter(user_org_id=org_id).filter(is_delete=0).distinct().count()
        sysAdmin = User.objects.filter(user_org_id=org_id).filter(is_delete=0).filter(admin=1).distinct().count()
        loginPermit = User.objects.filter(user_org_id=org_id).filter(is_delete=0).filter(is_active=1).filter(login_permit=1).distinct().count()
        notloginPermit = User.objects.filter(user_org_id=org_id).filter(is_delete=0).filter(is_active=1).filter(login_permit=0).distinct().count()
    else:
        agentsCount = User.objects.filter(user_type =0).filter(is_active=1).filter(is_delete=0).distinct().count()
        endUsers = User.objects.filter(user_type =1).filter(is_active=1).filter(is_delete=0).distinct().count()
        activeUser = User.objects.filter(is_active=1).filter(user_type__in = [1, 0]).filter(is_delete=0).distinct().count()
        inactiveUser = User.objects.filter(is_active=0).filter(is_delete=0).distinct().count()
        totalUser = User.objects.filter(is_delete=0).distinct().count()
        sysAdmin = User.objects.filter(is_delete=0).filter(admin=1).distinct().count()
        loginPermit = User.objects.filter(is_delete=0).filter(is_active=1).filter(login_permit=1).distinct().count()
        notloginPermit = User.objects.filter(is_delete=0).filter(is_active=1).filter(login_permit=0).distinct().count()
    can_assign_tickets = get_userids_with_permission(request,1).count() # 1 for 'can assign tickets' permission 
    can_be_assigned_tickets = get_userids_with_permission(request,2).count() # 2 for 'can be assigned tickets' permission 
    can_submit_tickets  = get_userids_with_permission(request,3).count() # 3 for 'can submit tickets' permission 
    can_access_and_maintain_admin  = get_userids_with_permission(request,4).count() # 3 for 'can access and maintain admin' permission 
    # total_can_assign_tickets = count(can_assign_tickets)
    # for can_assign_ticket in can_assign_tickets:
    #     user_act_obj = User.objects.filter(pk=can_assign_ticket[0]).get(display_name)    
    
    context = {
        'sidebar': load_sidebar,
        'agentsCount':agentsCount,
        'endUsers':endUsers,
        'activeUser':activeUser,
        'inactiveUser':inactiveUser,
        'totalUser':totalUser,
        'sysAdmin':sysAdmin,
        'loginPermit':loginPermit,
        'notloginPermit':notloginPermit,
        'can_assign_tickets':can_assign_tickets,
        'can_be_assigned_tickets':can_be_assigned_tickets,
        'can_submit_tickets':can_submit_tickets,
        'can_access_and_maintain_admin':can_access_and_maintain_admin,

    }
    return render(request, 'itrak/User/userSummary.html',context)

#user Summary  end

#User Files start
def saveUserFiles(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    print(request.FILES)
    return HttpResponse("Reached")

@active_user_required
def userAttachments(request): 
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)

    id = request.GET.get('UserID')
    try:
        user_id = signing.loads(id,salt=settings.SALT_KEY)
        data = User.objects.get(pk=user_id)
    except Ticket.DoesNotExist:
        return render_to_response('itrak/page-404.html')

    
    attachments = get_user_attachments(request, user_id)
    context = {
        'sidebar': load_sidebar,
        'data':data,
        'user_id':user_id,
        'attachments':attachments,
    }
    return render(request, 'itrak/User/user_attachment.html', context)

@active_user_required
def saveUserAttachmentFiles(request): 
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'user_id' in request.POST:
            user_id = request.POST.get('user_id')
        if 'file1' in request.FILES and request.FILES['file1'] or 'file2' in request.FILES and request.FILES['file2'] or 'file3' in request.FILES and request.FILES['file3']:
            if 'file1' in request.FILES and request.FILES['file1']:
                file1 = request.FILES['file1']
                size = file1.size/1000
                if size > 1000:
                    file_size = str(round((size/1000), 2)) + 'MB'
                else:
                    file_size = str(round(size, 2)) + 'KB'
                newattach = UserAttachment(ua_user_id=user_id, ua_file_path=file1, ua_file_name=file1, ua_file_size=file_size)
                newattach.save()
            if 'file2' in request.FILES and request.FILES['file2']:
                file2 = request.FILES['file2']
                size = file2.size / 1000
                if size > 1000:
                    file_size = str(round((size/1000), 2)) + 'MB'
                else:
                    file_size = str(round(size, 2)) + 'KB'
                newattach = UserAttachment(ua_user_id=user_id, ua_file_path=file2, ua_file_name=file2, ua_file_size=file_size)
                newattach.save()
            if 'file3' in request.FILES and request.FILES['file3']:
                file3 = request.FILES['file3']
                size = file3.size / 1000
                if size > 1000:
                    file_size = str(round((size/1000), 2)) + 'MB'
                else:
                    file_size = str(round(size, 2)) + 'KB'
                newattach = UserAttachment(ua_user_id=user_id, ua_file_path=file3, ua_file_name=file3, ua_file_size=file_size)
                newattach.save()
            messages.success(request, 'Request Succeed! Attachment added.')    

        # fs = FileSystemStorage()
        # filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)
            files = request.FILES.getlist('attach_files')
            if files:
                for file in files:
                    size = file.size / 1000
                    if size > 1000:
                        file_size = str(round((size / 1000), 2)) + 'MB'
                    else:
                        file_size = str(round(size, 2)) + 'KB'
                    newattach = UserAttachment(ua_user_id=user_id, ua_file_path=file, ua_file_name=file, ua_file_size=file_size)
                    newattach.save()
                messages.success(request, 'Request Succeed! Attachments updated.')
                # return redirect('listUser')
            try:
                user_id = signing.dumps(user_id, salt=settings.SALT_KEY)
            except User.DoesNotExist:
                return render_to_response('itrak/page-404.html')
            # return redirect(saveUserAttachmentFiles, id=user_id)
            return redirect(reverse('userAttachments') + '?UserID=' + str(user_id))
            # return redirect('listUser')
        else:
            messages.error(request, 'Request Failed! Attachment cannot be submitted. Please try again.')
            try:
                user_id = signing.dumps(user_id, salt=settings.SALT_KEY)
            except User.DoesNotExist:
                return render_to_response('itrak/page-404.html')
            # return redirect(saveUserAttachmentFiles, id=user_id)
            return redirect(reverse('userAttachments') + '?UserID=' + str(user_id)) 
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Attachment cannot be submitted.Please try again.')
        return redirect('listUser')

# User Attachment Delete Request Start#
@active_user_required
def deleteUserAttach(request):
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    if request.method == 'GET':
        ua_id = request.GET.get('ua_id')
        user_id = UserAttachment.objects.values_list('ua_user_id', flat=True).get(pk=ua_id)
        try:
            obj = UserAttachment.objects.get(pk=ua_id)
        except UserAttachment.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            # return redirect('attachTicket',str(id))
            rev_id = signing.dumps(user_id, salt=settings.SALT_KEY)
            return redirect(reverse('userAttachments') + '?UserID=' + str(rev_id))
        else:
            obj.ua_is_delete = 1
            obj.save()
            messages.success(request, 'Request Success! Attachment deleted.')
            # return redirect('attachTicket',str(obj.attach_ticket_id))
            rev_id = signing.dumps(user_id, salt=settings.SALT_KEY)
            return redirect(reverse('userAttachments') + '?UserID=' + str(rev_id))

# User Attachment Delete Request End#

@login_required
def changeUsersPassword(request):

    user_id = request.GET.get('user_id')
    load_sidebar = get_sidebar(request)
    obj = User.objects.get(username=request.user.username)
    users = User.objects.filter(is_delete=0)
    data = User.objects.get(pk=user_id)
    context = {
            'sidebar': load_sidebar,
            'users': users,
            'data':data,
            'user_id':user_id,
    }
    return render(request, 'itrak/User/change_users_password.html', context)

def userPasswordChange(request): 
        if request.method == 'POST':
            password = request.POST['old_password']
            user_id = request.POST['user_id']
            # return HttpResponse(password)
            if request.user.check_password(password):
                obj = User.objects.get(pk=user_id)
                obj.set_password(request.POST.get('password1'))
                obj.save()
                messages.success(request, 'Password has been updated!')
                rev_id = signing.dumps(user_id, salt=settings.SALT_KEY)
                return redirect(reverse('editUser') + '?UserID=' + str(rev_id))
            else:
                messages.error(request, 'Authorize Password is wrong! Password cannot be updated.Please try again.')
                # rev_id = signing.dumps(user_id, salt=settings.SALT_KEY)
                return redirect(reverse('changeUsersPassword') + '?user_id=' + str(user_id))

# User View Start#
@active_user_required
def viewUser(request):
    id = request.GET.get('UserID')
    try:
        user_id = signing.loads(id,salt=settings.SALT_KEY)
        data = User.objects.get(pk=user_id)
        data.allowed_groups = list(data.userMembership.filter(is_delete=0).values_list('m_group_id', flat=True))
        data.group_list = list(get_group_list(request, data.user_type))
        data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
        data.departments = Department.objects.filter(d_is_delete=0)
        settings1 = MySettings.objects.filter(m_user_id=user_id).first()
        permissions = PermissionSection.objects.filter(is_active=1).all() 
        if Ticket.objects.filter(ticket_is_delete=0).filter(ticket_caller_id=user_id).exists():
            tickets = Ticket.objects.filter(ticket_is_delete=0).filter(ticket_caller_id=user_id)
        else:    
            tickets = Ticket.objects.filter(ticket_is_delete=0).filter(ticket_created_by_id=user_id)

        # GET ASSOCIATED ACCOUNTS WITH USER
        SQL  = """
            select 
                GA.id
                ,GA.acc_name
            from AT_UserAccountRelation UAR with(nolock)
            JOIN GlobalACCTS GA with(nolock) ON GA.id = UAR.account_id
            where user_id = """+str(user_id)+"""
        """
        print(SQL)
        cursor = connection.cursor()
        cursor.execute(SQL)
        accounts = dictfetchall(cursor)
    except User.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listUser')
    else:
        load_sidebar = get_sidebar(request)
        menus_allowed = list(get_user_menus_permit(request, user_id))
        submenus_allowed = list(get_user_submenus_permit(request, user_id))                      
        actions_list = user_action_permissions(request, data)
        sub_actions_list = user_sub_action_permissions(request, data)
        disabled_actions= permissions_not_allowed(request, data)
        disabled_sub_action= sub_permissions_not_allowed(request, data)
        print(disabled_actions)
        print(disabled_sub_action)
        
        context = {
            'sidebar': load_sidebar,
            'timezones': pytz.common_timezones,
            'menus_allowed': menus_allowed,
            'submenus_allowed': submenus_allowed,
            'settings1': settings1,
            'data': data,
            'permissions': permissions,
            'actions_list': actions_list,
            'sub_actions_list': sub_actions_list,
            'disabled_actions': disabled_actions,            
            'disabled_sub_action': disabled_sub_action,
            'tickets':tickets,
            'user_id':user_id,  
            'accounts':accounts
        }
    return render(request, 'itrak/User/user_view.html', context)

# User View End#

#User View Membership Group update Start#

@active_user_required
def updateViewGroupMembershipUser(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.POST.get('user_id')
    if 'group_membership' in request.POST:    
        UserGroupMembership.objects.filter(m_user_id=id).delete()
        group_membership = request.POST.getlist('group_membership')
        if group_membership:
            if 'multiselect-all' in group_membership:
                group_membership.remove('multiselect-all')
        for group_id in group_membership:
            membership_obj = UserGroupMembership(m_user_id=id, m_group_id=group_id)
            membership_obj.save()

        messages.success(request, 'Request Succeed! User updated.')
        rev_id = signing.dumps(id, salt=settings.SALT_KEY)
        return redirect(reverse('viewUser') + '?UserID=' + str(rev_id))
    else:
        messages.error(request, 'Request Failed! Please Select Group Membership.')
        rev_id = signing.dumps(id, salt=settings.SALT_KEY)
        return redirect(reverse('viewUser') + '?UserID=' + str(rev_id))
#User View Membership Group update End#

#User Email Notification Start#    
@active_user_required
def userEmailNotification(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('UserID')
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    ticket_roles = TicketsRoles.objects.filter(t_is_default=0)
    tickets_actions = TicketsActions.objects.all()
    userData = User.objects.get(pk=id)
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'ticket_roles': ticket_roles,
        'tickets_actions': tickets_actions,
        'userData': userData
    }
    return render(request, 'itrak/User/user_email_Notification_permissions.html', context)
#User Email Notification End#

#User Summary Datatable Code Start Here#
class UserSummaryListJson(BaseDatatableView):
    # The model we're going to show
    model = User

    # define the columns that will be returned
    # columns = ['action', 'org_id', 'org_name', 'is_internal', 'display']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    # order_columns = ['', 'org_id', 'org_name', 'is_internal']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def get_initial_queryset(self):
        summary_type = self.request.GET.get('type')
        user_id = self.request.user.id
        org_id = self.request.user.user_org_id
        global_user = isGlobalUser(self.request)
        if self.request.user.user_type_slug != global_user:
            if summary_type == 'Agents':
                return User.objects.filter(user_org_id=org_id).filter(user_type=0).filter(is_active=1).filter(is_delete=0).distinct()
            if summary_type == 'endUser':
                return User.objects.filter(user_org_id=org_id).filter(user_type=1).filter(is_active=1).filter(is_delete=0).distinct()
            if summary_type == 'sysAdmin':
                return User.objects.filter(user_org_id=org_id).filter(is_delete=0).filter(admin=1).distinct()
            if summary_type == 'withlogin':
                return User.objects.filter(user_org_id=org_id).filter(is_delete=0).filter(is_active=1).filter(login_permit=1).distinct()
            if summary_type == 'withoutlogin':
                return User.objects.filter(user_org_id=org_id).filter(is_delete=0).filter(is_active=1).filter(login_permit=0).distinct()
            if summary_type == 'totalActive':
                return User.objects.filter(user_org_id=org_id).filter(is_active=1).filter(user_type__in = [1, 0]).filter(is_delete=0).distinct()
            if summary_type == 'totalInActive':
                return User.objects.filter(user_org_id=org_id).filter(is_active=0).filter(is_delete=0).distinct()
            if summary_type == 'totalUsers':
                return User.objects.filter(user_org_id=org_id).filter(is_delete=0).distinct()
            if summary_type == 'can_assign_tickets':    
                user_ids = UserActionPermission.objects.filter(user_org_id=org_id).filter(perm_act_id=1).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
            if summary_type == 'can_be_assigned_tickets':    
                user_ids = UserActionPermission.objects.filter(user_org_id=org_id).filter(perm_act_id=2).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
            if summary_type == 'can_submit_tickets':    
                user_ids = UserActionPermission.objects.filter(user_org_id=org_id).filter(perm_act_id=3).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
            if summary_type == 'can_access_and_maintain_admin':    
                user_ids = UserActionPermission.objects.filter(user_org_id=org_id).filter(perm_act_id=4).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
        else:
            if summary_type == 'Agents':
                return User.objects.filter(user_type=0).filter(is_active=1).filter(is_delete=0).distinct()
            if summary_type == 'endUser':
                return User.objects.filter(user_type=1).filter(is_active=1).filter(is_delete=0).distinct()
            if summary_type == 'sysAdmin':
                return User.objects.filter(is_delete=0).filter(admin=1).distinct()
            if summary_type == 'withlogin':
                return User.objects.filter(is_delete=0).filter(is_active=1).filter(login_permit=1).distinct()
            if summary_type == 'withoutlogin':
                return User.objects.filter(is_delete=0).filter(is_active=1).filter(login_permit=0).distinct()
            if summary_type == 'totalActive':
                return User.objects.filter(is_active=1).filter(user_type__in = [1, 0]).filter(is_delete=0).distinct()
            if summary_type == 'totalInActive':
                return User.objects.filter(is_active=0).filter(is_delete=0).distinct()
            if summary_type == 'totalUsers':
                return User.objects.filter(is_delete=0).distinct()
            if summary_type == 'can_assign_tickets':    
                user_ids = UserActionPermission.objects.filter(perm_act_id=1).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
            if summary_type == 'can_be_assigned_tickets':    
                user_ids = UserActionPermission.objects.filter(perm_act_id=2).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
            if summary_type == 'can_submit_tickets':    
                user_ids = UserActionPermission.objects.filter(perm_act_id=3).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
            if summary_type == 'can_access_and_maintain_admin':    
                user_ids = UserActionPermission.objects.filter(perm_act_id=4).filter(is_delete=0).values_list('user_id').distinct()
                return User.objects.filter(pk__in=user_ids)
               
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.

        return User.objects.filter(is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.id,salt=settings.SALT_KEY)
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_UserEdit?UserID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_UserDel?UserID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></i></a>'
        elif column == 'username': 
            return '<a class="ticket_id_link" href="Home_ViewUser?UserID=' + str(rid) + '">'+str(row.username)+'</a>'   
        elif column == 'display':
            return '<a href="viewUserTickets/' + str(row.id) + '" class="bg-warning text-white"> View Tickets </a>'
        elif column == 'user_type':
            if row.user_type == '0':
                return 'Agent'
            else:
                return 'End User'
        elif column == 'last_login':
            if row.last_login is not None:
                local_dt = row.last_login
                return datetime.strptime(str(local_dt),'%Y-%m-%d %H:%M:%S.%f%z').strftime('%m/%d/%Y %I:%M%p')        
        else:
            return super(UserSummaryListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(user_dep__dep_name__icontains=search) | Q(email__icontains=search) | Q(phone_no__icontains=search))
            # qs = qs.filter(name__istartswith=search)

        # more advanced example using extra parameters
        # filter_customer = self.request.GET.get('customer', None)
        #
        # if filter_customer:
        #     customer_parts = filter_customer.split(' ')
        #     qs_params = None
        #     for part in customer_parts:
        #         q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
        #         qs_params = qs_params | q if qs_params else q
        #     qs = qs.filter(qs_params)
        return qs


#User Summary Datatable Code End Here#


#User Email Notification Start#    
# @active_user_required
# def test(request):
#     allUsers = User.objects.all().values('id', 'username','first_name','last_name','user_type','user_dep_id','email','phone_no').filter(is_delete=0).union(
#     UserTemplate.objects.all().values('user_temp_id', 'username', 'first_name', 'last_name').annotate(user_type=Value(3, output_field=IntegerField())).annotate(user_dep_id=Value(None, output_field=CharField())).annotate(email=Value(None, output_field=CharField())).annotate(phone_no=Value(None, output_field=CharField()))
#     )
#     # for user in allUsers:
#     #     print("basitali")
#     return HttpResponse(allUsers.query)

#showGroupsnWhichGivesPermisison on Modal Through ID Start#
@csrf_exempt
def showGroupsnWhichGivesPermisison(request):
    if request.method == 'POST' and request.is_ajax():
        user_id = request.POST.get('user_id')
        per_id = request.POST.get('per_id')
        allGroupUsersPermissions = GroupActionPermission.objects.raw('''
            SELECT 
                1 AS group_act_per_id
                ,(
                    select g.group_display_name
                    from AT_Groups g
                    where g.group_id = GRP.group_id 
                ) as group_name
                ,GRP.group_id 
                
            FROM AT_GroupActionPermissions GRP
            WHERE GRP.perm_act_id = %s
            AND GRP.group_id in 
            (
                Select JOG.m_group_id
                From  AT_UserGroupMembership JOG with(nolock)
                Where JOG.m_user_id = %s
            )
            '''
            ,[per_id,user_id]
        )
        groupExternal = []
        for group in allGroupUsersPermissions:
            groupEnternal = {}
            groupEnternal['group_id'] = signing.dumps(group.group_id,salt=settings.SALT_KEY)
            groupEnternal['group_name'] = group.group_name
            groupExternal.append(groupEnternal)

        return HttpResponse(json.dumps(groupExternal), content_type="application/json")

#showGroupsnWhichGivesPermisison on Modal Through ID End#

# Account List load Ajax Data Start#
@csrf_exempt
def accountListJsonData(request):
    if request.is_ajax() and request.method == 'POST':
        # load All Accounts Data
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM GlobalACCTS")
        accountValues = cursor.fetchall()
        mainArray = []
        for index, tuple in enumerate(accountValues):
            innerArray = {}
            innerArray['ID'] = str(tuple[0])
            innerArray['NAME'] = tuple[3]
            mainArray.append(innerArray) 
            
        return HttpResponse(json.dumps(mainArray), content_type="application/json")
    else:
        return HttpResponse('fail')
# Account List load Ajax Data End#

#Selected Account List load Ajax Data Start#
@csrf_exempt
def selectedAccountListJsonData(request):
    if request.is_ajax() and request.method == 'POST':
        user_id = request.POST.get('user_id')
        sysAdmin = request.POST.get('sysAdmin')
        cursor = connection.cursor()
        if sysAdmin == '1': 
            cursor.execute("select AIAN_DK, acc_number, id from GlobalACCTS")
        else:
            cursor.execute("SELECT * FROM AT_UserAccountRelation WHERE user_id = %s", [user_id])
        accountsSelectedValues = cursor.fetchall()
        accountsSelectedValuesList = []
        for index, tuple in enumerate(accountsSelectedValues):
            account_id = tuple[2]
            accountsSelectedValuesList.append(str(account_id))
        return HttpResponse(json.dumps(accountsSelectedValuesList), content_type="application/json")
#Selected Account List load Ajax Data End#
# Account List load Ajax Data Start#
@csrf_exempt
def sendUserType(request):
    if request.is_ajax() and request.method == 'POST':
        # load All Accounts Data
        user_type = userType(request) 
        return HttpResponse(json.dumps(user_type), content_type="application/json")
    else:
        return HttpResponse('fail')


