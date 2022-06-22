from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from itrak.models import Organization, Client, Group, Department, User, UserManger, UserMenuPermissions, UserGroupMembership, ClientInformation
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


# Client Information Add Request Start#

@active_user_required
def addClientInfo(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }

    return render(request, 'itrak/ClientInformation/clientinfo_add.html', context)

# Client Informatioon Add Request End#


# Client Information Save Request Start#

@active_user_required
def saveClientInfo(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'record_locator' in request.POST and request.POST['record_locator']:
            record_locator = request.POST.get('record_locator')
        if 'caller_name' in request.POST:
            caller_name = request.POST.get('caller_name')
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
        if 'email' in request.POST:
            email = request.POST.get('email')
        if 'passenger_name' in request.POST:
            passenger_name = request.POST.get('passenger_name')

        obj = ClientInformation(record_locator=record_locator, caller_name=caller_name, caller_phone=phone, caller_email=email, passenger_name=passenger_name)
        obj.save()

        messages.success(request, 'Request Succeed! Client Information added.')
        return redirect('addClientInfo')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Client Information cannot be added.Please try again.')
        return redirect('addClientInfo')
# Client Information Save Request Start#


# Client Information List Request Start#

@active_user_required
def listClientInfos(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/ClientInformation/clientinfo_list.html', context)

# Client Information List Request End#


# Client Information Edit Request Start#

@active_user_required
def editClientInfo(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('ClientInfoID')
    try:
        clientInfo_id = signing.loads(id)
        data = ClientInformation.objects.get(pk=clientInfo_id)
    except ClientInformation.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listClientInfo')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/ClientInformation/clientinfo_edit.html', context)

# Client Information Edit Request End#


#Client Information Update Request Start
@active_user_required
def updateClientInfo(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('clientinfo_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = ClientInformation.objects.get(pk=id)
        except ClientInformation.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect("/Admin_ClientInfoList")
        else:
            if 'display_name' in request.POST:
                obj.caller_name = request.POST.get('display_name')
            if 'phone' in request.POST:
                obj.caller_phone = request.POST.get('phone')
            if 'email' in request.POST:
                obj.caller_email = request.POST.get('email')
            if 'passenger_name' in request.POST:
                obj.passenger_name = request.POST.get('passenger_name')

            obj.save()

        # return HttpReshtponse('Success')
        messages.success(request, 'Request Succeed! Client Information updated.')
        return redirect('listClientInfo')
    else:
        messages.error(request, 'Request Failed! Client Information cannot be updated.Please try again.')
        return redirect('listClientInfo')

# Client Information Update Request End#


# Client Information Delete Request Start#

@active_user_required
def deleteClientInfo(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('ClientInfoID')
    try:
        obj = ClientInformation.objects.get(pk=id)
    except ClientInformation.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listClientInfo')
    else:
        obj.clientinfo_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Client Information deleted.')
        return redirect('listClientInfo')

# Client Information Delete Request End#



#Datatable Code Start Here#
class ClientInfoListJson(BaseDatatableView):
    # The model we're going to show
    model = ClientInformation

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
        return ClientInformation.objects.filter(clientinfo_is_active=1).filter(clientinfo_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.clientinfo_id)
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_ClientInfoEdit?ClientInfoID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_ClientInfoDel?ClientInfoID=' + str(row.clientinfo_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'display':
            return '<a href="viewClientDetail/' + str(row.clientinfo_id) + '"  class="bg-warning text-white"> details </a>'
        else:
            return super(ClientInfoListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(record_locator__icontains=search) | Q(caller_name__icontains=search) | Q(caller_phone__icontains=search) | Q(caller_email__icontains=search) | Q(caller_phone__icontains=search) | Q(passenger_name__icontains=search))
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
def validateUnique(request):
    if request.is_ajax() and request.method == 'POST':
        record_locator = request.POST.get('record_locator')
        # probably you want to add a regex check if the username value is valid here
        if record_locator:
            is_exist = ClientInformation.objects.filter(record_locator=record_locator).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Username for Uniqueness End#





