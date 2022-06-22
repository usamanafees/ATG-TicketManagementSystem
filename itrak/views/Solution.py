from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from itrak.models import Organization, Client, Group, Department, User, UserManger, UserMenuPermissions, UserGroupMembership, ClientInformation, Priority, Solution
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


# Solution Add Request Start#

@active_user_required
def addSolution(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }

    return render(request, 'itrak/Solution/solution_add.html', context)

# Solution Add Request End#


# Solution Save Request Start#

@active_user_required
def saveSolution(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'solution_cus_id' in request.POST and request.POST['solution_cus_id']:
            solution_cus_id = request.POST.get('solution_cus_id')
        if 'display_order' in request.POST:
            display_order = request.POST.get('display_order')
        if 'solution_text' in request.POST:
            solution_text = request.POST.get('solution_text')
        org_id = request.user.user_org_id
        obj = Solution(solution_cus_id=solution_cus_id, sol_display_order=display_order, solution_text=solution_text, user_org_id=org_id)
        obj.save()

        messages.success(request, 'Request Succeed! Solution added.')
        return redirect('addSolution')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Solution cannot be added.Please try again.')
        return redirect('addSolution')
# Solution  Save Request Start#


# Solution  List Request Start#

@active_user_required
def listSolution(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Solution/solution_list.html', context)

# Solution List Request End#


# Solution Edit Request Start#

@active_user_required
def editSolution (request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('solID')
    try:
        solution_id = signing.loads(id)
        data = Solution.objects.get(pk=solution_id)
    except Solution.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listSolution')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Solution/solution_edit.html', context)

# Solution Edit Request End#


#Solution Update Request Start
@active_user_required
def updateSolution(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('solution_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Solution.objects.get(pk=id)
        except Solution.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listSolution')
        else:
            if 'solution_cus_id' in request.POST:
                obj.solution_cus_id = request.POST.get('solution_cus_id')
            if 'display_order' in request.POST:
                obj.sol_display_order = request.POST.get('display_order')
            if 'solution_text' in request.POST:
                obj.solution_text = request.POST.get('solution_text')

            obj.save()

        # return HttpReshtponse('Success')
        messages.success(request, 'Request Succeed! Solution updated.')
        return redirect('listSolution')
    else:
        messages.error(request, 'Request Failed! Solution cannot be updated.Please try again.')
        return redirect('listSolution')

# Solution  Update Request End#


# Solution  Delete Request Start#

@active_user_required
def deleteSolution (request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('solID')
    try:
        obj = Solution.objects.get(pk=id)
    except Solution.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listSolution')
    else:
        obj.sol_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Solution deleted.')
        return redirect('listSolution')

# Solution  Delete Request End#



#Datatable Code Start Here#
class SolutionListJson(BaseDatatableView):
    # The model we're going to show
    model = Solution

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
        global_user_ids = isGlobalUser(self.request)
        if self.request.user.user_type_slug != global_user_ids:
            return Solution.objects.filter(sol_is_delete=0).filter(user_org_id=org_id)
        else:
            return Solution.objects.filter(sol_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        rid = signing.dumps(row.solution_id)
        # We want to render user as a custom column
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_SolutionEdit?solID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_SolutionDel?solID=' + str(row.solution_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        else:
            return super(SolutionListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(solution_text__icontains=search) | Q(sol_display_order__icontains=search))
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
def validateSolUnique(request):
    if request.is_ajax() and request.method == 'POST':
        solution_cus_id = request.POST.get('solution_cus_id')
        org_id = request.user.user_org_id
        # probably you want to add a regex check if the Solution value is valid here
        if solution_cus_id:
            is_exist = Solution.objects.filter(user_org_id=org_id).filter(solution_cus_id=solution_cus_id).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Username for Uniqueness End#





