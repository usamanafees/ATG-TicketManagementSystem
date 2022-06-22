from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from itrak.models import Organization, Client, Group, Department, User, UserManger, UserMenuPermissions, UserGroupMembership, ClientInformation, Priority
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
from django.db.models.query import QuerySet
from django.core import signing




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


# Priority Add Request Start#

@active_user_required
def addPriority(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }

    return render(request, 'itrak/Priority/priority_add.html', context)

# Priority Add Request End#


# Priority Save Request Start#

@active_user_required
def savePriority(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'priority_name' in request.POST and request.POST['priority_name']:
            priority_name = request.POST.get('priority_name')
        if 'display_order' in request.POST:
            display_order = request.POST.get('display_order')
        if 'popup_msg' in request.POST:
            popup_msg = request.POST.get('popup_msg')
        if 'priority_color' in request.POST:
            priority_color = request.POST.get('priority_color')
        org_id = request.user.user_org_id
        obj = Priority(priority_name=priority_name, p_display_order=display_order, popup_message=popup_msg, priority_color=priority_color, user_org_id=org_id)
        obj.save()

        messages.success(request, 'Request Succeed! Priority added.')
        return redirect('addPriority')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Priority cannot be added.Please try again.')
        return redirect('addPriority')
# Priority  Save Request Start#


# Priority  List Request Start#

@active_user_required
def listPriority(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Priority/priority_list.html', context)

# Priority List Request End#


# Priority Edit Request Start#

@active_user_required
def editPriority (request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('priorityID')
    try:
        priority_id = signing.loads(id)
        data = Priority.objects.get(pk=priority_id)
    except Priority.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listPriority')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Priority/priority_edit.html', context)

# Priority Edit Request End#


#Priority Update Request Start
@active_user_required
def updatePriority(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('priority_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Priority.objects.get(pk=id)
        except Priority.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listPriority')
        else:
            if 'priority_name' in request.POST:
                obj.priority_name = request.POST.get('priority_name')
            if 'display_order' in request.POST:
                obj.p_display_order = request.POST.get('display_order')
            if 'popup_msg' in request.POST:
                obj.popup_message = request.POST.get('popup_msg')
            if 'priority_color' in request.POST:
                obj.priority_color = request.POST.get('priority_color')

            obj.save()

        # return HttpReshtponse('Success')
        messages.success(request, 'Request Succeed! Priority updated.')
        return redirect('listPriority')
    else:
        messages.error(request, 'Request Failed! Priority cannot be updated.Please try again.')
        return redirect('listPriority')

# Priority  Update Request End#


# Priority  Delete Request Start#

@active_user_required
def deletePriority (request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('priorityID')
    try:
        obj = Priority.objects.get(pk=id)
    except Priority.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listPriority')
    else:
        obj.prior_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Priority deleted.')
        return redirect('listPriority')

# Priority  Delete Request End#



#Datatable Code Start Here#
class PriorityListJson(BaseDatatableView):
    # The model we're going to show
    model = Priority

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
        org_id = self.request.user.user_org_id
        global_user = isGlobalUser(self.request)
        # if self.request.user.user_type_slug != global_user:
        return Priority.objects.filter(user_org_id=org_id).filter(prior_is_delete=0)
        # else:
        #     return Priority.objects.filter(prior_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.priority_id)
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_PriorityEdit?priorityID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_PriorityDel?priorityID=' + str(row.priority_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        else:
            return super(PriorityListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        print(search)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(priority_name__icontains=search) | Q(priority_color__icontains=search) | Q(p_display_order__icontains=search))
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
def validatePUnique(request):
    if request.is_ajax() and request.method == 'POST':
        org_id = request.user.user_org_id
        priority_name = request.POST.get('priority_name')
        # probably you want to add a regex check if the Priority value is valid here
        if priority_name:
            is_exist = Priority.objects.filter(user_org_id=org_id).filter(priority_name=priority_name).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Username for Uniqueness End#

#Priority User Permissions
@active_user_required
def priorityEmailNotification(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('priorityID')
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    priorityActions = PriorityAction.objects.all()
    priorityData = Priority.objects.get(pk=id)
    SQL = '''
        SELECT 
            distinct UP.user_id
            ,1 as id
            ,UP.priority_id
            ,(
                select U.display_name
                from AT_Users U
                where U.id = UP.user_id
            ) as display_name
            ,(
                select count(*)
                from AT_PriorityEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.priority_id = UP.priority_id
                and a.action_id = 1
            ) as On_Submit
            ,(
                select count(*)
                from AT_PriorityEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.priority_id = UP.priority_id
                and a.action_id = 2
            ) as On_Assign
            ,(
                select count(*)
                from AT_PriorityEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.priority_id = UP.priority_id
                and a.action_id = 3
            ) as On_Next_Action
            ,(
                select count(*)
                from AT_PriorityEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.priority_id = UP.priority_id
                and a.action_id = 4
            ) as On_Note
            ,(
                select count(*)
                from AT_PriorityEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.priority_id = UP.priority_id
                and a.action_id = 5
            ) as On_Close
            ,(
                select count(*)
                from AT_PriorityEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.priority_id = UP.priority_id
                and a.action_id = 6
            ) as On_Escalate
        from AT_PriorityEmailNotificationUserPermissions UP
        where UP.priority_id = %s
        order by display_name
    '''
    priorityUsers = PriorityEmailNotificationUserPermission.objects.raw(SQL,[id])
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'priorityActions': priorityActions,
        'priorityData': priorityData,
        'priorityUsers': priorityUsers,
    }
    return render(request, 'itrak/Priority/pri_email_Notification_permissions.html', context)

#ORGANIZATION ADD USER NOTIFICATION PERMISISONS
@csrf_exempt
def getModalToAddUserPermissionsInPermission(request):
    if request.method == 'POST':
        priority_id = request.POST.get('priority_id')
        allUsers = User.objects.filter(user_type = 0, is_active = 1, is_delete = 0)
        bookedUsers = PriorityEmailNotificationUserPermission.objects.filter(priority_id = priority_id).values_list('user_id',flat=True)
        context = {
            'allUsers': allUsers,
            'bookedUsers': bookedUsers,
            'priority_id': priority_id,
        }
        return render(request, 'itrak/Priority/pri_user_permission_modal.html', context)

# Priority User Save Request Start#
@active_user_required
def savePriorityUserNotificationPermissions(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        priority_id = request.POST.get('priority_id')
        user_id = request.POST.get('user_id')
        p = PriorityEmailNotificationUserPermission(
            priority_id=priority_id,
            user_id=user_id,
        )
        p.save()
        messages.success(request, 'Request Succeed! User added.')
        return redirect(reverse('priorityEmailNotification') + '?priorityID='+str(priority_id))
    else:
        messages.error(request, 'Request Failed! User cannot be added.Please try again.')
        return redirect(reverse('priorityEmailNotification') + '?priorityID='+str(priority_id))
# Org User Save Request Start#


@csrf_exempt
def getModalPriorityEmailPermissionsByID(request):
    if request.method == 'POST':
        priority_actions = PriorityAction.objects.all()
        priority_id = request.POST.get('priority_id')
        user_id = request.POST.get('user_id')
        priority = Priority.objects.get(pk = priority_id)
        user = User.objects.get(pk = user_id)
        email_permit = PriorityEmailNotificationUserPermission.objects.filter(priority_id = priority_id, user_id = user_id, email=1).values_list('action_id',flat=True)
        mobile_permit = PriorityEmailNotificationUserPermission.objects.filter(priority_id = priority_id, user_id = user_id, mobile=1).values_list('action_id',flat=True)
        # return HttpResponse(email_permit)
        context = {
            'priority': priority,
            'email_permit': email_permit,
            'mobile_permit': mobile_permit,
            'priority_actions': priority_actions,
            'user': user,
        }
        return render(request, 'itrak/Priority/pri_permission_modal.html', context)

def updatePriorityEmailMobileNotifications(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        priority_id = request.POST.get('priority_id')
        user_id = request.POST.get('user_id')
        PriorityEmailNotificationUserPermission.objects.filter(priority_id=priority_id, user_id=user_id).delete()
        
        for email in request.POST.getlist('email'):
            permit_obj = PriorityEmailNotificationUserPermission(priority_id=priority_id, user_id=user_id, email=1, action_id=email)
            permit_obj.save()
        # for mobile in request.POST.getlist('mobile'):
        #     permit_obj = OrganizationEmailNotificationUserPermission(org_id=org_id, user_id=user_id, mobile=1, action_id=mobile)
        #     permit_obj.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect(reverse('priorityEmailNotification') + '?priorityID='+str(priority_id))

def deletePriorityEmailMobilePermissions(request):
    if request.method == 'POST':
        priority_id = request.POST.get('priority_id')
        user_id = request.POST.get('user_id')
        PriorityEmailNotificationUserPermission.objects.filter(priority_id = priority_id, user_id = user_id).delete()        
        messages.success(request, 'Request Succeed! Record successfully deleted.')
        return redirect(reverse('priorityEmailNotification') + '?priorityID='+str(priority_id))

