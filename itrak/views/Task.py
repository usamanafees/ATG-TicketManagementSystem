from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from itrak.models import Organization, Client, Group, Department, User, UserManger, UserMenuPermissions, UserGroupMembership, ClientInformation, Priority, Solution, SubStatus, Task, TaskGroup, TaskManager
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
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
from django.db.models import F
from django.core import signing
from datetime import datetime
from django.db import transaction, IntegrityError
from django.urls import reverse






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


# Task Add Request Start#

@active_user_required
def addTask(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }

    return render(request, 'itrak/Task/task_add.html', context)

# Task Add Request End#


# Task Save Request Start#

@active_user_required
def saveTask(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'task_type' in request.POST and request.POST['task_type']:
            task_type = request.POST.get('task_type')
        if 'task_description' in request.POST and request.POST['task_description']:
            task_description = request.POST.get('task_description')
        if 'display_order' in request.POST:
            display_order = request.POST.get('display_order')
        org_id = request.user.user_org_id
        obj = Task(task_type= task_type, task_description=task_description, task_display_order=display_order, task_org_id=org_id)
        obj.save()

        messages.success(request, 'Request Succeed! Task added.')
        return redirect('addTask')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Task cannot be added.Please try again.')
        return redirect('addTask')
# Task  Save Request Start#


# Task  List Request Start#

@active_user_required
def listTask(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Task/task_list.html', context)

# Task List Request End#


# Task Edit Request Start#

@active_user_required
def editTask (request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('taskID')
    user_id = request.user.id
    org_id = request.user.user_org_id
    global_user_ids = isGlobalUser(request)
    try:
        task_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listTask')
    else:
        load_sidebar = get_sidebar(request)
        excluded_groups = TaskRestrict.objects.values_list('tr_group_id', flat=True).filter(tr_task_id=task_id).filter(tr_is_delete=0).exclude(tr_group_id__isnull=True)
        excluded_orgs = TaskRestrict.objects.values_list('tr_org_id', flat=True).filter(tr_task_id=task_id).filter(tr_is_delete=0).exclude(tr_org_id__isnull=True)
        taskrestricts = get_taskrestricts(request, task_id)
        if request.user.user_type_slug != global_user_ids:
            groupss = Group.objects.filter(group_org=org_id).filter(gp_is_delete=0).filter(gp_is_active=1).exclude(pk__in=excluded_groups)
            organizations = Organization.objects.filter(org_id=org_id).filter(org_is_delete=0).filter(org_is_active=1).exclude(pk__in=excluded_orgs)
        else:
            groupss = Group.objects.filter(gp_is_delete=0).filter(gp_is_active=1).exclude(pk__in=excluded_groups)
            organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1).exclude(pk__in=excluded_orgs)
        

        context = {
            'sidebar': load_sidebar,
            'data': data,
            'groups':groupss,
            'taskrestricts':taskrestricts,
            'organizations':organizations,
            'task_id':task_id
        }
        return render(request, 'itrak/Task/task_edit.html', context)

# Task Edit Request End#


#Task Update Request Start
@active_user_required
def updateTask(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('task_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Task.objects.get(pk=id)
        except Task.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listTask')
        else:
            if 'task_type' in request.POST:
                obj.task_type = request.POST.get('task_type')
            if 'task_description' in request.POST:
                obj.task_description = request.POST.get('task_description')
            if 'display_order' in request.POST:
                obj.task_display_order = request.POST.get('display_order')
            if 'is_active' in request.POST:
                obj.task_is_active = 'True'
            else:
                obj.task_is_active = 'False'

            obj.save()

        # return HttpReshtponse('Success')
        messages.success(request, 'Request Succeed! Task updated.')
        return redirect('listTask')
    else:
        messages.error(request, 'Request Failed! Task cannot be updated.Please try again.')
        return redirect('listTask')

# Task  Update Request End#


# Task  Delete Request Start#

@active_user_required
def deleteTask (request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    task_id = request.GET.get('taskID')
    try:
        id = signing.loads(task_id,salt=settings.SALT_KEY)
        obj = Task.objects.get(pk=id)
    except Task.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listTask')
    else:
        obj.task_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Task deleted.')
        return redirect('listTask')

# Task  Delete Request End#


#Datatable Code Start Here#
class TaskListJson(BaseDatatableView):
    # The model we're going to show
    model = Task

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
        # if self.request.user.user_type_slug!= global_user_ids:
        return Task.objects.filter(task_is_delete=0).filter(task_org_id=org_id)
        # else:
        #     return Task.objects.filter(task_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        rid = signing.dumps(row.task_id,salt=settings.SALT_KEY)
        # We want to render user as a custom column
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_TaskEdit?taskID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_TaskDel?taskID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'task_type':
            if row.task_type == 0:
                return 'Complete'
            else:
                return 'Yes/No/NA'
        elif column == 'task_is_active':
            if row.task_is_active == 1:
                return 'Y'
            else:
                return 'N'                
        else:
            return super(TaskListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(task_description__icontains=search) | Q(task_display_order__icontains=search))
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
def validateTaskUnique(request):
    if request.is_ajax() and request.method == 'POST':
        org_id = request.user.user_org_id
        task_description = request.POST.get('task_description')
        # probably you want to add a regex check if the Task value is valid here
        if task_description:
            is_exist = Task.objects.filter(task_org_id=org_id).filter(task_description=task_description).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Username for Uniqueness End#



# Task Group Add Request Start#

@active_user_required
def addTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }

    return render(request, 'itrak/Task/taskgroup_add.html', context)

# Task Group Add Request End#



# Task Group Save Request Start#

@active_user_required
def saveTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'task_group' in request.POST and request.POST['task_group']:
            task_group_description = request.POST.get('task_group')
        if 'display_order' in request.POST:
            display_order = request.POST.get('display_order')
        org_id = request.user.user_org_id
        obj = TaskGroup(taskgroup_description=task_group_description, taskgroup_display_order=display_order, task_group_org_id=org_id)
        obj.save()

        messages.success(request, 'Request Succeed! Task Group added.')
        return redirect('AddTaskGroup')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Task Group cannot be added.Please try again.')
        return redirect('AddTaskGroup')
# Task Group Save Request Start#


# Task Group List Request Start#

@active_user_required
def listTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Task/taskgroup_list.html', context)

# Task Group List Request End#



# Task Group Edit Request Start#

@active_user_required
def editTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    user_id = request.user.id
    org_id = request.user.user_org_id
    global_user_ids = isGlobalUser(request)
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('taskGroupId')
    try:
        task_group_id = signing.loads(id,salt=settings.SALT_KEY)
        data = TaskGroup.objects.get(pk=task_group_id)
    except TaskGroup.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listTaskGroup')
    else:
        if request.user.user_type_slug != global_user_ids:
            load_sidebar = get_sidebar(request)
            tasks = Task.objects.filter(task_org_id=org_id).filter(task_is_active=1).filter(task_is_delete=0).order_by(F('task_display_order').asc(nulls_last=True))
            taskGroups = TaskGroup.objects.filter(task_group_org_id=org_id).filter(taskgroup_is_active=1).filter(taskgroup_is_delete=0).order_by(F('taskgroup_display_order').asc(nulls_last=True))
            substatus = SubStatus.objects.filter(ss_org_id=org_id).filter(sstatus_is_delete=0)
            users = User.objects.filter(user_org_id=org_id).filter(is_active=1).filter(is_delete=0)    
            RTGs = TaskGroupRestrict.objects.values_list('tgr_task_group', flat=True).filter(tgr_is_delete=0)
            #organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1)
            excluded_groups = TaskGroupRestrict.objects.values_list('tgr_group_id', flat=True).filter(tgr_task_group_id=task_group_id).filter(tgr_is_delete=0).exclude(tgr_group_id__isnull=True)
            groupss = Group.objects.filter(group_org_id=org_id).filter(gp_is_delete=0).filter(gp_is_active=1).exclude(pk__in=excluded_groups)
            excluded_orgs = TaskGroupRestrict.objects.values_list('tgr_org_id', flat=True).filter(tgr_task_group_id=task_group_id).filter(tgr_is_delete=0).exclude(tgr_org_id__isnull=True)
            organizations = Organization.objects.filter(org_id=org_id).filter(org_is_delete=0).filter(org_is_active=1).exclude(pk__in=excluded_orgs)

            taskgrouprestricts = get_taskgrouprestricts(request, task_group_id)
            task_groups= TaskGroupRestrict.objects.values_list('tgr_id', flat=True).filter(tgr_task_group_id=task_group_id)
            list_task_groups= list(task_groups)
        else:
            load_sidebar = get_sidebar(request)
            tasks = Task.objects.filter(task_is_active=1).filter(task_is_delete=0).order_by(F('task_display_order').asc(nulls_last=True))
            taskGroups = TaskGroup.objects.filter(taskgroup_is_active=1).filter(taskgroup_is_delete=0).order_by(F('taskgroup_display_order').asc(nulls_last=True))
            substatus = SubStatus.objects.filter(sstatus_is_delete=0)
            users = User.objects.filter(is_active=1).filter(is_delete=0)    
            RTGs = TaskGroupRestrict.objects.values_list('tgr_task_group', flat=True).filter(tgr_is_delete=0)
            #organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1)
            excluded_groups = TaskGroupRestrict.objects.values_list('tgr_group_id', flat=True).filter(tgr_task_group_id=task_group_id).filter(tgr_is_delete=0).exclude(tgr_group_id__isnull=True)
            groupss = Group.objects.filter(gp_is_delete=0).filter(gp_is_active=1).exclude(pk__in=excluded_groups)
            excluded_orgs = TaskGroupRestrict.objects.values_list('tgr_org_id', flat=True).filter(tgr_task_group_id=task_group_id).filter(tgr_is_delete=0).exclude(tgr_org_id__isnull=True)
            organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1).exclude(pk__in=excluded_orgs)

            taskgrouprestricts = get_taskgrouprestricts(request, task_group_id)
            task_groups= TaskGroupRestrict.objects.values_list('tgr_id', flat=True).filter(tgr_task_group_id=task_group_id)
            list_task_groups= list(task_groups)
        context = {
            'sidebar': load_sidebar,    
            'data': data,
            'tasks': tasks,
            'taskGroups': taskGroups,
            'substatus': substatus,
            'users': users,
            'RTGs' :RTGs,
            'groups':groupss,
            'taskgrouprestricts':taskgrouprestricts,
            'task_group_id':task_group_id,
            'organizations':organizations,
        }
        return render(request, 'itrak/Task/taskgroup_edit.html', context)

# Task Group Edit Request End#


#Task Group Update Request Start
@active_user_required
def updateTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('taskgroup_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = TaskGroup.objects.get(pk=id)
        except TaskGroup.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listTaskGroup')
        else:
            if 'taskgroup_description' in request.POST:
                obj.taskgroup_description = request.POST.get('taskgroup_description')
            if 'display_order' in request.POST:
                obj.taskgroup_display_order = request.POST.get('display_order')
            if 'is_active' in request.POST:
                obj.taskgroup_is_active = 'True'
            else:
                obj.taskgroup_is_active = 'False'

            obj.save()

            if request.POST.get('changeTM') == '1':
                TaskGroupManager.objects.filter(tmgrgp_group_id=id).delete()
            if 'tmanager_task_id[]' in request.POST and request.POST.get('tmanager_task_id[]') and request.POST.get('changeTM') == '1':
                task_ids = request.POST.getlist('tmanager_task_id[]')
                task_types = request.POST.getlist('tmanager_task_type[]')
                task_notes = request.POST.getlist('tmanager_note[]')
                task_assign_tos = request.POST.getlist('tmanager_assign_to[]')
                task_due_dates = request.POST.getlist('tmanager_due_date[]')
                task_dependencies = request.POST.getlist('tmanager_task_dependency[]')
                task_orders = request.POST.getlist('tmanager_task_order[]')
                task_dependency_orders = request.POST.getlist('tmanager_dependency_order[]')
                for i,task_id in enumerate(task_ids):
                    if task_notes and task_notes[i]:
                        task_note = task_notes[i]
                    else:
                        task_note = None
                    if task_assign_tos and task_assign_tos[i]:
                        task_assigned_to_id = task_assign_tos[i]
                    else:
                        task_assigned_to_id = None
                    if task_due_dates and task_due_dates[i]:
                        task_due_date = datetime.strptime(task_due_dates[i], '%d/%m/%Y').strftime('%Y-%m-%d')
                    else:
                        task_due_date = None
                    if task_dependencies and task_dependencies[i]:
                        task_dependency = task_dependencies[i]
                    else:
                        task_dependency = None
                    if task_types and task_types[i]:
                        task_type = task_types[i]
                    else:
                        task_type = None
                    if task_orders and task_orders[i]:
                        task_order = task_orders[i]
                    else:
                        task_order = None
                    if task_dependency_orders and task_dependency_orders[i]:
                        task_depend_order = task_dependency_orders[i]
                    else:
                        task_depend_order = None

                    TMobj = TaskGroupManager(tmgrgp_task_id=task_id, tmgrgp_group_id=id, tmgrgp_display_order=task_order, tg_task_note=task_note,
                                             tg_task_assigned_to_id=task_assigned_to_id, tg_task_due_date=task_due_date, tg_task_dependency=task_dependency,
                                             tg_task_type=task_type, tg_task_depend_order=task_depend_order, tg_task_created_by_id=request.user.id)
                    TMobj.save()

            if 'tgroup_id' in request.POST and request.POST['tgroup_id']:
                tgroup_id = request.POST.get('tgroup_id')
                groupTasks = TaskManager.objects.filter(tmgr_group_id=tgroup_id)
                for task in groupTasks:
                    TMobj = TaskManager(tmgr_group_id=id, tmgr_task_id=task.tmgr_task_id, task_note=task.task_note,
                                        task_assigned_to_id=task.task_assigned_to_id, task_due_date=task.task_due_date,
                                        task_dependency=task.task_dependency, task_depend_order=task.task_depend_order)
                    TMobj.save()

            if 'task_id' in request.POST and request.POST['task_id']:
                task_id = request.POST.get('task_id')
                if 'task_note' in request.POST:
                    task_note = request.POST.get('task_note')
                if 'assign_to' in request.POST:
                    task_assigned_to_id = request.POST.get('assign_to')
                if 'due_date' in request.POST:
                    task_due_date = datetime.strptime(request.POST.get('due_date'), '%m/%d/%Y').strftime('%Y-%m-%d')
                if 'dependency' in request.POST:
                    task_dependency = request.POST.get('dependency')
                if 'task_order' in request.POST:
                    task_depend_order = request.POST.get('task_order')

                TMobj = TaskManager(tmgr_group_id=id, tmgr_task_id=task_id, task_note=task_note, task_assigned_to_id=task_assigned_to_id, task_due_date=task_due_date, task_dependency=task_dependency, task_depend_order=task_depend_order)
                TMobj.save()

        # return HttpReshtponse('Success')
        messages.success(request, 'Request Succeed! Task Group updated.')
        return redirect('listTaskGroup')
    else:
        messages.error(request, 'Request Failed! Task Group cannot be updated.Please try again.')
        return redirect('listTaskGroup')

# Task Group Update Request End#


# Task Group Delete Request Start#

@active_user_required
def deleteTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('taskGroupId')
    try:
        obj = TaskGroup.objects.get(pk=id)
    except TaskGroup.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listTask')
    else:
        obj.taskgroup_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Task Group deleted.')
        return redirect('listTaskGroup')

# Task Group Delete Request End#



#Datatable Code Start Here#
class TaskGroupListJson(BaseDatatableView):
    # The model we're going to show
    model = TaskGroup

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
        user_id = self.request.user.id
        org_id = self.request.user.user_org_id
        global_user_ids = isGlobalUser(self.request)
        if self.request.user.user_type_slug != global_user_ids:
            return TaskGroup.objects.filter(taskgroup_is_delete=0).filter(task_group_org_id=org_id)
        else:
            return TaskGroup.objects.filter(taskgroup_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.taskgroup_id,salt=settings.SALT_KEY)
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_TaskGroupEdit?taskGroupId=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_TaskGroupDel?taskGroupId=' + str(row.taskgroup_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'taskgroup_is_active':
            if row.taskgroup_is_active == 1:
                return 'Y'
            else:
                return 'N'
        elif column == 'further_tasks':
            return '<a href="Admin_TaskGroupChildList?task_id=' + str(rid) + '">Tasks</i></a>'        
        elif column == 'groupManager':
            # further_tasks= TaskGroupManager.objects.values_list('tmgrgp_group', flat=True).get(tmgrgp_group=row.taskgroup_id) 
            # for further_task in further_tasks:   
                return '<a href="Admin_TaskGroupChildList?task_id=' + str(rid) + '">Tasks</i></a>' 
        else:
            return super(TaskGroupListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(taskgroup_description__icontains=search) | Q(taskgroup_display_order__icontains=search))
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


#Get Group Task Manager on Modal Through ID Start#
def getGroupModalTaskManagerById(request):
    context = {}
    if request.method == 'POST' and request.is_ajax():
        records = json.loads(request.POST.get('records', ''))
        context['records'] = records
    return render(request, 'itrak/Task/get_taskmanager_modal_records.html', context)

#Get Group Task Manager on Modal Through ID End#

#Get Task Manager on Table Through ID Start#
def getGroupTableTaskManagerById(request):
    context = {}
    if request.method == 'POST' and request.is_ajax():
        records = json.loads(request.POST.get('records', ''))
        context['records'] = records
    return render(request, 'itrak/Task/get_taskmanager_table_records.html', context)

#Get Task Manager on Table Through ID End#



#Save Task Manager on Table Through Group ID Start#
def saveModalTaskManagerByTaskGroupId(request):
    context = {}
    response_data = {}
    if request.method == 'POST' and request.is_ajax():
        records = json.loads(request.POST.get('records', ''))
        groupId =  request.POST.get('groupId', '')
        print(records)
        with transaction.atomic():
            TaskGroupManager.objects.filter(tmgrgp_group_id=groupId).delete()
            if records:
                try:
                    for record in records:
                        task_order_val = record['task_order_val']
                        task_id_val = record['task_id_val']
                        task_assign_to_val = record['task_assign_to_val']
                        if record['task_due_date_val']:
                            task_due_date_val = datetime.strptime(record['task_due_date_val'], '%d/%m/%Y').strftime('%Y-%m-%d')
                        else:
                            task_due_date_val = None
                        task_type_val = record['task_type_val']
                        task_note_val = record['task_note_val']
                        task_dependency_val = record['task_dependency_val']
                        task_dependency_order_val = record['task_dependency_order_val']
                        modal_ttype_group_yes_val = record['modal_ttype_group_yes_val']
                        modal_ttype_copen_yes_val = record['modal_ttype_copen_yes_val']
                        modal_ttype_cticket_yes_val = record['modal_ttype_cticket_yes_val']
                        modal_ttype_substatus_yes_val = record['modal_ttype_substatus_yes_val']
                        modal_ttype_group_no_val = record['modal_ttype_group_no_val']
                        modal_ttype_copen_no_val = record['modal_ttype_copen_no_val']
                        modal_ttype_cticket_no_val = record['modal_ttype_cticket_no_val']
                        modal_ttype_substatus_no_val = record['modal_ttype_substatus_no_val']
                        modal_ttype_group_na_val = record['modal_ttype_group_na_val']
                        modal_ttype_copen_na_val = record['modal_ttype_copen_na_val']
                        modal_ttype_cticket_na_val = record['modal_ttype_cticket_na_val']
                        modal_ttype_substatus_na_val = record['modal_ttype_substatus_na_val']

                        TGMobj = TaskGroupManager(tmgrgp_display_order=task_order_val, tmgrgp_task_id=task_id_val, tmgrgp_group_id = groupId,
                                            tg_task_assigned_to_id=task_assign_to_val, tg_task_due_date=task_due_date_val,
                                            tg_task_type=task_type_val, tg_task_note=task_note_val,
                                            tg_task_dependency=task_dependency_val, tg_task_depend_order=task_dependency_order_val,
                                            tg_ttype_group_yes_id=modal_ttype_group_yes_val, tg_ttype_copen_yes=modal_ttype_copen_yes_val,
                                            tg_ttype_cticket_yes=modal_ttype_cticket_yes_val, tg_ttype_substatus_yes_id=modal_ttype_substatus_yes_val,
                                            tg_ttype_group_no_id=modal_ttype_group_no_val, tg_ttype_copen_no=modal_ttype_copen_no_val,
                                            tg_ttype_cticket_no=modal_ttype_cticket_no_val, tg_ttype_substatus_no_id=modal_ttype_substatus_no_val,
                                            tg_ttype_group_na_id=modal_ttype_group_na_val, tg_ttype_copen_na=modal_ttype_copen_na_val,
                                            tg_ttype_cticket_na=modal_ttype_cticket_na_val, tg_ttype_substatus_na_id=modal_ttype_substatus_na_val,
                                            tg_task_created_by_id=request.user.id)
                        TGMobj.save()
                except IntegrityError:
                    transaction.rollback()

        response_data['response'] = 'Success'
    else:
        response_data['response'] = 'No Record Found'

    return HttpResponse(response_data)

#Save Task Manager on Table Through Group ID End#



#Get Task Manager Database Records By Group ID Start#
@csrf_exempt
def getTaskManagerByTaskgroupId(request):
    if request.is_ajax() and request.method == 'POST':
        taskgroup_id = request.POST.get('group_id')
        if taskgroup_id:
            result = TaskGroupManager.objects.filter(tmgrgp_group_id=taskgroup_id).order_by('tmgrgp_display_order')
            response_data = {}
            try:
                response_data['response'] = serializers.serialize('json', result)
            except:
                response_data['response'] = ''
            return JsonResponse(response_data)

#Get Task Manager Database Records By Group ID End#

#Task Group Restrict To Start#

@active_user_required
def saveRestrictTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        all_groups = request.POST.getlist('tgr_group')
        all_orgs = request.POST.getlist('tgr_org')

        task_group_id = request.POST.get('task_group_id')

        if 'tgr_org' in request.POST and 'tgr_group' in request.POST :
            if request.POST['tgr_org'] != '':
                tgr_type_is_org = 1
                tgr_type_is_group = 0
                tgr_group_id = ''
                tgr_group = '' 
                    
                if all_orgs:
                    if 'multiselect-all' in all_orgs:
                        all_orgs.remove('multiselect-all')
                for one_org in all_orgs: 
                    tgr_group_or_org_name = Organization.objects.values_list('org_name', flat=True).get(pk=one_org)
                    obj = TaskGroupRestrict(tgr_task_group_id= task_group_id, tgr_org_id=one_org, tgr_group_or_org_name=tgr_group_or_org_name,tgr_type_is_group=tgr_type_is_group,tgr_type_is_org=tgr_type_is_org,tgr_group_id=tgr_group)
                    obj.save()  

            if request.POST['tgr_group'] != '':
                tgr_type_is_group = 1  
                tgr_type_is_org = 0
                tgr_org_id = ''
                tgr_org = '' 

                if all_groups:
                    if 'multiselect-all' in all_groups:
                        all_groups.remove('multiselect-all')
                for one_group in all_groups: 
                    tgr_group_or_org_name = Group.objects.values_list('group_display_name', flat=True).get(pk=one_group)
                    obj = TaskGroupRestrict(tgr_task_group_id= task_group_id, tgr_org_id=tgr_org, tgr_group_or_org_name=tgr_group_or_org_name,tgr_type_is_group=tgr_type_is_group,tgr_type_is_org=tgr_type_is_org,tgr_group_id=one_group)
                    obj.save()  
            messages.success(request, 'Request Succeed! Restrict TaskGroup updated.')    
        elif 'tgr_org' in request.POST:
            tgr_type_is_org = 1
            tgr_type_is_group = 0
            tgr_group_id = ''
            tgr_group = '' 
                
            if all_orgs:
                if 'multiselect-all' in all_orgs:
                    all_orgs.remove('multiselect-all')
            for one_org in all_orgs: 
                tgr_group_or_org_name = Organization.objects.values_list('org_name', flat=True).get(pk=one_org)
                obj = TaskGroupRestrict(tgr_task_group_id= task_group_id, tgr_org_id=one_org, tgr_group_or_org_name=tgr_group_or_org_name,tgr_type_is_group=tgr_type_is_group,tgr_type_is_org=tgr_type_is_org,tgr_group_id=tgr_group)
                obj.save()
            messages.success(request, 'Request Succeed! Restrict TaskGroup updated.') 

        elif 'tgr_group' in request.POST:
            tgr_type_is_group = 1  
            tgr_type_is_org = 0
            tgr_org_id = ''
            tgr_org = '' 

            if all_groups:
                if 'multiselect-all' in all_groups:
                    all_groups.remove('multiselect-all')
            for one_group in all_groups: 
                tgr_group_or_org_name = Group.objects.values_list('group_display_name', flat=True).get(pk=one_group)
                obj = TaskGroupRestrict(tgr_task_group_id= task_group_id, tgr_org_id=tgr_org, tgr_group_or_org_name=tgr_group_or_org_name,tgr_type_is_group=tgr_type_is_group,tgr_type_is_org=tgr_type_is_org,tgr_group_id=one_group)
                obj.save()
            messages.success(request, 'Request Succeed! Restrict TaskGroup updated.')         
        else:    
            messages.error(request, 'Request Failed! Restrict TaskGroup not updated. Please Select any field.')         
   
        try:
            task_group_id = request.POST.get('task_group_id')
            task_group_id = signing.dumps(task_group_id, salt=settings.SALT_KEY)
        except TaskGroupRestrict.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        return redirect(reverse('editTaskGroup') + '?taskGroupId=' + str(task_group_id))
#Task Group Restrict To End#


#Delete Task Group Restrict To Start#
@active_user_required
def deleteRestrictTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    
    # id = request.GET['tgr_id']
    if request.method == 'POST':
        if 'id' in request.POST and request.POST['id']:
            id = request.POST.get('id')
    try:
        # obj = get_object_or_404(TaskGroupRestrict , pk = id)
        obj = TaskGroupRestrict.objects.get(pk=id)
    except Task.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    response_data = {}
    if not obj:
        messages.error(request, 'Request Failed! Restrict TaskGroup not deleted.Please try again.')
        response_data['response'] = 'No Record Found'
        return HttpResponse('error response')
    else:
        obj.tgr_is_delete = 1
        obj.save()
        messages.success(request, 'Request Succeed! Restrict TaskGroup deleted.')
        response_data['response'] = 'Success'
        return HttpResponse('Success response')
        
    return HttpResponse(response_data)

# Delete Task Group Restrict To End#

#Child List Task Group Restrict To Start#
@active_user_required
def childlistTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    task_id = request.GET.get('parent_id')
    id = request.GET.get('task_id')
    t_id = signing.loads(id)
    
    further_group_tasks= TaskGroupManager.objects.values_list('tmgrgp_group', flat=True).filter(tmgrgp_group=t_id)
    for further_group_task in further_group_tasks:
        further_tasks= TaskGroupManager.objects.values_list('tmgrgp_task', flat=True).filter(tmgrgp_group=further_group_task)  

    task_ids =  list(further_tasks)
    for task_id in task_ids:   
        task_names = Task.objects.values_list('task_description', flat=True).filter(pk__in=task_ids)
    
    all_names=  list(task_names)

    # return HttpResponse(str(further_tasks))
    load_sidebar = get_sidebar(request)

    context = {
        'task_id': task_id,
        't_id':t_id,
        'further_group_tasks':further_group_tasks,
        'task_names':all_names,
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Task/child_list_task_group.html', context)

# Child List Task Restrict To End#

#GET ALL TASK GROUP DATA FOR EJ2 GRID
@csrf_exempt
def getAllTaskGroupJson(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    user_id = request.user.id
    org_id = request.user.user_org_id
    global_user_ids = isGlobalUser(request)
    # if request.user.user_type_slug != global_user_ids:
    allTaskGroups = TaskGroup.objects.filter(taskgroup_is_delete=0).filter(task_group_org_id=org_id)
    # else:
    #     allTaskGroups = TaskGroup.objects.filter(taskgroup_is_delete=0)
    resultArray = []
    for taskGroup in allTaskGroups:
        rid = signing.dumps(taskGroup.taskgroup_id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['taskgroup_id'] = taskGroup.taskgroup_id
        resutlCurrentRecord['action'] = '<a href="Admin_TaskGroupEdit?taskGroupId=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_TaskGroupDel?taskGroupId=' + str(taskGroup.taskgroup_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        resutlCurrentRecord['taskgroup_description'] = taskGroup.taskgroup_description
        resultArray.append(resutlCurrentRecord)
    
    return HttpResponse(json.dumps(resultArray), content_type="application/json")

#GET TASKS BY GROUP EJ2 GRID JSON
@csrf_exempt
def getTasksByTaskGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    filterString = request.GET.get('$filter')
    taskgroup_id = filterString.split("eq ",1)[1] 
    taskgroup_id = taskgroup_id.strip()
    SQL = '''
        SELECT T.task_description, TGM.*
        ,(
            SELECT TGR.taskgroup_description
            FROM AT_TaskGroup TGR
            WHERE TGR.taskgroup_id = TGM.tg_ttype_group_yes_id
        )AS group_yes
        ,(
            SELECT TGR.taskgroup_description
            FROM AT_TaskGroup TGR
            WHERE TGR.taskgroup_id = TGM.tg_ttype_group_no_id
        )AS group_no
        ,(
            SELECT TGR.taskgroup_description
            FROM AT_TaskGroup TGR
            WHERE TGR.taskgroup_id = TGM.tg_ttype_group_na_id
        )AS group_na
        ,(
            SELECT SS.sub_status_text
            FROM AT_SubStatus SS
            WHERE SS.sub_status_id = TGM.tg_ttype_substatus_yes_id
        )AS substatus_yes
        ,(
            SELECT SS.sub_status_text
            FROM AT_SubStatus SS
            WHERE SS.sub_status_id = TGM.tg_ttype_substatus_no_id
        )AS substatus_no
        ,(
            SELECT SS.sub_status_text
            FROM AT_SubStatus SS
            WHERE SS.sub_status_id = TGM.tg_ttype_substatus_na_id
        )AS substatus_na
        FROM AT_TaskGroupManager TGM
        INNER JOIN AT_Task T ON T.task_id = TGM.tmgrgp_task_id
        INNER JOIN AT_TaskGroup TG ON TG.taskgroup_id = TGM.tmgrgp_group_id
        WHERE TGM.tmgrgp_group_id = %s
    '''
    allGroupTasks = TaskGroupManager.objects.raw(SQL,[taskgroup_id])
    groupMembersCount = len(list(allGroupTasks))

    resultArray = []
    for groupTask in allGroupTasks:
        resutlCurrentRecord = {}
        process_options_str = ''
        if groupTask.group_yes:
            process_options_str += "Add Task Group On Yes: <b>"+groupTask.group_yes+"</b><br>"
        if groupTask.group_no:
            process_options_str += "Add Task Group On No: <b>"+groupTask.group_no+"</b><br>"
        if groupTask.group_na:
            process_options_str += "Add Task Group On N/A: <b>"+groupTask.group_na+"</b><br>"
        if groupTask.substatus_yes:
            process_options_str += "Change Substatus On Yes: <b>"+groupTask.substatus_yes+"</b><br>"
        if groupTask.substatus_no:
            process_options_str += "Change Substatus On No: <b>"+groupTask.substatus_no+"</b><br>"
        if groupTask.substatus_na:
            process_options_str += "Change Substatus On N/A: <b>"+groupTask.substatus_na+"</b><br>"

        resutlCurrentRecord['task_description'] = groupTask.task_description
        resutlCurrentRecord['process_options'] = process_options_str
        resultArray.append(resutlCurrentRecord)
    mainArray = {}
    mainArray['results'] = resultArray
    mainArray['__count'] = groupMembersCount
    externalArray = {}
    externalArray['d'] = mainArray

    return HttpResponse(json.dumps(externalArray), content_type="application/json")

#Task Restrict To Start#

@active_user_required
def saveRestrictTask(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        all_groups = request.POST.getlist('tr_group')
        all_orgs = request.POST.getlist('tr_org')

        task_id = request.POST.get('task_id')

        if 'tr_org' in request.POST and 'tr_group' in request.POST :
            if request.POST['tr_org'] != '':
                tr_type_is_org = 1
                tr_type_is_group = 0
                tr_group_id = ''
                tr_group = '' 
                    
                if all_orgs:
                    if 'multiselect-all' in all_orgs:
                        all_orgs.remove('multiselect-all')
                for one_org in all_orgs: 
                    tr_group_or_org_name = Organization.objects.values_list('org_name', flat=True).get(pk=one_org)
                    obj = TaskRestrict(tr_task_id= task_id, tr_org_id=one_org, tr_group_or_org_name=tr_group_or_org_name,tr_type_is_group=tr_type_is_group,tr_type_is_org=tr_type_is_org,tr_group_id=tr_group)
                    obj.save()  

            if request.POST['tr_group'] != '':
                tr_type_is_group = 1  
                tr_type_is_org = 0
                tr_org_id = ''
                tr_org = '' 

                if all_groups:
                    if 'multiselect-all' in all_groups:
                        all_groups.remove('multiselect-all')
                for one_group in all_groups: 
                    tr_group_or_org_name = Group.objects.values_list('group_display_name', flat=True).get(pk=one_group)
                    obj = TaskRestrict(tr_task_id= task_id, tr_org_id=tr_org, tr_group_or_org_name=tr_group_or_org_name,tr_type_is_group=tr_type_is_group,tr_type_is_org=tr_type_is_org,tr_group_id=one_group)
                    obj.save()  
            messages.success(request, 'Request Succeed! Restrict Task updated.')    
        elif 'tr_org' in request.POST:
            tr_type_is_org = 1
            tr_type_is_group = 0
            tr_group_id = ''
            tr_group = '' 
                
            if all_orgs:
                if 'multiselect-all' in all_orgs:
                    all_orgs.remove('multiselect-all')
            for one_org in all_orgs: 
                tr_group_or_org_name = Organization.objects.values_list('org_name', flat=True).get(pk=one_org)
                obj = TaskRestrict(tr_task_id= task_id, tr_org_id=one_org, tr_group_or_org_name=tr_group_or_org_name,tr_type_is_group=tr_type_is_group,tr_type_is_org=tr_type_is_org,tr_group_id=tr_group)
                obj.save()
            messages.success(request, 'Request Succeed! Restrict Task updated.') 

        elif 'tr_group' in request.POST:
            tr_type_is_group = 1  
            tr_type_is_org = 0
            tr_org_id = ''
            tr_org = '' 

            if all_groups:
                if 'multiselect-all' in all_groups:
                    all_groups.remove('multiselect-all')
            for one_group in all_groups: 
                tr_group_or_org_name = Group.objects.values_list('group_display_name', flat=True).get(pk=one_group)
                obj = TaskRestrict(tr_task_id= task_id, tr_org_id=tr_org, tr_group_or_org_name=tr_group_or_org_name,tr_type_is_group=tr_type_is_group,tr_type_is_org=tr_type_is_org,tr_group_id=one_group)
                obj.save()
            messages.success(request, 'Request Succeed! Restrict Task updated.')         
        else:    
            messages.error(request, 'Request Failed! Restrict Task not updated. Please Select any field.')         
   
        try:
            task_id = request.POST.get('task_id')
            task_id = signing.dumps(task_id, salt=settings.SALT_KEY)
        except TaskRestrict.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        return redirect(reverse('editTask') + '?taskID=' + str(task_id))
#Task Restrict To End#

#Delete Task Restrict To Start#
@active_user_required
def deleteRestrictTask(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'id' in request.POST and request.POST['id']:
            id = request.POST.get('id')
    try:
        # obj = get_object_or_404(TaskGroupRestrict , pk = id)
        obj = TaskRestrict.objects.get(pk=id)
    except Task.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    response_data = {}
    if not obj:
        messages.error(request, 'Request Failed! Restrict Task not deleted.Please try again.')
        response_data['response'] = 'No Record Found'
        return HttpResponse('error response')
    else:
        obj.tr_is_delete = 1
        obj.save()
        messages.success(request, 'Request Succeed! Restrict Task deleted.')
        response_data['response'] = 'Success'
        return HttpResponse('Success response')
        
    return HttpResponse(response_data)

# Delete Task Restrict To End#