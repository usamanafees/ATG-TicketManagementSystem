from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Organization, Client, BusinessRules
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.utils import timezone
import pytz
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from django.core import signing
import calendar
from collections import OrderedDict
# import cronjobs
# import datetime
from functools import wraps

# Create your views here.

#Custom Decorator Start#

user_login_required = user_passes_test(lambda user: user.is_active, login_url='/') #Here user_passes_test decorator designates the user is active.

# def active_user_required(view_func):
#     decorated_view_func = login_required(user_login_required(view_func))
#     return decorated_view_func
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


#Business Rules Add Request Start#

@active_user_required
def addBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    print(org_id)
    if request.user.id != 3108:
        organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1).filter(org_id=org_id)
        for org in organizations:
            organizations = org.org_id
        departments = Department.objects.filter(d_is_delete=0).filter(d_is_active=1).filter(user_org_id=org_id)
        clients = Client.objects.filter(cl_is_delete=0)
        ticketTypes = get_tickettype_data(request)
        priorities = Priority.objects.filter(prior_is_delete=0).filter(user_org_id=org_id)
        substatus = SubStatus.objects.filter(sstatus_is_delete=0).filter(ss_org_id=org_id)
        users = User.objects.filter(user_type=0).filter(is_delete=0).filter(user_org_id=org_id)
    else:
        organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1)
        departments = Department.objects.filter(d_is_delete=0).filter(d_is_active=1)
        clients = Client.objects.filter(cl_is_delete=0)
        ticketTypes = get_tickettype_data(request)
        priorities = Priority.objects.filter(prior_is_delete=0)
        substatus = SubStatus.objects.filter(sstatus_is_delete=0)
        users = User.objects.filter(user_type=0).filter(is_delete=0)
    # agents = User.objects.filter(is_delete=0)

    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'organizations': organizations,
        'departments' : departments,
        'clients': clients,
        'ticketTypes': ticketTypes,
        'priorities': priorities,
        'substatus': substatus,
        'users': users,
        'range1':range(0,10),
        'range': range(10,60),
        'user_id':user_id,
    }

    return render(request, 'itrak/BusinessRules/business_rules_add.html', context)
#Business Rules Add Request End#
@active_user_required
def saveBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'BR_organizations' in request.POST and request.POST['BR_organizations']:
            BR_organizations = request.POST.get('BR_organizations')
        else:
            BR_organizations = ''
        print(BR_organizations)
        if 'BR_departments' in request.POST and request.POST['BR_departments']:
            BR_departments = request.POST.get('BR_departments')
        else:
            BR_departments = ''

        if 'BR_clients' in request.POST:
            BR_clients = request.POST.get('BR_clients')
        else:
            BR_clients = ''

        if 'ticket_type' in request.POST:
            ticket_type = request.POST.get('ticket_type')
        else:
            ticket_type = ''

        if 'subtype1' in request.POST:
            subtype1 = request.POST.get('subtype1')
        if 'subtype2' in request.POST:
            subtype2 = request.POST.get('subtype2')
        if 'subtype3' in request.POST:
            subtype3 = request.POST.get('subtype3')
        if 'subtype4' in request.POST:
            subtype4 = request.POST.get('subtype4')
        if 'BR_priorities' in request.POST:
            BR_priorities = request.POST.get('BR_priorities')
        else:
            BR_priorities = ''

        if 'assigned_to' in request.POST:
            assigned_to = request.POST.get('assigned_to')

        if not BR_organizations:
            org_name = ''
        else:
            org_name = Organization.objects.get(pk=BR_organizations)

        if not BR_departments:
            dep_name = ''
        else:
            dep_name = Department.objects.get(pk=BR_departments)

        if not BR_clients:
            client_name = ''
        else:
            client_name = Client.objects.get(pk=BR_clients)

        if not BR_priorities:
            priority_name = ''
        else:
            priority_name = Priority.objects.get(pk=BR_priorities)

        display_name = User.objects.values_list('display_name', flat=True).get(pk=assigned_to)

        # users = User.objects.filter(is_delete=0)
        # if users.id == assigned_to:
        #     display_name= users.display_name



        start_hour = request.POST.get('inp_starthour') if 'inp_starthour' in request.POST else '12'
        start_minutes = request.POST.get('inp_startminutes') if 'inp_startminutes' in request.POST else '00'
        start_AM_PM = request.POST.get('inp_startAMPM') if 'inp_startAMPM' in request.POST else 'AM'
        end_hour = request.POST.get('inp_endhour') if 'inp_endhour' in request.POST else '11'
        end_minutes = request.POST.get('inp_endminutes') if 'inp_endminutes' in request.POST else '30'
        end_AM_PM = request.POST.get('inp_endAMPM') if 'inp_endAMPM' in request.POST else 'PM'
        monday = request.POST.get('inp_Monday') if 'inp_Monday' in request.POST else ''
        tuesday = request.POST.get('inp_Tuesday') if 'inp_Tuesday' in request.POST else ''
        wednesday = request.POST.get('inp_Wednesday') if 'inp_Wednesday' in request.POST else ''
        thursday = request.POST.get('inp_Thursday') if 'inp_Thursday' in request.POST else ''
        friday = request.POST.get('inp_Friday') if 'inp_Friday' in request.POST else ''
        saturday = request.POST.get('inp_Saturday') if 'inp_Saturday' in request.POST else ''
        sunday = request.POST.get('inp_Sunday') if 'inp_Sunday' in request.POST else ''

        # start_24_hours and end_24_hours fields
        db_start_time = start_hour +':'+ start_minutes+' '+ start_AM_PM
        db_end_time = end_hour +':'+ end_minutes+' '+end_AM_PM
        db_start_time_only = start_hour +':'+ start_minutes
        db_end_time_only = end_hour +':'+ end_minutes
        #24Hour Format
        start_time = get24HourFormattedTime(db_start_time)
        end_time = get24HourFormattedTime(db_end_time)
        if start_AM_PM == 'PM':
            starttime_24_hrs = datetime.strptime(start_time,'%H:%M %p').strftime('%H:%M')
        else:
            starttime_24_hrs = start_time 
        if end_AM_PM == 'PM':
            endtime_24_hrs = datetime.strptime(end_time,'%H:%M %p').strftime('%H:%M')    
        else:
            endtime_24_hrs = end_time 

        obj = BusinessRules(br_org_name=org_name, br_dep_name=dep_name, br_client_name=client_name, br_ticket_type_id=ticket_type, br_ticket_subtype1_id=subtype1, br_ticket_subtype2_id=subtype2, br_ticket_subtype3_id=subtype3, br_ticket_subtype4_id=subtype4, br_priority_name=priority_name, start_hour=start_hour, start_minutes=start_minutes, start_AM_PM=start_AM_PM, end_hour=end_hour, end_minutes=end_minutes, end_AM_PM=end_AM_PM, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, sunday=sunday, br_ticket_assign_to_id=assigned_to, br_ticket_assign_to_name=display_name, br_client_id=BR_clients, br_dep_id=BR_departments , br_org_id=BR_organizations, br_priority_id=BR_priorities, start_24_hours=starttime_24_hrs, end_24_hours=endtime_24_hrs )
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! BusinessRules added.')
        return redirect('listBusinessRules')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! BusinessRules cannot be added.Please try again.')
        return redirect('listBusinessRules')

@active_user_required
def listBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/BusinessRules/business_rules_list.html', context)


#Datatable Code Start Here#
class BusinessRulesListJson(BaseDatatableView):
    # The model we're going to show
    model = BusinessRules

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
        if self.request.user.id != 3108:
            org_id = self.request.user.user_org_id
            return BusinessRules.objects.filter(br_is_delete=0).filter(br_org_id=org_id)
        else:
            return BusinessRules.objects.filter(br_is_delete=0)
        # return BusinessRules.objects
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        user_id = self.request.user.id
        if column == 'submit_day':

            monday = BusinessRules.objects.values_list('monday', flat=True).get(pk=str(row.br_id))
            tuesday = BusinessRules.objects.values_list('tuesday', flat=True).get(pk=str(row.br_id))
            wednesday = BusinessRules.objects.values_list('wednesday', flat=True).get(pk=str(row.br_id))
            thursday = BusinessRules.objects.values_list('thursday', flat=True).get(pk=str(row.br_id))
            friday = BusinessRules.objects.values_list('friday', flat=True).get(pk=str(row.br_id))
            saturday = BusinessRules.objects.values_list('saturday', flat=True).get(pk=str(row.br_id))
            sunday = BusinessRules.objects.values_list('sunday', flat=True).get(pk=str(row.br_id))

            if monday:
                monday_val = 'Mon'
            else:
                monday_val = ''
            if tuesday:
                tuesday_val = 'Tues'
            else:
                tuesday_val = ''
            if wednesday:
                wednesday_val = 'Wed'
            else:
                wednesday_val = ''
            if thursday:
                thursday_val = 'Thurs'
            else:
                thursday_val = ''
            if friday:
                friday_val = 'Fri'
            else:
                friday_val = ''
            if saturday:
                saturday_val = 'Sat'
            else:
                saturday_val = ''
            if sunday:
                sunday_val = 'Sun'
            else:
                sunday_val = ''

            temp = monday_val+' '+tuesday_val+' '+wednesday_val+' '+thursday_val+' '+friday_val+' '+saturday_val+' '+sunday_val;
            return temp

        if column == 'modified_at':
            local_dt = row.br_modified_at
            # BusinessRules.objects.values_list('br_modified_at', flat=True).get(pk=rid)
            return datetime.strptime(str(local_dt), '%Y-%m-%d').strftime('%m/%d/%Y')

        if column == 'is_active':
            # activee= BusinessRules.objects.filter(br_is_active=1)
            active = BusinessRules.objects.values_list('br_is_active', flat=True).get(pk=str(row.br_id))
            if active:
                return '<i class="fa fa-check" style="color:green"></i>'
            else:
                return ''

        if column == 'submit_time':

            start_hour = BusinessRules.objects.values_list('start_hour', flat=True).get(pk=str(row.br_id))
            start_minutes = BusinessRules.objects.values_list('start_minutes', flat=True).get(pk=str(row.br_id))
            start_AM_PM = BusinessRules.objects.values_list('start_AM_PM', flat=True).get(pk=str(row.br_id))
            end_hour = BusinessRules.objects.values_list('end_hour', flat=True).get(pk=str(row.br_id))
            end_minutes = BusinessRules.objects.values_list('end_minutes', flat=True).get(pk=str(row.br_id))
            end_AM_PM = BusinessRules.objects.values_list('end_AM_PM', flat=True).get(pk=str(row.br_id))

            temp = start_hour + ':' + start_minutes + ' ' + start_AM_PM + ' and ' + end_hour + ':' + end_minutes + ' ' + end_AM_PM;
            return temp

        if column == 'action':
            rid = signing.dumps(row.br_id)
            # escape HTML for security reasons
            return '<a href="Admin_BusinessRulesEdit?br_id=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_BusinessRulesDel?br_id=' + str(row.br_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        else:
            return super(BusinessRulesListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(br_org_name__icontains=search) | Q(br_dep_name__icontains=search) | Q(br_client_name__icontains=search))
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
@active_user_required
def editBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('br_id')
    try:
        try:
            br_id = signing.loads(id)
        except signing.BadSignature:
            return render_to_response('itrak/page-404.html')
        data = BusinessRules.objects.get(pk=br_id)
        org_id = request.user.user_org_id
        user_id = request.user.id
        print(org_id)
        if request.user.id != 3108:
            organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1).filter(org_id=org_id)
            for org in organizations:
                organizations = org.org_id
            departments = Department.objects.filter(d_is_delete=0).filter(d_is_active=1).filter(user_org_id=org_id)
            clients = Client.objects.filter(cl_is_delete=0)
            ticketTypes = get_tickettype_data(request)
            tickettype= get_tickettype_data(request)
            TicketSubTypes1 = TicketType.objects.filter(parent_id=data.br_ticket_type_id).filter(ttype_is_delete=0)
            TicketSubTypes2 = TicketType.objects.filter(parent_id=data.br_ticket_subtype1_id).filter(ttype_is_delete=0)
            TicketSubTypes3 = TicketType.objects.filter(parent_id=data.br_ticket_subtype2_id).filter(ttype_is_delete=0)
            TicketSubTypes4 = TicketType.objects.filter(parent_id=data.br_ticket_subtype3_id).filter(ttype_is_delete=0)
            priority = Priority.objects.filter(prior_is_delete=0).filter(user_org_id=org_id)
            user = User.objects.filter(user_type=0).filter(is_delete=0).filter(user_org_id=org_id)
            start_minutes = BusinessRules.objects.values_list('start_minutes', flat=True).get(pk=br_id)
            end_minutes = BusinessRules.objects.values_list('end_minutes', flat=True).get(pk=br_id)
        else:
            organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
            departments = Department.objects.filter(d_is_delete=0)
            clients = Client.objects.filter(cl_is_delete=0)
            tickettype= get_tickettype_data(request)
            TicketSubTypes1 = TicketType.objects.filter(parent_id=data.br_ticket_type_id).filter(ttype_is_delete=0)
            TicketSubTypes2 = TicketType.objects.filter(parent_id=data.br_ticket_subtype1_id).filter(ttype_is_delete=0)
            TicketSubTypes3 = TicketType.objects.filter(parent_id=data.br_ticket_subtype2_id).filter(ttype_is_delete=0)
            TicketSubTypes4 = TicketType.objects.filter(parent_id=data.br_ticket_subtype3_id).filter(ttype_is_delete=0)
            priority = Priority.objects.filter(prior_is_delete=0)
            user = User.objects.filter(user_type=0).filter(is_delete=0)
            start_minutes = BusinessRules.objects.values_list('start_minutes', flat=True).get(pk=br_id)
            end_minutes = BusinessRules.objects.values_list('end_minutes', flat=True).get(pk=br_id)

    except BusinessRules.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listBusinessRules')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data,
            'organizations': organizations,
            'departments': departments,
            'clients': clients,
            'tickettypes': tickettype,
            'TicketSubTypes1': TicketSubTypes1,
            'TicketSubTypes2':TicketSubTypes2,
            'TicketSubTypes3':TicketSubTypes3,
            'TicketSubTypes4':TicketSubTypes4,
            'priorities': priority,
            'users': user,
            'start_minutes' : start_minutes,
            'end_mintues' : end_minutes,
            'range': range(0, 60),
            'j':0,
            'user_id':user_id,
        }
        return render(request, 'itrak/BusinessRules/business_rules_edit.html', context)

@active_user_required
def updateBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('br_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = BusinessRules.objects.get(pk=id)
        except BusinessRules.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listBusinessRules')
        else:
            if 'isActive' in request.POST:
                obj.br_is_active = '1'
            else:
                obj.br_is_active = '0'
            if 'org_id' in request.POST:
                org = request.POST.get('org_id')
                if org:
                    obj.br_org_name = Organization.objects.values_list('org_name', flat=True).get(pk=org)
                    obj.br_org_id = request.POST.get('org_id')
                else:
                    obj.br_org_name = ''
                    obj.br_org_id = '' 
            if 'dep_id' in request.POST:
                dep = request.POST.get('dep_id')
                if dep:
                    obj.br_dep_name = Department.objects.values_list('dep_name', flat=True).get(pk=dep)
                    obj.br_dep_id = request.POST.get('dep_id')
                else: 
                    obj.br_dep_name = '' 
                    obj.br_dep_id = ''   

                   
            if 'client_id' in request.POST:
                client = request.POST.get('client_id')
                if client:
                    obj.br_client_name = Client.objects.values_list('client_name', flat=True).get(pk=client)
                    obj.br_client_id = request.POST.get('client_id')
                else:
                    obj.br_client_name= ''
                    obj.br_client_id= ''

            if 'ticket_type' in request.POST:
                obj.br_ticket_type_id = request.POST.get('ticket_type')
            if 'subtype1' in request.POST:
                obj.br_ticket_subtype1_id = request.POST.get('subtype1')
            if 'subtype2' in request.POST:
                obj.br_ticket_subtype2_id = request.POST.get('subtype2')
            if 'subtype3' in request.POST:
                obj.br_ticket_subtype3_id = request.POST.get('subtype3')
            if 'subtype4' in request.POST:
                obj.br_ticket_subtype4_id = request.POST.get('subtype4')
            if 'BR_priorities' in request.POST:
                priority = request.POST.get('BR_priorities')
                if priority:
                    obj.br_priority_id = request.POST.get('BR_priorities')
                    obj.br_priority_name = Priority.objects.values_list('priority_name', flat=True).get(pk=priority)
                else:
                    obj.br_priority_name =''
                    obj.br_priority_id = ''
            if 'assigned_to' in request.POST:
                assigned_to =request.POST.get('assigned_to')
                obj.br_ticket_assign_to_id = request.POST.get('assigned_to')
                obj.br_ticket_assign_to_name = User.objects.values_list('display_name', flat=True).get(pk=assigned_to)

            obj.start_hour = request.POST.get('inp_starthour') if 'inp_starthour' in request.POST else '00'
            obj.start_minutes = request.POST.get('inp_startminutes') if 'inp_startminutes' in request.POST else '00'
            obj.start_AM_PM = request.POST.get('inp_startAMPM') if 'inp_startAMPM' in request.POST else 'AM'
            obj.end_hour = request.POST.get('inp_endhour') if 'inp_endhour' in request.POST else '00'
            obj.end_minutes = request.POST.get('inp_endminutes') if 'inp_endminutes' in request.POST else '00'
            obj.end_AM_PM = request.POST.get('inp_endAMPM') if 'inp_endAMPM' in request.POST else 'PM'
            obj.monday = request.POST.get('inp_Monday') if 'inp_Monday' in request.POST else ''
            obj.tuesday = request.POST.get('inp_Tuesday') if 'inp_Tuesday' in request.POST else ''
            obj.wednesday = request.POST.get('inp_Wednesday') if 'inp_Wednesday' in request.POST else ''
            obj.thursday = request.POST.get('inp_Thursday') if 'inp_Thursday' in request.POST else ''
            obj.friday = request.POST.get('inp_Friday') if 'inp_Friday' in request.POST else ''
            obj.saturday = request.POST.get('inp_Saturday') if 'inp_Saturday' in request.POST else ''
            obj.sunday = request.POST.get('inp_Sunday') if 'inp_Sunday' in request.POST else ''

            # start_24_hours and end_24_hours fields
            db_start_time = obj.start_hour +':'+ obj.start_minutes+' '+ obj.start_AM_PM
            db_end_time = obj.end_hour +':'+ obj.end_minutes+' '+obj.end_AM_PM
            db_start_time_only = obj.start_hour +':'+ obj.start_minutes
            db_end_time_only = obj.end_hour +':'+ obj.end_minutes
            #24Hour Format
            start_time = get24HourFormattedTime(db_start_time)
            end_time = get24HourFormattedTime(db_end_time)
            if obj.start_AM_PM == 'PM':
                starttime_24_hrs = datetime.strptime(start_time,'%H:%M %p').strftime('%H:%M')
            else:
                starttime_24_hrs = start_time 
            if obj.end_AM_PM == 'PM':
                endtime_24_hrs = datetime.strptime(end_time,'%H:%M %p').strftime('%H:%M')    
            else:
                endtime_24_hrs = end_time 

            obj.start_24_hours = starttime_24_hrs 
            obj.end_24_hours = endtime_24_hrs
            
            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Business Rules updated.')
            return redirect('listBusinessRules')
    else:
        messages.error(request, 'Request Failed! Business Rules cannot be updated.Please try again.')
        return redirect('listBusinessRules')

@active_user_required
def deleteBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('br_id')
    try:
        obj = BusinessRules.objects.get(pk=id)
    except BusinessRules.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listBusinessRules')
    else:
        obj.br_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Business Rules deleted.')
        return redirect('listBusinessRules')

@active_user_required
def precedenceBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    user_id = request.user.id
    org_id = request.user.user_org_id
    if user_id != 3108:
        precedence = PrecedenceBusinessRule.objects.filter(user_org_id=org_id).first()
    else:
        precedence = PrecedenceBusinessRule.objects.first() 
    context = {
        'sidebar': load_sidebar,
        'precedence':precedence,
    }
    return render(request, 'itrak/BusinessRules/business_rules_precedence.html', context)

@active_user_required
def savePrecedenceBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    org_id = request.user.user_org_id
    user_id = request.user.id
    if request.method == 'POST':
        if 'pre_class' in request.POST:
            pre_class = request.POST.get('pre_class')
            if pre_class == '':
                pre_class = '9'    
        if 'pre_department' in request.POST:
            pre_department= request.POST.get('pre_department')
            if pre_department == '':
                pre_department = '1'   
        if 'pre_client' in request.POST:
            pre_client = request.POST.get('pre_client')
            if pre_client == '':
                pre_client = '2' 
        if 'pre_tickettype' in request.POST:
            pre_tickettype = request.POST.get('pre_tickettype')
            if pre_tickettype == '':
                pre_tickettype = '3'
        if 'pre_organization' in request.POST:
            pre_organization = request.POST.get('pre_organization')
            if pre_organization == '':
                pre_organization = '4'
        if 'pre_priority' in request.POST:
            pre_priority = request.POST.get('pre_priority')
            if pre_priority == '':
                pre_priority = '5'
        if 'pre_submit_betw' in request.POST:
            pre_submit_betw = request.POST.get('pre_submit_betw')
            if pre_submit_betw == '':
                pre_submit_betw = '6'
        if 'pre_submit_on' in request.POST:
            pre_submit_on = request.POST.get('pre_submit_on')
            if pre_submit_on == '':
                pre_submit_on = '7'

        if not PrecedenceBusinessRule.objects.filter(user_org_id=org_id).exists():
            obj = PrecedenceBusinessRule(pbr_class=pre_class, pbr_dep=pre_department, pbr_client=pre_client,
                                pbr_tickettype=pre_tickettype, pbr_org=pre_organization, pbr_priority=pre_priority,
                                pbr_submit_betw=pre_submit_betw, pbr_submit_on=pre_submit_on, user_org_id=org_id)
            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Precedence Business Rules added.')
            return redirect('precedenceBusinessRules')
        else:
            if user_id != 3108:
                obj = PrecedenceBusinessRule.objects.filter(user_org_id=org_id).first()
            else:
                obj = PrecedenceBusinessRule.objects.first()   
            obj.pbr_class =  pre_class
            obj.pbr_dep =  pre_department
            obj.pbr_client =  pre_client
            obj.pbr_tickettype =  pre_tickettype
            obj.pbr_org =  pre_organization
            obj.pbr_priority =  pre_priority
            obj.pbr_submit_betw =  pre_submit_betw
            obj.pbr_submit_on =  pre_submit_on

            obj.save()
           
            messages.success(request, 'Request Succeed! Precedence Business Rules added.')
            return redirect('precedenceBusinessRules')

    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! BusinessRules cannot be added.Please try again.')
        return redirect('precedenceBusinessRules')

@active_user_required
def substatusBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    user_id = request.user.id
    org_id = request.user.user_org_id
    load_sidebar = get_sidebar(request)
    substatus=SubStatus.objects.filter(sstatus_is_delete=0).filter(ss_org_id=org_id)
    ticketevents=TicketEvent.objects.filter(te_is_delete=0)
    if user_id != 3108:
        substatusBusinessRules=SubstatusBusinessRule.objects.filter(sbr_is_delete=0).filter(sbr_org_id=org_id)
        pauseclockBusinessRules=PauseClockBusinessRule.objects.filter(pcbr_is_delete=0).filter(pcbr_org_id=org_id)
    else:
        substatusBusinessRules=SubstatusBusinessRule.objects.filter(sbr_is_delete=0)
        pauseclockBusinessRules=PauseClockBusinessRule.objects.filter(pcbr_is_delete=0)
        
    context = {
        'sidebar': load_sidebar,
        'substatus':substatus,
        'ticketevents':ticketevents,
        'substatusBusinessRules':substatusBusinessRules,
        'pauseclockBusinessRules':pauseclockBusinessRules,
    }
    return render(request, 'itrak/BusinessRules/business_rules_substatus.html', context)
    
@active_user_required
def saveSubstatusBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    if request.method == 'POST':
        org_id = request.user.user_org_id
        if 'sbr_ticketevent' in request.POST:
            sbr_ticketevent = request.POST.get('sbr_ticketevent')
            total = SubstatusBusinessRule.objects.filter(sbr_org_id=org_id).filter(sbr_is_delete=0).filter(sbr_ticketevent_id = sbr_ticketevent).count()
            if(total !=0):
                messages.error(request, 'Request Failed! Substatus Business Rules already exists.')
                return redirect('substatusBusinessRules')

        if 'sbr_when_substatus_equal' in request.POST:
            sbr_when_substatus_equal= request.POST.get('sbr_when_substatus_equal')
            # total = SubstatusBusinessRule.objects.filter(sbr_when_substatus_equal_id = sbr_when_substatus_equal).count()
            # if(total !=0):
            #     messages.error(request, 'Request Failed! Substatus Business Rules already exists.')
            #     return redirect('substatusBusinessRules')

        if 'sbr_when_substatus_to' in request.POST:
            sbr_when_substatus_to = request.POST.get('sbr_when_substatus_to')
            # total = SubstatusBusinessRule.objects.filter(sbr_when_substatus_to_id = sbr_when_substatus_to).count()
            # if(total !=0):
            #     messages.error(request, 'Request Failed! Substatus Business Rules already exists.')
            #     return redirect('substatusBusinessRules')
                
        if 'sbr_process_order' in request.POST:
            sbr_process_order = request.POST.get('sbr_process_order')

            sbr_ticketevent_name = TicketEvent.objects.get(pk=sbr_ticketevent)
            if sbr_when_substatus_equal == '':
                sbr_when_substatus_equal_name = '-Any Value-'
            else:    
                sbr_when_substatus_equal_name = SubStatus.objects.get(pk=sbr_when_substatus_equal)

            if sbr_when_substatus_to == '':
                sbr_when_substatus_to_name = '-Blank-'
            else:    
                sbr_when_substatus_to_name = SubStatus.objects.get(pk=sbr_when_substatus_to) 

            context = {
                'sidebar': load_sidebar,
            }
        obj = SubstatusBusinessRule(sbr_ticketevent_id=sbr_ticketevent, sbr_when_substatus_equal_id=sbr_when_substatus_equal, sbr_when_substatus_to_id=sbr_when_substatus_to,
                            sbr_process_order=sbr_process_order,sbr_ticketevent_name=sbr_ticketevent_name,sbr_when_substatus_equal_name=sbr_when_substatus_equal_name,sbr_when_substatus_to_name=sbr_when_substatus_to_name, sbr_org_id=org_id)
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Substatus Business Rules added.')
        return redirect('substatusBusinessRules')

    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed!Substatus BusinessRules cannot be added.Please try again.')
        return redirect('substatusBusinessRules')    

@active_user_required
def editSubstatusBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)

    # id = request.GET.get('sbr_id')
    id = request.GET['sbr_id']
    user_id = request.user.id
    org_id = request.user.user_org_id
    try:
        try:
            sbr_id = id
        except signing.BadSignature:
            return render_to_response('itrak/page-404.html')
        data = SubstatusBusinessRule.objects.filter(pk=sbr_id)
        
    except SubstatusBusinessRule.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('substatusBusinessRules')
    else:
        load_sidebar = get_sidebar(request)
        substatus=SubStatus.objects.filter(sstatus_is_delete=0)
        ticketevents=TicketEvent.objects.filter(te_is_delete=0)
        if user_id != 3108:
            substatusBusinessRules=SubstatusBusinessRule.objects.filter(sbr_is_delete=0).filter(sbr_org_id=org_id)
            pauseclockBusinessRules=PauseClockBusinessRule.objects.filter(pcbr_is_delete=0).filter(pcbr_org_id=org_id)
        else:
            substatusBusinessRules=SubstatusBusinessRule.objects.filter(sbr_is_delete=0)
            pauseclockBusinessRules=PauseClockBusinessRule.objects.filter(pcbr_is_delete=0)
        tick_events = SubstatusBusinessRule.objects.values_list('sbr_ticketevent_name', flat=True).get(pk=sbr_id)
        when_substatus_equal_name = SubstatusBusinessRule.objects.values_list('sbr_when_substatus_equal_name', flat=True).get(pk=sbr_id)  
        when_substatus_to_name = SubstatusBusinessRule.objects.values_list('sbr_when_substatus_to_name', flat=True).get(pk=sbr_id)
        process_order = SubstatusBusinessRule.objects.values_list('sbr_process_order', flat=True).get(pk=sbr_id)
        
        context = {
                'data':data,
                'sidebar': load_sidebar,
                'substatus':substatus,
                'ticketevents':ticketevents,
                'substatusBusinessRules':substatusBusinessRules,
                'tick_events':tick_events,
                'when_substatus_equal_name': when_substatus_equal_name,
                'when_substatus_to_name':when_substatus_to_name,
                'process_order':process_order,  
                'pauseclockBusinessRules':pauseclockBusinessRules,
                'temp':sbr_id,
        }
        return render(request, 'itrak/BusinessRules/business_rules_substatus.html', context)

  
@active_user_required
def updateSubstatusBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('sbr_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj  = get_object_or_404(SubstatusBusinessRule , pk = id)
            #  obj = SubstatusBusinessRule.objects.filter(pk=id)
        except SubstatusBusinessRule.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('substatusBusinessRules')
        else:
            if 'sbr_ticketevent' in request.POST:
                obj.sbr_ticketevent_id = request.POST.get('sbr_ticketevent')
            if 'sbr_when_substatus_equal' in request.POST:
                obj.sbr_when_substatus_equal_id = request.POST.get('sbr_when_substatus_equal')
            if 'sbr_when_substatus_to' in request.POST:
                obj.sbr_when_substatus_to_id = request.POST.get('sbr_when_substatus_to')
            if 'sbr_process_order' in request.POST:
                obj.sbr_process_order = request.POST.get('sbr_process_order')
                
            ticketevent = request.POST.get('sbr_ticketevent')
            substatus_equal = request.POST.get('sbr_when_substatus_equal')
            substatus_to = request.POST.get('sbr_when_substatus_to')

            obj.sbr_ticketevent_name = TicketEvent.objects.values_list('te_name', flat=True).get(pk=ticketevent)
            if(substatus_equal == '-1'):
                obj.sbr_when_substatus_equal_name = '-Any Value-'
            else:    
                obj.sbr_when_substatus_equal_name = SubStatus.objects.values_list('sub_status_text', flat=True).get(pk=substatus_equal)

            if(substatus_to == '0'):
                obj.sbr_when_substatus_to_name = '-Blank-'
            else:    
                obj.sbr_when_substatus_to_name = SubStatus.objects.values_list('sub_status_text', flat=True).get(pk=substatus_to)
            
            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Substatus Business Rules updated.')
            return redirect('substatusBusinessRules')
    else:
        messages.error(request, 'Request Failed! Substatus Business Rules cannot be updated.Please try again.')
        return redirect('substatusBusinessRules')      

@active_user_required
def deleteSubstatusBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('sbr_id')
    try:
       obj  = get_object_or_404(SubstatusBusinessRule , pk = id)
    except BusinessRules.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('substatusBusinessRules')
    else:
        obj.sbr_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Substatus Business Rules deleted.')
        return redirect('substatusBusinessRules')        

@active_user_required
def savePauseClockBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.user.user_org_id
        if 'pcbr_substatus_equal' in request.POST:
            pcbr_substatus_equal = request.POST.get('pcbr_substatus_equal')
            total = PauseClockBusinessRule.objects.filter(pcbr_org_id=org_id).filter(pcbr_is_delete = 0).filter(pcbr_substatus_equal_id = pcbr_substatus_equal).count()
            if(total != 0):
                messages.error(request, 'Request Failed! Pause Clock Business Rules already exists.')
                return redirect('substatusBusinessRules')
                    
        pcbr_substatus_equal_name = SubStatus.objects.get(pk=pcbr_substatus_equal) 
        obj = PauseClockBusinessRule(pcbr_substatus_equal_id=pcbr_substatus_equal, pcbr_substatus_equal_name=pcbr_substatus_equal_name, pcbr_org_id=org_id)
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Pause Clock Business Rules added.')
        return redirect('substatusBusinessRules')

    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed!Pause Clock Business Rules cannot be added.Please try again.')
        return redirect('substatusBusinessRules')    

@active_user_required
def deletePauseClockBusinessRules(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET['pcbr_id']
    try:
       obj  = get_object_or_404(PauseClockBusinessRule , pk = id)
    except BusinessRules.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('substatusBusinessRules')
    else:
        obj.pcbr_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Pause Clock Business Rules deleted.')
        return redirect('substatusBusinessRules')       

#Business Rules Auto Assignment Start#
@active_user_required
def autoAssignmentBusinessRules(request,ticketid): 
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    obj = Ticket.objects.get(pk= ticketid)       
    business_ruless = BusinessRules.objects.filter(br_is_active=1).filter(br_is_delete=0).filter(br_org_id=org_id)

    for business_rules in business_ruless:
        if request.method == 'POST':
            # Auto Assignement logic starts
            kwargs = {
                '{0}__{1}'.format('br_is_delete', 'iexact'): 0,
                '{0}__{1}'.format('br_is_active', 'iexact'): 1,
            }
            # if 'dept' in request.POST and request.method == 'POST' and request.POST.get('dept') != '':
            #     dept = request.POST.get('dept')
            #     kwargs.setdefault('ticket_dept_id', dept) 
            if business_rules.br_client_id:
                if obj.ticket_client_id:
                    print(obj.ticket_client_id)
                    client = obj.ticket_client_id
                    kwargs.setdefault('br_client_id', client)
            if business_rules.br_ticket_type_id:               
                if obj.ticket_type_id: 
                    ticket_type = obj.ticket_type_id
                    kwargs.setdefault('br_ticket_type_id', ticket_type)
                    print(obj.ticket_type_id)
            if business_rules.br_ticket_subtype1_id:
                if obj.ticket_subtype1_id:
                    subtype1 = obj.ticket_subtype1_id
                    kwargs.setdefault('br_ticket_subtype1_id', subtype1)
            if business_rules.br_ticket_subtype2_id:        
                if obj.ticket_subtype2_id:
                    subtype2 = obj.ticket_subtype2_id
                    kwargs.setdefault('br_ticket_subtype2_id', subtype2)
            if business_rules.br_ticket_subtype3_id:         
                if obj.ticket_subtype3_id:
                    subtype3 = obj.ticket_subtype3_id
                    kwargs.setdefault('br_ticket_subtype3_id', subtype3)
            if business_rules.br_ticket_subtype4_id:         
                if obj.ticket_subtype4_id:
                    subtype4 = obj.ticket_subtype4_id
                    kwargs.setdefault('br_ticket_subtype4_id', subtype4)
            if business_rules.br_org_id:          
                if obj.ticket_org_id:
                    print(obj.ticket_org_id)
                    org = obj.ticket_org_id
                    kwargs.setdefault('br_org_id', org)
            # if 'assigned_to' in request.POST and request.method == 'POST' and request.POST.get('assigned_to') != '' and 'ever_assign' not in request.POST:
            #     assigned_to = request.POST.get('assigned_to')
            #     kwargs.setdefault('ticket_assign_to_id', assigned_to)
            if business_rules.br_priority_id:
                if obj.priority_id:
                    print(obj.priority_id)
                    priority = obj.priority_id
                    kwargs.setdefault('br_priority_id', priority)

        db_start_time = business_rules.start_hour +':'+ business_rules.start_minutes+' '+business_rules.start_AM_PM
        db_end_time = business_rules.end_hour +':'+ business_rules.end_minutes+' '+business_rules.end_AM_PM
        db_start_time_only = business_rules.start_hour +':'+ business_rules.start_minutes
        db_end_time_only = business_rules.end_hour +':'+ business_rules.end_minutes
        #24Hour Format
            
        start_time = get24HourFormattedTime(db_start_time)
        end_time = get24HourFormattedTime(db_end_time)

        if business_rules.start_AM_PM == 'PM':
            starttime_24_hrs = datetime.strptime(start_time,'%H:%M %p').strftime('%H:%M')
        else:
            starttime_24_hrs = start_time 

        if business_rules.end_AM_PM == 'PM':
            endtime_24_hrs = datetime.strptime(end_time,'%H:%M %p').strftime('%H:%M')    
        else:
            endtime_24_hrs = end_time  

        # Ticket submitted time
        submitted_ticket_time = obj.submitted_time.strftime('%H:%M')
        if starttime_24_hrs != '00:00' and endtime_24_hrs != '00:00':
            # kwargs.setdefault('start_24_hours__gte', starttime_24_hrs)
            # kwargs.setdefault('end_24_hours__lte', endtime_24_hrs)
            if submitted_ticket_time > starttime_24_hrs:
                kwargs.setdefault('start_24_hours', str(starttime_24_hrs)) 
            if submitted_ticket_time < endtime_24_hrs:  
                kwargs.setdefault('end_24_hours', str(endtime_24_hrs))

        #fetch day name through submitted date column
        ticket_date = obj.submitted_date
        date = ticket_date.strftime("%d %m %Y")
        day_name= ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday','sunday']
        current_day_key = datetime.strptime(date, '%d %m %Y').weekday()

        # return HttpResponse(day_name[current_day_key])
        if day_name[current_day_key] == 'monday':
            if business_rules.monday:
                kwargs.setdefault('monday', business_rules.monday)
        if day_name[current_day_key] == 'tuesday':
            if business_rules.tuesday:
                kwargs.setdefault('tuesday', business_rules.tuesday)
        if day_name[current_day_key] == 'wednesday':
            if business_rules.wednesday:
                kwargs.setdefault('wednesday', business_rules.wednesday)
        if day_name[current_day_key] == 'thursday':
            if business_rules.thursday:
                kwargs.setdefault('thursday', business_rules.thursday)
        if day_name[current_day_key] == 'friday':
            if business_rules.friday:
                kwargs.setdefault('friday', business_rules.friday)
        if day_name[current_day_key] == 'saturday':
            if business_rules.saturday:
                kwargs.setdefault('saturday', business_rules.saturday)
        if day_name[current_day_key] == 'sunday':
            if business_rules.sunday:
                kwargs.setdefault('sunday', business_rules.sunday)                           

        brid_list = BusinessRules.objects.filter(**kwargs).distinct().values_list('br_id', flat=True)
        for br_id in brid_list:
            query= BusinessRules.objects.get(pk=br_id)
            assign_to = query.br_ticket_assign_to_id
            if not obj.ticket_assign_to_id: 
                obj.ticket_assign_to_id = assign_to
                obj.save()

                obj1 = TicketUserRoleLog(
                urlog_ticket_id=obj.ticket_id,
                urlog_user_id=query.br_ticket_assign_to_id,
                urlog_event=1,
                urlog_created_by_id=obj.ticket_created_by_id
                )
                obj1.save()
    return 


#Business Rules Auto Assignment End#     

#Escalation Rules End
def addEscalationRules(request):
    ticketTypes = TicketType.objects.filter(ttype_is_delete=0).filter(ttype_is_active=1).filter(has_parent=0).filter(parent_id=0)
    # priorities = Priority.objects.filter(prior_is_delete=0).order_by('p_display_order')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'ticketTypes': ticketTypes,
        # 'priorities': priorities,
    }
    return render(request, 'itrak/BusinessRules/escalation_rules_add.html', context)

def saveEscalationRules(request):
    if request.method == 'POST':
        if 'ttype_id' in request.POST and request.POST['ttype_id']:
            ttype_id = request.POST.get('ttype_id')
        else:
            ttype_id = None

        if 'status_id' in request.POST and request.POST['status_id']:
            status_id = request.POST.get('status_id')
        else:
            status_id = None


        obj = EscalationRule(
            er_ttype_id = ttype_id
            ,er_status_id = status_id
        )
        obj.save()
        messages.success(request, 'Request Succeed! Escalation Rules added.')
        return redirect('listEscalationRules')
    else:
        messages.error(request, 'Request Failed! Escalation Rules cannot be added.Please try again.')
        return redirect('listEscalationRules')

@active_user_required
def listEscalationRules(request):
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/BusinessRules/escalation_rules_list.html', context)
#Escalation Rules End

@active_user_required
def getEscalationRulesListJson(request):
    allRules = EscalationRule.objects.filter(er_is_delete=0, er_is_active = 1)
    allAccountsArray = []
    for rule in allRules:
        innerArray = {}
        if rule.er_ttype_id:
            ticketTypeData = TicketType.objects.get(pk=rule.er_ttype_id)
            innerArray['ttype_name'] = ticketTypeData.ttype_name
        else:
            innerArray['ttype_name'] = ""
            
        if rule.er_status_id == True:
            innerArray['status']  = "Close"
        elif rule.er_status_id == False:
            innerArray['status'] = "Open"
        elif rule.er_status_id == "":
            innerArray['status'] = ""

        if rule.er_is_active == True:
            innerArray['active']  = "Active"
        else:   
            innerArray['active'] = "Not Active"
        innerArray['action'] = '<a href="Admin_EscalationRulesEdit?ERID='+ str(rule.er_id) +'"><i class="fa fa-pencil"></i></a> | <a onclick="deleteItemModal('+ str(rule.er_id) +')"><i class="fa fa-trash-o"></i></a>'
        allAccountsArray.append(innerArray)
    return HttpResponse(json.dumps(allAccountsArray), content_type="application/json")



@active_user_required
def editEscalationRules(request):
    erid = request.GET.get('ERID')
    try:
        data = EscalationRule.objects.get(pk=erid)
        ticketTypes = TicketType.objects.filter(ttype_is_delete=0).filter(ttype_is_active=1).filter(has_parent=0).filter(parent_id=0)
        # priorities = Priority.objects.filter(prior_is_delete=0).order_by('p_display_order')
    except EscalationRule.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listEscalationRules')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data,
            'ticketTypes': ticketTypes,
            # 'priorities': priorities
        }
        return render(request, 'itrak/BusinessRules/escalation_rules_edit.html', context)

@active_user_required
def updateEscalationRules(request):
    if request.method == 'POST':
        id = request.POST.get('ERID')
        try:
            obj = EscalationRule.objects.get(pk=id)
        except EscalationRule.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listEscalationRules')
        else:
            if 'ttype_id' in request.POST:
                obj.er_ttype_id = request.POST.get('ttype_id')
            else:
                obj.er_ttype_id = None

            if 'status_id' in request.POST:
                obj.er_status_id = request.POST.get('status_id')
            else:
                obj.er_status_id = None
            
            obj.save()

            messages.success(request, 'Request Succeed! Escalation Rules updated.')
            return redirect('listEscalationRules')
    else:
        messages.error(request, 'Request Failed! Escalation Rules cannot be updated.Please try again.')
        return redirect('listEscalationRules')

@active_user_required
def deleteEscalationRules(request):
    id = request.POST.get('ERID')
    try:
        obj = EscalationRule.objects.get(pk=id)
    except EscalationRule.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listEscalationRules')
    else:
        obj.er_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Escalation Rules deleted.')
        return redirect('listEscalationRules')

#Run Escalation Rules#
@active_user_required
def runEscalationRules(request, ticketid):
    obj = Ticket.objects.get(pk= ticketid)       
    escalationRules = EscalationRule.objects.filter(er_is_delete=0, er_is_active = 1)

    for rule in escalationRules:
        if request.method == 'POST':
            if rule.er_ttype_id:
                if rule.er_ttype_id == obj.ticket_type_id:
                    obj.ticket_status = rule.er_status_id
                    obj.save()
    return True