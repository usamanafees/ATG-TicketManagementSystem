from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Organization, Client, DashboardSettings
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from datetime import datetime
import calendar
from itrak.views.Load import *
from itrak.views.Email import *
from django.db.models import Count
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
import pytz
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
@active_user_required
def tickets(request):
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
    }
    return render(request, 'itrak/EmailNotification/email_ticket.html', context)

@active_user_required
def ticketsListAll(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    ticket_roles = TicketsRoles.objects.filter(t_is_default=0)
    tickets_actions = TicketsActions.objects.all()
    permit = TicketsEmailNotificationPermissions.objects.filter(t_org_id=org_id)
    permis = []
    for p in permit:
        permis.append(str(p.t_email_role_id)+' '+str(p.t_email_action_id))
    # return HttpResponse(permis)
    permitted_clients=[]
    clients = Client.objects.all()
    for client in clients:
        check = ClientEmailNotificationPermission.objects.filter(client_id=client.client_id).values_list('client_id',flat=True).distinct()
        print(check)
        if(check):
            permitted_clients.append(check[0])
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'ticket_roles': ticket_roles,
        'tickets_actions': tickets_actions,
        'permis': permis,
        'clients': clients,
        'permitted_clients': permitted_clients,
    }
    return render(request, 'itrak/EmailNotification/tickets_list_all.html', context)

@csrf_exempt
def getModalActionDetailById(request):
    if request.method == 'POST':
        user_id = request.user.id
        org_id = request.user.user_org_id
        role = TicketsRoles.objects.filter(t_role_id=request.POST.get('role_id')).first()
        tickets_actions = TicketsActions.objects.all()
        permit = TicketsEmailNotificationPermissions.objects.filter(t_org_id=org_id).filter(t_email_role_id=role.t_role_id).values_list('t_email_action_id',flat=True)
        # return HttpResponse(permit)
        context = {
            'role': role,
            'tickets_actions': tickets_actions,
            'permit': permit,
        }
        return render(request, 'itrak/EmailNotification/ticket_permission_modal.html', context)

@active_user_required
def updateTicketsEmailPermission(request):
    # return HttpResponse()
    if request.method == 'POST':
        actions = request.POST.getlist('action_name[]')
        role = TicketsRoles.objects.filter(t_name=request.POST.get('role_name')).first()
        TicketsEmailNotificationPermissions.objects.filter(t_email_role_id=role.t_role_id).delete()
        if len(actions) > 0:
            for a in actions:
                action = TicketsActions.objects.filter(t_action_name=a).first()
                permit = TicketsEmailNotificationPermissions(t_email_role_id=role.t_role_id,t_email_action_id=action.t_action_id,t_email_created_by_id=request.user.id,t_email_modified_by_id=request.user.id, t_org_id=request.user.user_org_id)
                permit.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect(request.META['HTTP_REFERER'])
            # return HttpResponse(role.t_role_id)
    else:
        messages.error(request, 'Request Failed! Check atleast one checkbox!')
        return redirect(request.META['HTTP_REFERER'])
        
@active_user_required
def ticketsDefaultDistribution(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    ticket_roles = TicketsRoles.objects.all()
    tickets_actions = TicketsActions.objects.all()
    # permit = TicketsEmailNotificationPermissions.objects.all()
    permit = TicketsEmailNotificationPermissions.objects.filter(t_org_id=org_id)
    permis = []
    for p in permit:
        permis.append(str(p.t_email_role_id)+' '+str(p.t_email_action_id))
    # return HttpResponse(permis)
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'ticket_roles': ticket_roles,
        'tickets_actions': tickets_actions,
        'permis': permis,
    }
    return render(request, 'itrak/EmailNotification/tickets_default_distribution.html', context)

@csrf_exempt
def editEmailMobileNotifications(request):
    if request.method == 'POST':
        tickets_actions = TicketsActions.objects.all()
        client = Client.objects.get(client_id=request.POST.get('client_id'))
        email_permit = ClientEmailNotificationPermission.objects.filter(client_id=request.POST.get('client_id'),email=1).values_list('t_action_id',flat=True)
        mobile_permit = ClientEmailNotificationPermission.objects.filter(client_id=request.POST.get('client_id'),mobile=1).values_list('t_action_id',flat=True)
        context = {
            'client': client,
            'email_permit': email_permit,
            'mobile_permit': mobile_permit,
            'tickets_actions': tickets_actions,
        }
        return render(request, 'itrak/EmailNotification/client_email_mobile_notification_modal.html', context)

def updateEmailMobileNotifications(request):
    if request.method == 'POST':
        ClientEmailNotificationPermission.objects.filter(client_id=request.POST.get('client_id')).delete()
        for email in request.POST.getlist('email'):
                permit_obj = ClientEmailNotificationPermission(client_id=request.POST.get('client_id'), email=1, t_action_id=email)
                permit_obj.save()
        for mobile in request.POST.getlist('mobile'):
                permit_obj = ClientEmailNotificationPermission(client_id=request.POST.get('client_id'), mobile=1, t_action_id=mobile)
                permit_obj.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect('ticketsListAll')
@csrf_exempt
def deleteEmailMobileNotifications(request):
    if request.method == 'POST':
        ClientEmailNotificationPermission.objects.filter(client_id=request.POST.get('client_id')).delete()        
        messages.success(request, 'Request Succeed! Record successfully deleted.')
        return redirect('ticketsListAll')

@active_user_required
def tasks(request):
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
    }
    return render(request, 'itrak/EmailNotification/email_tasks.html', context)

@active_user_required
def tasksDefaultDistribution(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    task_roles = TasksRole.objects.all()
    task_actions = TasksAction.objects.all()
    # permit = TasksEmailNotificationPermission.objects.all()
    permit = TasksEmailNotificationPermission.objects.filter(t_org_id=org_id)

    permis = []
    for p in permit:
        permis.append(str(p.t_email_role_id)+' '+str(p.t_email_action_id))
    # return HttpResponse(permis)
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'task_roles': task_roles,
        'task_actions': task_actions,
        'permis': permis,
    }
    return render(request, 'itrak/EmailNotification/tasks_default_distribution.html', context)

@csrf_exempt
def getModalTaskEmailPermissionsByID(request):
    if request.method == 'POST':
        user_id = request.user.id
        org_id = request.user.user_org_id
        role = TasksRole.objects.filter(task_role_id=request.POST.get('role_id')).first()
        task_actions = TasksAction.objects.all()
        permit = TasksEmailNotificationPermission.objects.filter(t_org_id=org_id).filter(t_email_role_id=role.task_role_id).values_list('t_email_action_id',flat=True)
        # return HttpResponse(permit)
        context = {
            'role': role,
            'task_actions': task_actions,
            'permit': permit,
        }
        return render(request, 'itrak/EmailNotification/task_permission_modal.html', context)


def updateTasksEmailPermission(request):
    # return HttpResponse()
    if request.method == 'POST':
        actions = request.POST.getlist('action_name[]')
        role = TasksRole.objects.filter(task_name=request.POST.get('role_name')).first()
        TasksEmailNotificationPermission.objects.filter(t_email_role_id=role.task_role_id).delete()
        if len(actions) > 0:
            for a in actions:
                action = TasksAction.objects.filter(task_action_name=a).first()
                permit = TasksEmailNotificationPermission(t_email_role_id=role.task_role_id,t_email_action_id=action.task_action_id,t_email_created_by_id=request.user.id,t_email_modified_by_id=request.user.id, t_org_id=request.user.user_org_id)
                permit.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect(request.META['HTTP_REFERER'])
            # return HttpResponse(role.t_role_id)
    else:
        messages.error(request, 'Request Failed! Check atleast one checkbox!')
        return redirect(request.META['HTTP_REFERER'])

@active_user_required
def addCustomMessages(request):
    # return HttpResponse()
    load_sidebar = get_sidebar(request)
    events = CustomMessagesEvent.objects.all()
    tokens = CustomMessagesToken.objects.all()
    subject_tokens =  get_subject_tokens(request, 1)
    message_tokens = get_message_tokens(request, 0)
    context = {
        'sidebar': load_sidebar,
        'events': events,
        'subject_tokens':subject_tokens,
        'message_tokens':message_tokens,
    }
    return render(request, 'itrak/EmailNotification/custom_messages.html', context)


@active_user_required
def showCustomMessages(request):
    
    
    # is_exist = CustomMessage.objects.filter(cm_event_id=2).exists()
    # if is_exist == True:
    #     subject = getSubjectReplaceText(2,'updated')
    #     message = getMessageReplaceText(2,'updated')
    # else:
    #     subject = getSubjectReplaceText(2,'default')
    #     message = getMessageReplaceText(2,'default')
    event_id = request.POST.get('event_id')

    is_exist = CustomMessage.objects.filter(cm_event_id=event_id).exists()
    if is_exist == True:
        subject= CustomMessage.objects.values_list('cm_subject', flat=True).get(cm_event_id=event_id)
        message = CustomMessage.objects.values_list('cm_message', flat=True).get(cm_event_id=event_id)
        subject_slug = json.loads(subject)
        message_slug = json.loads(message)
    else:
        subject=CustomMessagesEvent.objects.values_list('cme_subject_slug', flat=True).get(pk=event_id)
        message=CustomMessagesEvent.objects.values_list('cme_message_slug', flat=True).get(pk=event_id)
        subject_slug = json.loads(subject)
        message_slug = json.loads(message)
        
    try:
        response_data = { 'subject_slug': subject_slug, 'message_slug':message_slug,'event_id_is_exist': is_exist}
        return JsonResponse(response_data)
    except:
        response_data = { 'response': ''}

   

    # try:
    #     response_data['response'] = serializers.serialize('json', subject_slug)
    # except:
    #     response_data['response'] = ''
    # return JsonResponse(response_data)

@active_user_required
def saveCustomMessages(request):
    # return HttpResponse()
    
    event_id = request.POST.get('custom_event')
   
    
    if event_id != '':
        event_name = CustomMessagesEvent.objects.get(pk=event_id)
        subject = request.POST.get('subject_textarea')
        message = request.POST.get('message_textarea')

        if not CustomMessage.objects.filter(cm_event_id=event_id).exists():
            obj = CustomMessage(cm_event_id=event_id, cm_event_name=event_name, cm_subject=json.dumps(subject),
                                    cm_message=json.dumps(message))
            obj.save()
            messages.success(request, 'Request Succeed! Custom Message added.')
            return redirect('addCustomMessages')

        else:
            # return HttpResponse(event_name)
            obj = CustomMessage.objects.filter(cm_event_id=event_id).first()
            obj.cm_event_id = event_id
            obj.cm_event_name = str(event_name)
            obj.cm_subject = json.dumps(subject)
            obj.cm_message = json.dumps(message)

        obj.save()
        messages.success(request, 'Request Succeed! Custom Message added.')
        return redirect('addCustomMessages')        

    else:
        messages.error(request, 'Request Failed! Custom Message not added.')
        return redirect('addCustomMessages')
        
        

