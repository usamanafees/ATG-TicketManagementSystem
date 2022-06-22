from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from itrak.models import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz
from django.utils.crypto import get_random_string
from django.conf.urls import url
from django.template.loader import render_to_string, get_template
from itrak.views.Load import *
from django.db.models.query import QuerySet
from django.core import signing
from datetime import datetime, timezone, timedelta
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, NamedStyle
import json
import operator
from functools import reduce
from django.db.models import Q, Count, F, Func, Sum
from django.apps import apps


# Create your views here.


# Custom Decorator Start#

user_login_required = user_passes_test(lambda user: user.is_active,
                                       login_url='/')  # Here user_passes_test decorator designates the user is active.


def active_user_required(view_func):
    decorated_view_func = login_required(user_login_required(view_func))
    return decorated_view_func


# Custom Decorator End#


# Get Saved Search Reports Start#

@active_user_required
def savedSearches(request):
    load_sidebar = get_sidebar(request)
    savedSearches = TicketSavedSearch.objects.filter()
    context = {
        'sidebar': load_sidebar,
        'savedSearches': savedSearches,
    }
    return render(request, 'itrak/Reports/saved_searches.html', context)


# Get Saved Search Reports End#


# Get Saved Search Process Start#

@active_user_required
def saveSearchProcess(request):
    save_id = request.GET.get('savedSearch')
    obj = TicketSavedSearch.objects.get(pk=save_id)

    kwargs = {
        '{0}__{1}'.format('ticket_is_delete', 'iexact'): 0,
        '{0}__{1}'.format('ticket_is_active', 'iexact'): 1,
    }
    ticket_status_dict = {0: "Opened", 1: "Closed"}
    labor_hours_dict = {"0": "Less Than", "1": "More Than", "2": "Equal"}
    fielddict = {"1": ''}
    if obj.ticket_status != None:
        ticket_status = obj.ticket_status
        kwargs.setdefault('ticket_status__iexact', ticket_status)
        fielddict.update({'Ticket Status': ticket_status_dict[ticket_status]})
    if obj.ticket_sub_status_id != None:
        ticket_sub_status = obj.ticket_sub_status_id
        kwargs.setdefault('ticket_sub_status_id', ticket_sub_status)
        result = SubStatus.objects.only('sub_status_text').get(pk=ticket_sub_status).sub_status_text
        if obj.ticket_status != None:
            fielddict.update({'Ticket Status': ticket_status_dict[ticket_status] + ' - ' + result})
        else:
            fielddict.update({'Ticket Status': ' - ' + result})
    if obj.priority_id != None:
        priority = obj.priority_id
        kwargs.setdefault('priority_id', priority)
        result = Priority.objects.only('priority_name').get(pk=priority).priority_name
        fielddict.update({'Priority': result})
    if obj.ticket_type_id != None:
        ticket_type = obj.ticket_type_id
        kwargs.setdefault('ticket_type_id', ticket_type)
        result = TicketType.objects.only('ttype_name').get(pk=ticket_type).ttype_name
        fielddict.update({'Ticket Type': result})
    if obj.ticket_subtype1_id != None:
        subtype1 = obj.ticket_subtype1_id
        kwargs.setdefault('ticket_subtype1_id', subtype1)
        result = TicketType.objects.only('ttype_name').get(pk=subtype1).ttype_name
        fielddict.update({'Subtype 1': result})
    if obj.ticket_subtype2_id != None:
        subtype2 = obj.ticket_subtype2_id
        kwargs.setdefault('ticket_subtype2_id', subtype2)
        result = TicketType.objects.only('ttype_name').get(pk=subtype2).ttype_name
        fielddict.update({'Subtype 2': result})
    if obj.ticket_subtype3_id != None:
        subtype3 = obj.ticket_subtype3_id
        kwargs.setdefault('ticket_subtype3_id', subtype3)
        result = TicketType.objects.only('ttype_name').get(pk=subtype3).ttype_name
        fielddict.update({'Subtype 3': result})
    if obj.ticket_subtype4_id != None:
        subtype4 = obj.ticket_subtype4_id
        kwargs.setdefault('ticket_subtype4_id', subtype4)
        result = TicketType.objects.only('ttype_name').get(pk=subtype4).ttype_name
        fielddict.update({'Subtype 4': result})
    if obj.subject != '':
        subject = obj.subject
        kwargs.setdefault('subject__icontains', subject)
        fielddict.update({'Subject': subject})
    if obj.ticket_note != '':
        ticket_note = request.POST.get('ticket_note')
        kwargs.setdefault('ticketNote__note_detail__icontains', ticket_note)
        fielddict.update({'Notes': ticket_note})
    if obj.all_three != '':
        all_three = request.POST.get('all_three')
        args = Q(subject__icontains=all_three) | Q(ticketNote__note_detail__icontains=all_three)
        fielddict.update({'Search All Three': all_three})
    if obj.ticket_record_locator != '':
        record_locator = obj.ticket_record_locator
        kwargs.setdefault('ticket_record_locator__startswith', record_locator)
        fielddict.update({'Record Locator': record_locator})
    if obj.ticket_caller_name != '':
        caller_name = obj.ticket_caller_name
        kwargs.setdefault('ticket_caller_name__startswith', caller_name)
        fielddict.update({'Caller Name': caller_name})
    if obj.ticket_caller_phone != '':
        caller_phone = obj.ticket_caller_phone
        kwargs.setdefault('ticket_caller_phone__startswith', caller_phone)
        fielddict.update({'Caller Phone': caller_phone})
    if obj.ticket_caller_email != '':
        caller_email = obj.ticket_caller_email
        kwargs.setdefault('ticket_caller_email__startswith', caller_email)
        fielddict.update({'Caller Email': caller_email})
    if obj.ticket_passenger_name != '':
        passenger_name = request.POST.get('passenger_name')
        kwargs.setdefault('ticket_passenger_name__startswith', passenger_name)
        fielddict.update({'Passenger Name': passenger_name})
    if obj.note_entered_by_id != None:
        note_entered_by = request.POST.get('note_entered_by')
        kwargs.setdefault('ticketNote__note_created_by_id', note_entered_by)
        result = User.objects.only('display_name').get(pk=note_entered_by).display_name
        fielddict.update({'Note Entered By': result})
    if obj.submitted_by_id != None:
        submitted_by = request.POST.get('submitted_by')
        kwargs.setdefault('ticket_caller_id', submitted_by)
        result = User.objects.only('display_name').get(pk=submitted_by).display_name
        fielddict.update({'Submitted By': result})
    if obj.entered_by_id != None:
        entered_by = request.POST.get('entered_by')
        kwargs.setdefault('ticket_created_by_id', entered_by)
        result = User.objects.only('display_name').get(pk=entered_by).display_name
        fielddict.update({'Entered By': result})
    if obj.task_assigned_to_id != None and obj.ever_assigned == 0:
        assigned_to = obj.task_assigned_to_id
        kwargs.setdefault('ticket_assign_to_id', assigned_to)
        result = User.objects.only('display_name').get(pk=assigned_to).display_name
        fielddict.update({'Assigned To': result})
    if obj.task_assigned_to_id != None and obj.ever_assigned == 1:
        assigned_to = obj.task_assigned_to_id
        kwargs.setdefault('ticketURLog__urlog_event', 1)
        kwargs.setdefault('ticketURLog__urlog_user_id', assigned_to)
        result = User.objects.only('display_name').get(pk=assigned_to).display_name
        fielddict.update({'Assigned To': result})
    if obj.assigned_by_id != None:
        assigned_by = obj.assigned_by_id
        kwargs.setdefault('ticket_assign_by_id', assigned_by)
        result = User.objects.only('display_name').get(pk=assigned_by).display_name
        fielddict.update({'Assigned By': result})
    if obj.next_action_id != None and obj.ever_next_action == 0:
        next_action = obj.next_action_id
        kwargs.setdefault('ticket_next_action_id', next_action)
        result = User.objects.only('display_name').get(pk=next_action).display_name
        fielddict.update({'Next Action': result})
    if obj.next_action_id != None and obj.ever_next_action == 1:
        next_action = obj.next_action_id
        kwargs.setdefault('ticketURLog__urlog_event', 2)
        kwargs.setdefault('ticketURLog__urlog_user_id', next_action)
        result = User.objects.only('display_name').get(pk=next_action).display_name
        fielddict.update({'Next Action': result})
    if obj.closed_by_id != None:
        closed_by = obj.closed_by_id
        kwargs.setdefault('ticket_closed_by_id', closed_by)
        result = User.objects.only('display_name').get(pk=closed_by).display_name
        fielddict.update({'Closed By': result})
    if obj.org_id != None:
        org_id = obj.org_id
        kwargs.setdefault('ticket_org_id', org_id)
        result = Organization.objects.only('org_name').get(pk=org_id).org_name
        fielddict.update({'Organization': result})
    if obj.client_id != None:
        client_id = obj.client_id
        kwargs.setdefault('ticket_client_id', client_id)
        result = Client.objects.only('client_name').get(pk=client_id).client_name
        fielddict.update({'Client': result})
    if obj.date_opened != '':
        date_opened = obj.date_opened
        dopen_start = datetime.strptime(obj.date_opened.split(' - ')[0], '%m/%d/%Y').strftime('%Y-%m-%d')
        dopen_end = datetime.strptime(obj.date_opened.split(' - ')[1], '%m/%d/%Y').strftime('%Y-%m-%d')
        kwargs.setdefault('ticket_created_at__gte', dopen_start)
        kwargs.setdefault('ticket_created_at__lte', dopen_end)
        fielddict.update({'Date Opened': date_opened})
    if obj.date_closed != '':
        date_closed = obj.date_closed
        dclose_start = datetime.strptime(obj.date_closed.split(' - ')[0], '%m/%d/%Y').strftime('%Y-%m-%d')
        dclose_end = datetime.strptime(obj.date_closed.split(' - ')[1], '%m/%d/%Y').strftime('%Y-%m-%d')
        kwargs.setdefault('ticket_closed_at__gte', dclose_start)
        kwargs.setdefault('ticket_closed_at__lte', dclose_end)
        fielddict.update({'Date Closed': date_closed})
    if obj.labour_hours_val != '':
        labour_hours_val = obj.labour_hours_val
        labour_hours_val += ':00:00'
        labour_hours = obj.labour_hours
        if labour_hours == '0':
            condition = 'lte'
        elif labour_hours == '1':
            condition = 'gte'
        else:
            condition = 'startswith'
        kwargs.setdefault('labour_hours__' + condition, str(labour_hours_val))
        fielddict.update({'Labor Hours - ' + labor_hours_dict[labour_hours]: labour_hours})
    if obj.task_description != '':
        task_description = obj.task_description
        kwargs.setdefault('ticketManager__tmgr_task__task_description__icontains', task_description)
        fielddict.update({'Task Description': task_description})
    if obj.task_assigned_to_id != None:
        task_assigned_to = obj.task_assigned_to_id
        kwargs.setdefault('ticketManager__task_assigned_to_id', task_assigned_to)
        result = User.objects.only('display_name').get(pk=task_assigned_to).display_name
        fielddict.update({'Task Assigned To': result})
    if obj.task_completion_date != '':
        task_completion_date = obj.task_completion_date
        dtask_start = datetime.strptime(obj.task_completion_date.split(' - ')[0], '%m/%d/%Y').strftime('%Y-%m-%d')
        dtask_end = datetime.strptime(obj.task_completion_date.split(' - ')[1], '%m/%d/%Y').strftime('%Y-%m-%d')
        kwargs.setdefault('ticketManager__task_due_date__gte', dtask_start)
        kwargs.setdefault('ticketManager__task_due_date__lte', dtask_end)
        fielddict.update({'Task Completion Date': task_completion_date})
    if obj.search_title != '':
        search_title = obj.search_title
    else:
        search_title = 'Search Results'

    if obj.search_title != '':
        search_title = obj.search_title
    if obj.output_view != '':
        output_view = obj.output_view
    sortargs = []
    sortresponse = []
    sortdict = {
        "ticket_assign_to__display_name": "Assigned To",
        "ticket_closed_at": "Date Closed",
        "ticket_created_at": "Date Opened",
        "ticket_created_by__display_name": "Entered By",
        "ticket_id": "Ticket Nbr",
        "ticket_subtype1__ttype_name": "Ticket Subtype",
        "ticket_type__ttype_name": "Ticket Type",
        "ticket_modified_at": "Last Activity",
        "ticket_next_action__display_name": "Next Action",
        "ticket_org__org_name": "Organization",
        "priority__p_display_order": "Priority",
        "ticket_status": "Status",
        "ticket_caller__display_name": "Submitted By",
        "ticket_client__client_name": "Client"
    }
    sortorder_dict = {
        "0": "Asc",
        "1": "Desc"
    }
    if obj.sort_column1 != '':
        sort_column1 = obj.sort_column1
        sort_order1 = obj.sort_order1
        if sort_order1 == '0':
            sort_value = sort_column1
        else:
            sort_value = '-' + sort_column1

        sortargs.append(sort_value)
        sortresponse.append(sortdict[sort_column1] + " , " + sortorder_dict[sort_order1])

    if obj.sort_column2 != '':
        sort_column2 = obj.sort_column2
        sort_order2 = obj.sort_order2
        if sort_order2 == '0':
            sort_value = sort_column2
        else:
            sort_value = '-' + str(sort_column2)

        sortargs.append(sort_value)
        sortresponse.append(sortdict[sort_column2] + " , " + sortorder_dict[sort_order2])

    if obj.sort_column3 != '':
        sort_column3 = obj.sort_column3
        sort_order3 = obj.sort_order3
        if sort_order3 == '0':
            sort_value = sort_column3
        else:
            sort_value = '-' + str(sort_column3)

        sortargs.append(sort_value)
        sortresponse.append(sortdict[sort_column3] + " , " + sortorder_dict[sort_order3])

    if not sortargs:
        if obj.all_three != '':
            tickets = Ticket.objects.filter(**kwargs).filter(args).distinct()
            ticketid_list = Ticket.objects.filter(**kwargs).filter(args).distinct().values_list('ticket_id', flat=True)
        else:
            tickets = Ticket.objects.filter(**kwargs).distinct()
            ticketid_list = Ticket.objects.filter(**kwargs).distinct().values_list('ticket_id', flat=True)
    else:
        if obj.all_three != '':
            tickets = Ticket.objects.filter(**kwargs).filter(args).distinct().order_by(*sortargs)
            ticketid_list = Ticket.objects.filter(**kwargs).filter(args).distinct().values_list('ticket_id',
                                                                                                flat=True).order_by(
                *sortargs)
        else:
            tickets = Ticket.objects.filter(**kwargs).distinct().order_by(*sortargs)
            ticketid_list = Ticket.objects.filter(**kwargs).distinct().values_list('ticket_id', flat=True).order_by(
                *sortargs)

    # Total Time Open Case Start #
    if obj.total_time_open_val != '':
        total_time_open_val = obj.total_time_open_val
        total_time_open = obj.total_time_open

        ticket_list = []
        if tickets:
            for ticket in tickets:
                if ticket.ticket_status == 0:
                    delta = datetime.now(timezone.utc) - ticket.ticket_created_at
                else:
                    delta = ticket.ticket_closed_at - ticket.ticket_created_at
                if total_time_open == '0':
                    if int(delta.days) <= int(total_time_open_val):
                        ticket_list.append(ticket.ticket_id)
                elif total_time_open == '1':
                    if int(delta.days) >= int(total_time_open_val):
                        ticket_list.append(ticket.ticket_id)
                else:
                    if int(delta.days) == int(total_time_open_val):
                        ticket_list.append(ticket.ticket_id)

            if not sortargs and ticket_list:
                tickets = Ticket.objects.filter(ticket_id__in=ticket_list).filter(ticket_is_delete=0).filter(
                    ticket_is_active=1)
                ticketid_list = Ticket.objects.filter(ticket_id__in=ticket_list).filter(
                    ticket_is_delete=0).filter(ticket_is_active=1).values_list('ticket_id', flat=True)

            elif sortargs and ticket_list:
                tickets = Ticket.objects.filter(ticket_id__in=ticket_list).filter(ticket_is_delete=0).filter(
                    ticket_is_active=1).order_by(*sortargs)
                ticketid_list = Ticket.objects.filter(ticket_id__in=ticket_list).filter(
                    ticket_is_delete=0).filter(ticket_is_active=1).values_list('ticket_id', flat=True).order_by(
                    *sortargs)
            else:
                tickets = []
        fielddict.update({'Total Time Open - ' + labor_hours_dict[total_time_open]: total_time_open_val})
    # Total Time Open Case End #

    if obj.show_criteria != 1:
        fielddict = {"1": ''}

    # for key, value in kwargs.items():
    #     print("The value of {} is {}".format(key, value))
    # return HttpResponse('OK')

    context = {
        'tickets': tickets,
        'search_title': search_title,
        'sortresponses': sortresponse,
        'fielddict': fielddict,
        'output_view': output_view,
        'ticketid_list': list(ticketid_list)
    }

    if output_view == 'OutputToExcel' or output_view == 'DetailOutputToExcel':
        if output_view == 'OutputToExcel':
            return get_xls_from_tickets(list(ticketid_list), '0')
        else:
            return get_xls_from_tickets(list(ticketid_list), '1')
    else:
        return render(request, 'itrak/Ticket/tickets_search_list.html', context)


# Get Saved Search Process End#


@csrf_exempt
# Delete Saved Search Against ID Start#
def savedSearchRemove(request):
    if request.is_ajax() and request.method == 'POST':
        save_id = request.POST.get('save_id[]')
        # probably you want to add a regex check if the username value is valid here
        if save_id:
            print(save_id)
            result = TicketSavedSearch.objects.filter(saved_search_id=save_id).delete()
            response_data = {}
            try:
                response_data['response'] = 'Success'
            except:
                response_data['response'] = 'No Record Found'
            return JsonResponse(response_data)


# Delete Saved Search Against ID End#


# Get Saved Search Reports Start#

@active_user_required
def summaryReports(request):
    load_sidebar = get_sidebar(request)
    savedSearches = TicketSavedSearch.objects.filter()
    context = {
        'sidebar': load_sidebar,
        'savedSearches': savedSearches,
    }
    return render(request, 'itrak/Reports/summary_reports.html', context)


# Get Saved Search Reports End#


# Get Date Range For Summry Report  Start#

@active_user_required
def getReportDateRange(request):
    report_id = request.GET.get('summaryReport')
    load_sidebar = get_sidebar(request)

    # for key, value in kwargs.items():
    #     print("The value of {} is {}".format(key, value))
    # return HttpResponse('OK')

    context = {
        'report_id': report_id,
        'sidebar': load_sidebar,
    }

    return render(request, 'itrak/Reports/get_report_daterange.html', context)


# Get Date Range For Summry Report End#


# Get Summary Report Result Start#

@active_user_required
def summaryReportResults(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        date_range = request.POST.get('date_range')
        start_date = datetime.strptime(request.POST.get('date_range').split(' - ')[0], '%m/%d/%Y').strftime('%Y-%m-%d')
        end_date = datetime.strptime(request.POST.get('date_range').split(' - ')[1] + " 23:59:59",
                                     '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        sort_by = request.POST.get('sort_by')

        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.

        reportdict = {
            "OrgContractTime": "Contract Time Used by Organization - Select Date Range",
            "OrgContractExp": "Contracts Expiring by Organization - Select Date Range",
            "OrgContractTimeOverage": "Contract Overage Time by Organization - Select Date Range",
            "IssuesPriority": "Tickets by Priority - Select Date Range",
            "IssuesPriorityByDay": "Tickets by Priority (Day) - Select Date Range",
            "IssuesPriorityByMonth": "Tickets by Priority (Month) - Select Date Range",
            "AssignedTo": "Tickets by Assigned To - Select Date Range",
            "Inactive": "Tickets by Inactive User - Results",
            "IssueSubTypes": "Tickets by Ticket Subtype - Select Date Range",
            "IssueTypes": "Tickets by Ticket Type - Select Date Range",
            "Locations": "Tickets by Client - Select Date Range",
            "NextActionBy": "Tickets by Next Action - Select Date Range",
            "Organizations": "Tickets by Organization - Select Date Range",
            "SubmittedBy": "Tickets by Submitter - Select Date Range",
            "DepartmentsSubmit": "Tickets by Submitting Department - Select Date Range",
            "OrgTimes": "Tickets by Rep - Select Date Range",
            "IncidentsByRep": "Labor Hours by Organization - Select Date Range",
            "UserTimes": "Labor Hours by User - Select Date Range",
            "OrgTimeOpen": "Total Time Open by Organization - Select Date Range",
            "UserTimeOpen": "Total Time Open by User - Select Date getReportDateRange"
        }

        if report_id in reportdict:
            if report_id == 'IssuesPriority':
                try:
                    tickets = Ticket.objects.values('priority__priority_name').filter(
                        priority_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    priorities = Priority.objects.values('priority_id', 'priority_name').filter(prior_is_delete=0)
                except Priority.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_closed_at__gte=start_date).filter(ticket_closed_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_closed_at__gte=start_date).filter(ticket_closed_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(Q(ticket_created_at__lt=start_date) | (Q(ticket_created_at__gte=start_date) & Q(ticket_created_at__lte=end_date))).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(Q(ticket_created_at__lt=start_date) | (Q(ticket_created_at__gte=start_date) & Q(ticket_created_at__lte=end_date))).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                # tickets_left_opened = Priority.objects.values('priority_name').filter(prior_is_delete=0).filter(ticketPriority__ticket_created_at__gt=end_date).annotate(tcount=Count('ticketPriority__ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'priorities': priorities,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_priority_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssuesPriorityByDay':
                try:
                    tickets = Ticket.objects.values('priority__priority_name').filter(
                        priority_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    priorities = Priority.objects.values('priority_name').filter(prior_is_delete=0)
                except Priority.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                total_tickets = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                total_tickets_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_sunday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_sunday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_monday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_monday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_tuesday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_tuesday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_wednesday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_wednesday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_thursday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_thursday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_friday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_friday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_saturday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_saturday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                total_sunday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=1).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_monday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=2).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_tuesday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=3).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_wednesday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=4).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_thursday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=5).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_friday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=6).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_saturday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=7).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                grand_total = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)

                if tickets_sunday or tickets_monday or tickets_tuesday or tickets_wednesday or tickets_thursday or tickets_friday or tickets_saturday:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'total_tickets': total_tickets,
                        'total_tickets_list': total_tickets_list,
                        'tickets_sunday': tickets_sunday,
                        'tickets_sunday_list': tickets_sunday_list,
                        'tickets_monday': tickets_monday,
                        'tickets_monday_list': tickets_monday_list,
                        'tickets_tuesday': tickets_tuesday,
                        'tickets_tuesday_list': tickets_tuesday_list,
                        'tickets_wednesday': tickets_wednesday,
                        'tickets_wednesday_list': tickets_wednesday_list,
                        'tickets_thursday': tickets_thursday,
                        'tickets_thursday_list': tickets_thursday_list,
                        'tickets_friday': tickets_friday,
                        'tickets_friday_list': tickets_friday_list,
                        'tickets_saturday': tickets_saturday,
                        'tickets_saturday_list': tickets_saturday_list,
                        'total_sunday': total_sunday,
                        'total_monday': total_monday,
                        'total_tuesday': total_tuesday,
                        'total_wednesday': total_wednesday,
                        'total_thursday': total_thursday,
                        'total_friday': total_friday,
                        'total_saturday': total_saturday,
                        'grand_total': grand_total,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'priorities': priorities,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_priority_day_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssuesPriorityByMonth':
                try:
                    tickets = Ticket.objects.values('priority__priority_name').filter(
                        priority_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    priorities = Priority.objects.values('priority_name').filter(prior_is_delete=0)
                except Priority.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                total_tickets = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                total_tickets_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_january = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_february = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_march = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_april = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_may = Ticket.objects.values('priority__priority_name').filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=5).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_june = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_july = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_august = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=8).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_september = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=9).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_october = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=10).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_november = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=11).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_december = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=12).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_january_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_february_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_march_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_april_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_may_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_june_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_july_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_august_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=8).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_september_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=9).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_october_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=10).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_november_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=11).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_december_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=12).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                total_january = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=1).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_february = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=2).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_march = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=3).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_april = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=4).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_may = Ticket.objects.filter(priority_id__isnull=False).filter(ticket_created_at__month=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)
                total_june = Ticket.objects.filter(priority_id__isnull=False).filter(ticket_created_at__month=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)
                total_july = Ticket.objects.filter(priority_id__isnull=False).filter(ticket_created_at__month=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)
                total_august = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=8).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_september = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=9).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_october = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=10).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_november = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=11).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_december = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=12).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                grand_total = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)

                if total_january or total_february or total_march or total_april or total_may or total_june or total_june or total_july or total_august or total_september or total_october or total_november or total_december:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'total_tickets': total_tickets,
                        'total_tickets_list': total_tickets_list,
                        'tickets_january': tickets_january,
                        'tickets_january_list': tickets_january_list,
                        'tickets_february': tickets_february,
                        'tickets_february_list': tickets_february_list,
                        'tickets_march': tickets_march,
                        'tickets_march_list': tickets_march_list,
                        'tickets_april': tickets_april,
                        'tickets_april_list': tickets_april_list,
                        'tickets_may': tickets_may,
                        'tickets_may_list': tickets_may_list,
                        'tickets_june': tickets_june,
                        'tickets_june_list': tickets_june_list,
                        'tickets_july': tickets_july,
                        'tickets_july_list': tickets_july_list,
                        'tickets_august': tickets_august,
                        'tickets_august_list': tickets_august_list,
                        'tickets_september': tickets_september,
                        'tickets_september_list': tickets_september_list,
                        'tickets_october': tickets_october,
                        'tickets_october_list': tickets_october_list,
                        'tickets_november': tickets_november,
                        'tickets_november_list': tickets_november_list,
                        'tickets_december': tickets_december,
                        'tickets_december_list': tickets_december_list,
                        'total_january': total_january,
                        'total_february': total_february,
                        'total_march': total_march,
                        'total_april': total_april,
                        'total_may': total_may,
                        'total_june': total_june,
                        'total_july': total_july,
                        'total_august': total_august,
                        'total_september': total_september,
                        'total_october': total_october,
                        'total_november': total_november,
                        'total_december': total_december,
                        'grand_total': grand_total,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'priorities': priorities,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_priority_month_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'AssignedTo':
                try:
                    tickets = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                    'ticket_assign_to__last_name').filter(
                        ticket_assign_to__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                        'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                       'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_assign_to_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'Inactive':
                try:
                    tickets = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                    'ticket_assign_to__last_name').filter(
                        ticket_assign_to__isnull=False).filter(ticket_assign_to__is_active=False).annotate(
                        tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                print(tickets)
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                        'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                       'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    print(tickets)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_inactive_user_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssueSubTypes':
                try:
                    ttypes = Ticket.objects.values('ticket_subtype1__parent_id', 'ticket_subtype1_id',
                                                   'ticket_subtype1__ttype_name').filter(
                        ticket_subtype1_id__isnull=False).annotate(tcount=Count('ticket_id')).order_by('ticket_type')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    parent_ttypes = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                        ticket_subtype1_id__isnull=False).annotate(tcount=Count('ticket_id')).order_by('ticket_type')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                tickets_open_before = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                parent_open_before = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                parent_open_in = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                parent_closed = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                parent_left_opened = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'parent_open_before': parent_open_before,
                        'parent_open_in': parent_open_in,
                        'parent_closed': parent_closed,
                        'parent_left_opened': parent_left_opened,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'ttypes': ttypes,
                        'parent_ttypes': parent_ttypes,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_ticket_subtype_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssueTypes':
                try:
                    ttypes = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                        ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).annotate(
                        tcount=Count('ticket_id')).order_by('-tcount')
                    ttypes_list = Ticket.objects.values_list('ticket_type_id', flat=True).filter(
                        ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).annotate(
                        tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id')).order_by('-tcount')
                tickets_open_before_list = Ticket.objects.values_list('ticket_type_id', flat=True).filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id')).order_by('-tcount')
                tickets_open_in_list = list(
                    Ticket.objects.values_list('ticket_type_id', flat=True).filter(ticket_type_id__isnull=False).filter(
                        ticket_type__has_parent=0).filter(ticket_created_at__gte=start_date).filter(
                        ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id')).order_by(
                    '-tcount')
                tickets_closed_list = list(
                    Ticket.objects.values_list('ticket_type_id', flat=True).filter(ticket_type_id__isnull=False).filter(
                        ticket_type__has_parent=0).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                        tcount=Count('ticket_id')))
                tickets_left_opened = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id')).order_by('-tcount')
                tickets_left_opened_list = Ticket.objects.values_list('ticket_type_id', flat=True).filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                ttype_tickets_closed = TicketType.objects.values('ttype_id', 'ttype_name').filter(has_parent=0).filter(
                    ttype_is_delete=0).filter(ticketType__ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticketType__ticket_id')).order_by('-tcount')

                for tickets in tickets_closed:
                    print(type(tickets))

                # tickets_closed.add("{'ticket_type_id': 2, 'ticket_type__ttype_name': 'Waivers & Favors', 'tcount':777777}')")

                # return HttpResponse(tickets_closed)

                for ttype in ttypes_list:
                    if ttype not in tickets_closed_list:
                        print(ttype)
                        tickets_closed_list.append(ttype)

                print(tickets_closed_list)

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'ttypes': ttypes,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_ticket_type_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'Locations':
                try:
                    clients = Ticket.objects.values('ticket_client_id', 'ticket_client__client_name').filter(
                        ticket_client_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'clients': clients,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_client_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'NextActionBy':
                try:
                    tickets = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                    'ticket_next_action__last_name').filter(
                        ticket_assign_to__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                            'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                        'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                       'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                            'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    print(tickets)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_next_action_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'Organizations':
                try:
                    organizations = Ticket.objects.values('ticket_org_id', 'ticket_org__org_name').filter(
                        ticket_org_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_org_id', flat=True).filter(
                    ticket_org_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(
                    Ticket.objects.values_list('ticket_org_id', flat=True).filter(ticket_org_id__isnull=False).filter(
                        ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                        tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_org_id', flat=True).filter(
                    ticket_org_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_org_id', flat=True).filter(
                    ticket_org_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'organizations': organizations,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_organization_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'SubmittedBy':
                try:
                    tickets = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                    'ticket_caller__last_name').filter(
                        ticket_assign_to__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                            'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                        'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                       'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                            'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    print(tickets)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_caller_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'DepartmentsSubmit':
                try:
                    departments = Ticket.objects.values('ticket_caller__user_dep__dep_id',
                                                        'ticket_caller__user_dep__dep_name').filter(
                        ticket_caller__isnull=False).filter(ticket_caller__user_dep__isnull=False).annotate(
                        tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_caller__user_dep__dep_id',
                                                                      flat=True).filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(
                    Ticket.objects.values_list('ticket_caller__user_dep__dep_id', flat=True).filter(
                        ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                        ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_caller__user_dep__dep_id', flat=True).filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_caller__user_dep__dep_id',
                                                                      flat=True).filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'departments': departments,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_submit_department_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'OrgTimes':

                try:
                    org_labour_hours = TicketNote.objects.values('note_ticket__ticket_org_id',
                                                                 'note_ticket__ticket_org__org_name', 'labour_hours',
                                                                 'note_created_at').filter(
                        labour_hours__isnull=False).filter(note_created_at__gte=start_date).filter(
                        note_created_at__lte=end_date).order_by('note_ticket__ticket_org__org_id')
                except TicketNote.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                hoursList = []
                orghoursList = []
                orgDict = {}
                last_id = 0

                for org in org_labour_hours:
                    hoursList.append(org['labour_hours'].strftime("%H:%M:%S"))
                    if last_id != org['note_ticket__ticket_org__org_name']:
                        if last_id != 0:
                            totalSecs = 0
                            for hours in orghoursList:
                                timeParts = [int(s) for s in hours.split(':')]
                                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                            totalSecs, sec = divmod(totalSecs, 60)
                            hr, min = divmod(totalSecs, 60)
                            orgDict[last_id] = "%d:%02d" % (hr, min)
                            orghoursList.clear()
                        orghoursList.append(org['labour_hours'].strftime("%H:%M:%S"))
                    else:
                        orghoursList.append(org['labour_hours'].strftime("%H:%M:%S"))
                    last_id = org['note_ticket__ticket_org__org_name']
                totalSecs = 0
                for hours in orghoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                orgDict[last_id] = "%d:%02d" % (hr, min)
                totalSecs = 0
                for hours in hoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                total_hours = "%d:%02d" % (hr, min)

                # last_id = 0
                # lbr_hours = {}
                # total_hours = 0
                # total_minutes = 0
                # for org in org_labour_hours:
                #     print(org['labour_hours'])
                #     print(org['note_ticket__ticket_org__org_name'])
                #     if org['note_ticket__ticket_org_id'] != last_id:
                #         print('IF')
                #         hours = org['labour_hours']
                #         lbr_hours.update({org['note_ticket__ticket_org__org_name']: hours.strftime("%H:%M") })
                #     else:
                #         print('ELSE')
                #         print(org['labour_hours'])
                #         # t1 = lbr_hours[org['note_ticket__ticket_org__org_name']]
                #         # t1 = datetime.strptime(str(t1)+":00", '%H:%M:%S')
                #         # t2 = org['labour_hours']
                #         # t2 = datetime.strptime(str(t2), '%H:%M:%S')
                #         # time_zero = datetime.strptime('00:00:00', '%H:%M:%S')
                #         # print(t1.hour + t2.hour)
                #         # print((t1 - time_zero + t2).hour)
                #         # print((t1 - time_zero + t2).minute)
                #         hours  = org['labour_hours'].hour
                #         # hours  = '40:15:30'
                #         # hours = timedelta(hours=hours.hour, minutes=hours.minute)
                #         print(type(hours))
                #         lbr_hours.update({org['note_ticket__ticket_org__org_name']: hours })
                #     print(lbr_hours)
                #     total_hours += org['labour_hours'].hour
                #     print(total_hours)
                #     total_minutes += org['labour_hours'].minute
                #     last_id = org['note_ticket__ticket_org_id']

                if orgDict:
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'orgDict': orgDict,
                        'total_hours': total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_org_labourhour_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'UserTimes':
                try:
                    user_labour_hours = TicketNote.objects.values('note_ticket__ticket_caller_id',
                                                                  'note_ticket__ticket_caller__display_name',
                                                                  'note_ticket__ticket_caller__first_name',
                                                                  'note_ticket__ticket_caller__last_name',
                                                                  'labour_hours', 'note_created_at').filter(
                        labour_hours__isnull=False).filter(note_ticket__ticket_caller_id__isnull=False).filter(
                        note_created_at__gte=start_date).filter(note_created_at__lte=end_date).order_by(
                        'note_ticket__ticket_caller__display_name')
                except TicketNote.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                hoursList = []
                userhoursList = []
                userDict = {}
                last_id = 0

                for user in user_labour_hours:
                    hoursList.append(user['labour_hours'].strftime("%H:%M:%S"))
                    if last_id != user['note_ticket__ticket_caller_id']:
                        if last_id != 0:
                            totalSecs = 0
                            for hours in userhoursList:
                                timeParts = [int(s) for s in hours.split(':')]
                                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                            totalSecs, sec = divmod(totalSecs, 60)
                            hr, min = divmod(totalSecs, 60)
                            userDict[full_name] = "%d:%02d" % (hr, min)
                            userhoursList.clear()
                        userhoursList.append(user['labour_hours'].strftime("%H:%M:%S"))
                    else:
                        userhoursList.append(user['labour_hours'].strftime("%H:%M:%S"))
                    last_id = user['note_ticket__ticket_caller_id']
                    full_name = user['note_ticket__ticket_caller__first_name'] + " , " + user[
                        'note_ticket__ticket_caller__last_name']

                totalSecs = 0
                for hours in userhoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                userDict[full_name] = "%d:%02d" % (hr, min)

                totalSecs = 0
                for hours in hoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                total_hours = "%d:%02d" % (hr, min)

                # last_id = 0
                # lbr_hours = {}
                # total_hours = 0
                # total_minutes = 0
                # for user in user_labour_hours:
                #     if user['note_ticket__ticket_caller__display_name'] != last_id:
                #         hours = user['labour_hours']
                #         print()
                #         lbr_hours.update({user['note_ticket__ticket_caller__display_name']: hours.strftime("%H:%M") })
                #     else:
                #         t1 = lbr_hours[user['note_ticket__ticket_caller__display_name']]
                #         t1 = datetime.strptime(str(t1)+":00", '%H:%M:%S')
                #         t2 = user['labour_hours']
                #         t2 = datetime.strptime(str(t2), '%H:%M:%S')
                #         time_zero = datetime.strptime('00:00:00', '%H:%M:%S')
                #         hours  = (t1 - time_zero + t2).time()
                #         lbr_hours.update({user['note_ticket__ticket_caller__display_name']: hours.strftime("%H:%M") })
                #
                #     total_hours += user['labour_hours'].hour
                #     total_minutes += user['labour_hours'].minute
                #     last_id = user['note_ticket__ticket_caller__display_name']

                if userDict:
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'userDict': userDict,
                        'total_hours': total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_user_labourhour_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'OrgTimeOpen':
                try:
                    tickets = Ticket.objects.values('ticket_org__org_name', 'ticket_status', 'ticket_created_at',
                                                    'ticket_id', 'ticket_closed_at').filter(ticket_is_delete=0).filter(
                        ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).order_by(
                        'ticket_org_id')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                last_id = 0
                tot_hours = {}
                g_total_hours = 0
                if tickets:
                    for ticket in tickets:

                        if ticket['ticket_org__org_name'] != last_id:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round((hours) + (minutes / 100), 2)
                            # print("T")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_org__org_name']: total_hours})
                            # print(tot_hours)
                        else:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round(tot_hours[ticket['ticket_org__org_name']] + (hours) + (minutes / 100),
                                                2)
                            # print("S")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_org__org_name']: total_hours})
                            # print(tot_hours)

                        g_total_hours += round(((hours) + (minutes / 100)), 2)
                        # print(g_total_hours)
                        last_id = ticket['ticket_org__org_name']

                if tot_hours:
                    g_total_hours = round(g_total_hours, 2)
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tot_hours': tot_hours,
                        'g_total_hours': g_total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_org_totaltime_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'UserTimeOpen':
                try:
                    tickets = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                    'ticket_caller__last_name', 'ticket_status', 'ticket_created_at',
                                                    'ticket_id', 'ticket_closed_at').filter(ticket_is_delete=0).filter(
                        ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).order_by(
                        'ticket_caller_id')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                last_id = 0
                tot_hours, userDict = {}, {}
                g_total_hours = 0
                if tickets:
                    for ticket in tickets:

                        if ticket['ticket_caller_id'] != last_id:
                            if last_id != 0:
                                userDict[full_name] = tot_hours[last_id]
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round((hours) + (minutes / 100), 2)
                            # print("T")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_caller_id']: total_hours})
                            # print(tot_hours)
                        else:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round(tot_hours[ticket['ticket_caller_id']] + (hours) + (minutes / 100), 2)
                            # print("S")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_caller_id']: total_hours})
                            # print(tot_hours)
                        if ticket['ticket_caller__first_name'] is None and ticket['ticket_caller__last_name'] is None:
                            full_name = 'No Name'
                        elif ticket['ticket_caller__first_name'] is None:
                            full_name = ticket['ticket_caller__last_name']
                        elif ticket['ticket_caller__last_name'] is None:
                            full_name = ticket['ticket_caller__first_name']
                        else:
                            full_name = ticket['ticket_caller__first_name'] + " , " + ticket['ticket_caller__last_name']

                        g_total_hours += round(((hours) + (minutes / 100)), 2)
                        # print(g_total_hours)
                        last_id = ticket['ticket_caller_id']
                        # full_name = ticket['ticket_caller__first_name'] + " , " + ticket['ticket_caller__first_name']

                if tot_hours:
                    g_total_hours = round(g_total_hours, 2)
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tot_hours': userDict,
                        'g_total_hours': g_total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_user_totaltime_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

        else:
            return render_to_response('itrak/page-404.html')


# Get Summary Report Result End#


# Get Summary Report Ticket List Start#

@active_user_required
def getSummaryReportTicketList(request):
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        date_range = request.POST.get('date_range')
        start_date = datetime.strptime(request.POST.get('date_range').split(' - ')[0], '%m/%d/%Y').strftime('%Y-%m-%d')
        end_date = datetime.strptime(request.POST.get('date_range').split(' - ')[1] + " 23:59:59",
                                     '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        sort_by = request.POST.get('sort_by')

        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.

        reportdict = {
            "OrgContractTime": "Contract Time Used by Organization - Select Date Range",
            "OrgContractExp": "Contracts Expiring by Organization - Select Date Range",
            "OrgContractTimeOverage": "Contract Overage Time by Organization - Select Date Range",
            "IssuesPriority": "Tickets by Priority - Select Date Range",
            "IssuesPriorityByDay": "Tickets by Priority (Day) - Select Date Range",
            "IssuesPriorityByMonth": "Tickets by Priority (Month) - Select Date Range",
            "AssignedTo": "Tickets by Assigned To - Select Date Range",
            "Inactive": "Tickets by Inactive User - Results",
            "IssueSubTypes": "Tickets by Ticket Subtype - Select Date Range",
            "IssueTypes": "Tickets by Ticket Type - Select Date Range",
            "Locations": "Tickets by Client - Select Date Range",
            "NextActionBy": "Tickets by Next Action - Select Date Range",
            "Organizations": "Tickets by Organization - Select Date Range",
            "SubmittedBy": "Tickets by Submitter - Select Date Range",
            "DepartmentsSubmit": "Tickets by Submitting Department - Select Date Range",
            "OrgTimes": "Tickets by Rep - Select Date Range",
            "IncidentsByRep": "Labor Hours by Organization - Select Date Range",
            "UserTimes": "Labor Hours by User - Select Date Range",
            "OrgTimeOpen": "Total Time Open by Organization - Select Date Range",
            "UserTimeOpen": "Total Time Open by User - Select Date getReportDateRange"
        }

        if report_id in reportdict:
            if report_id == 'IssuesPriority':
                try:
                    tickets = Ticket.objects.values('priority__priority_name').filter(
                        priority_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    priorities = Priority.objects.values('priority_name').filter(prior_is_delete=0)
                except Priority.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                # tickets_left_opened = Priority.objects.values('priority_name').filter(prior_is_delete=0).filter(ticketPriority__ticket_created_at__gt=end_date).annotate(tcount=Count('ticketPriority__ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'priorities': priorities,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_priority_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssuesPriorityByDay':
                try:
                    tickets = Ticket.objects.values('priority__priority_name').filter(
                        priority_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    priorities = Priority.objects.values('priority_name').filter(prior_is_delete=0)
                except Priority.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                total_tickets = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                total_tickets_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_sunday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_sunday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_monday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_monday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_tuesday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_tuesday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_wednesday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_wednesday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_thursday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_thursday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_friday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_friday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_saturday = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_saturday_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__week_day=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                total_sunday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=1).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_monday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=2).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_tuesday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=3).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_wednesday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=4).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_thursday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=5).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_friday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=6).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_saturday = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__week_day=7).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                grand_total = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)

                if tickets_sunday or tickets_monday or tickets_tuesday or tickets_wednesday or tickets_thursday or tickets_friday or tickets_saturday:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'total_tickets': total_tickets,
                        'total_tickets_list': total_tickets_list,
                        'tickets_sunday': tickets_sunday,
                        'tickets_sunday_list': tickets_sunday_list,
                        'tickets_monday': tickets_monday,
                        'tickets_monday_list': tickets_monday_list,
                        'tickets_tuesday': tickets_tuesday,
                        'tickets_tuesday_list': tickets_tuesday_list,
                        'tickets_wednesday': tickets_wednesday,
                        'tickets_wednesday_list': tickets_wednesday_list,
                        'tickets_thursday': tickets_thursday,
                        'tickets_thursday_list': tickets_thursday_list,
                        'tickets_friday': tickets_friday,
                        'tickets_friday_list': tickets_friday_list,
                        'tickets_saturday': tickets_saturday,
                        'tickets_saturday_list': tickets_saturday_list,
                        'total_sunday': total_sunday,
                        'total_monday': total_monday,
                        'total_tuesday': total_tuesday,
                        'total_wednesday': total_wednesday,
                        'total_thursday': total_thursday,
                        'total_friday': total_friday,
                        'total_saturday': total_saturday,
                        'grand_total': grand_total,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'priorities': priorities,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_priority_day_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssuesPriorityByMonth':
                try:
                    tickets = Ticket.objects.values('priority__priority_name').filter(
                        priority_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    priorities = Priority.objects.values('priority_name').filter(prior_is_delete=0)
                except Priority.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                total_tickets = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                total_tickets_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_january = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_february = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_march = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_april = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_may = Ticket.objects.values('priority__priority_name').filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=5).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_june = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_july = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_august = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=8).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_september = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=9).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_october = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=10).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_november = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=11).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_december = Ticket.objects.values('priority__priority_name').filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=12).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_january_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=1).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_february_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=2).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_march_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=3).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_april_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=4).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_may_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_june_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_july_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_august_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=8).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_september_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=9).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_october_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=10).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_november_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=11).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_december_list = Ticket.objects.values_list('priority__priority_name', flat=True).filter(
                    priority_id__isnull=False).filter(ticket_created_at__month=12).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                total_january = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=1).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_february = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=2).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_march = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=3).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_april = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=4).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_may = Ticket.objects.filter(priority_id__isnull=False).filter(ticket_created_at__month=5).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)
                total_june = Ticket.objects.filter(priority_id__isnull=False).filter(ticket_created_at__month=6).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)
                total_july = Ticket.objects.filter(priority_id__isnull=False).filter(ticket_created_at__month=7).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)
                total_august = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=8).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_september = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=9).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_october = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=10).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_november = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=11).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                total_december = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__month=12).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date)
                grand_total = Ticket.objects.filter(priority_id__isnull=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date)

                if total_january or total_february or total_march or total_april or total_may or total_june or total_june or total_july or total_august or total_september or total_october or total_november or total_december:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'total_tickets': total_tickets,
                        'total_tickets_list': total_tickets_list,
                        'tickets_january': tickets_january,
                        'tickets_january_list': tickets_january_list,
                        'tickets_february': tickets_february,
                        'tickets_february_list': tickets_february_list,
                        'tickets_march': tickets_march,
                        'tickets_march_list': tickets_march_list,
                        'tickets_april': tickets_april,
                        'tickets_april_list': tickets_april_list,
                        'tickets_may': tickets_may,
                        'tickets_may_list': tickets_may_list,
                        'tickets_june': tickets_june,
                        'tickets_june_list': tickets_june_list,
                        'tickets_july': tickets_july,
                        'tickets_july_list': tickets_july_list,
                        'tickets_august': tickets_august,
                        'tickets_august_list': tickets_august_list,
                        'tickets_september': tickets_september,
                        'tickets_september_list': tickets_september_list,
                        'tickets_october': tickets_october,
                        'tickets_october_list': tickets_october_list,
                        'tickets_november': tickets_november,
                        'tickets_november_list': tickets_november_list,
                        'tickets_december': tickets_december,
                        'tickets_december_list': tickets_december_list,
                        'total_january': total_january,
                        'total_february': total_february,
                        'total_march': total_march,
                        'total_april': total_april,
                        'total_may': total_may,
                        'total_june': total_june,
                        'total_july': total_july,
                        'total_august': total_august,
                        'total_september': total_september,
                        'total_october': total_october,
                        'total_november': total_november,
                        'total_december': total_december,
                        'grand_total': grand_total,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'priorities': priorities,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_priority_month_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'AssignedTo':
                try:
                    tickets = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                    'ticket_assign_to__last_name').filter(
                        ticket_assign_to__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                        'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                       'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_assign_to_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'Inactive':
                try:
                    tickets = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                    'ticket_assign_to__last_name').filter(
                        ticket_assign_to__isnull=False).filter(ticket_assign_to__is_active=False).annotate(
                        tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                print(tickets)
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                        'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                       'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_assign_to_id', 'ticket_assign_to__first_name',
                                                            'ticket_assign_to__last_name').filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_assign_to_id', flat=True).filter(
                    ticket_assign_to_id__isnull=False).filter(ticket_assign_to__is_active=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    print(tickets)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_inactive_user_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssueSubTypes':
                try:
                    ttypes = Ticket.objects.values('ticket_subtype1__parent_id', 'ticket_subtype1_id',
                                                   'ticket_subtype1__ttype_name').filter(
                        ticket_subtype1_id__isnull=False).annotate(tcount=Count('ticket_id')).order_by('ticket_type')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    parent_ttypes = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                        ticket_subtype1_id__isnull=False).annotate(tcount=Count('ticket_id')).order_by('ticket_type')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                tickets_open_before = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_subtype1__ttype_name').filter(
                    ticket_subtype1_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_subtype1_id', flat=True).filter(
                    ticket_subtype1_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                parent_open_before = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                parent_open_in = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                parent_closed = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                parent_left_opened = Ticket.objects.values('ticket_subtype1__parent_id').filter(
                    ticket_subtype1_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'parent_open_before': parent_open_before,
                        'parent_open_in': parent_open_in,
                        'parent_closed': parent_closed,
                        'parent_left_opened': parent_left_opened,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'ttypes': ttypes,
                        'parent_ttypes': parent_ttypes,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_ticket_subtype_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'IssueTypes':
                try:
                    ttypes = Ticket.objects.values('ticket_type_id', 'ticket_type__ttype_name').filter(
                        ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).annotate(
                        tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_type_id', flat=True).filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_created_at__lt=start_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in_list = list(
                    Ticket.objects.values_list('ticket_type_id', flat=True).filter(ticket_type_id__isnull=False).filter(
                        ticket_type__has_parent=0).filter(ticket_created_at__gte=start_date).filter(
                        ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_type_id', flat=True).filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_type__ttype_name').filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_type_id', flat=True).filter(
                    ticket_type_id__isnull=False).filter(ticket_type__has_parent=0).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'ttypes': ttypes,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_ticket_type_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'Locations':
                try:
                    clients = Ticket.objects.values('ticket_client_id', 'ticket_client__client_name').filter(
                        ticket_client_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_client__client_name').filter(
                    ticket_client_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_client_id', flat=True).filter(
                    ticket_client_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'clients': clients,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_client_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'NextActionBy':
                try:
                    tickets = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                    'ticket_next_action__last_name').filter(
                        ticket_assign_to__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                            'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                        'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                       'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_next_action_id', 'ticket_next_action__first_name',
                                                            'ticket_next_action__last_name').filter(
                    ticket_next_action_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_next_action_id', flat=True).filter(
                    ticket_next_action_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    print(tickets)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_next_action_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'Organizations':
                try:
                    organizations = Ticket.objects.values('ticket_org_id', 'ticket_org__org_name').filter(
                        ticket_org_id__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_org_id', flat=True).filter(
                    ticket_org_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(
                    Ticket.objects.values_list('ticket_org_id', flat=True).filter(ticket_org_id__isnull=False).filter(
                        ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).annotate(
                        tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_org_id', flat=True).filter(
                    ticket_org_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_org__org_name').filter(
                    ticket_org_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_org_id', flat=True).filter(
                    ticket_org_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'organizations': organizations,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_organization_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'SubmittedBy':
                try:
                    tickets = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                    'ticket_caller__last_name').filter(
                        ticket_assign_to__isnull=False).annotate(tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
                try:
                    users = User.objects.values('first_name', 'last_name').filter(is_delete=0)
                except User.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                            'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                        'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_closed = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                       'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(ticket_closed_at__range=(start_date, end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_caller_id', 'ticket_caller__first_name',
                                                            'ticket_caller__last_name').filter(
                    ticket_caller_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_caller_id', flat=True).filter(
                    ticket_caller_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)
                    print(tickets)
                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tickets': tickets,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_caller_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'DepartmentsSubmit':
                try:
                    departments = Ticket.objects.values('ticket_caller__user_dep__dep_id',
                                                        'ticket_caller__user_dep__dep_name').filter(
                        ticket_caller__isnull=False).filter(ticket_caller__user_dep__isnull=False).annotate(
                        tcount=Count('ticket_id'))
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                tickets_open_before = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_before_list = Ticket.objects.values_list('ticket_caller__user_dep__dep_id',
                                                                      flat=True).filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__lt=start_date).annotate(
                    tcount=Count('ticket_id'))
                tickets_open_in = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                    ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id'))
                tickets_open_in_list = list(
                    Ticket.objects.values_list('ticket_caller__user_dep__dep_id', flat=True).filter(
                        ticket_caller__user_dep__dep_id__isnull=False).filter(ticket_created_at__gte=start_date).filter(
                        ticket_created_at__lte=end_date).annotate(tcount=Count('ticket_id')))
                tickets_closed = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_closed_list = Ticket.objects.values_list('ticket_caller__user_dep__dep_id', flat=True).filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    ticket_closed_at__range=(start_date, end_date)).annotate(tcount=Count('ticket_id'))
                tickets_left_opened = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))
                tickets_left_opened_list = Ticket.objects.values_list('ticket_caller__user_dep__dep_id',
                                                                      flat=True).filter(
                    ticket_caller__user_dep__dep_id__isnull=False).filter(
                    Q(ticket_closed_at__isnull=True) | Q(ticket_closed_at__gt=end_date)).annotate(
                    tcount=Count('ticket_id'))

                if tickets_open_before or tickets_open_in or tickets_closed or tickets_left_opened:

                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'tickets_open_before': tickets_open_before,
                        'tickets_open_before_list': tickets_open_before_list,
                        'tickets_open_in': tickets_open_in,
                        'tickets_open_in_list': tickets_open_in_list,
                        'tickets_closed': tickets_closed,
                        'tickets_closed_list': tickets_closed_list,
                        'tickets_left_opened': tickets_left_opened,
                        'tickets_left_opened_list': tickets_left_opened_list,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'departments': departments,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_submit_department_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'OrgTimes':

                try:
                    org_labour_hours = TicketNote.objects.values('note_ticket__ticket_org_id',
                                                                 'note_ticket__ticket_org__org_name', 'labour_hours',
                                                                 'note_created_at').filter(
                        labour_hours__isnull=False).filter(note_created_at__gte=start_date).filter(
                        note_created_at__lte=end_date).order_by('note_ticket__ticket_org__org_id')
                except TicketNote.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                hoursList = []
                orghoursList = []
                orgDict = {}
                last_id = 0

                for org in org_labour_hours:
                    hoursList.append(org['labour_hours'].strftime("%H:%M:%S"))
                    if last_id != org['note_ticket__ticket_org__org_name']:
                        if last_id != 0:
                            totalSecs = 0
                            for hours in orghoursList:
                                timeParts = [int(s) for s in hours.split(':')]
                                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                            totalSecs, sec = divmod(totalSecs, 60)
                            hr, min = divmod(totalSecs, 60)
                            orgDict[last_id] = "%d:%02d" % (hr, min)
                            orghoursList.clear()
                        orghoursList.append(org['labour_hours'].strftime("%H:%M:%S"))
                    else:
                        orghoursList.append(org['labour_hours'].strftime("%H:%M:%S"))
                    last_id = org['note_ticket__ticket_org__org_name']
                totalSecs = 0
                for hours in orghoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                orgDict[last_id] = "%d:%02d" % (hr, min)
                totalSecs = 0
                for hours in hoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                total_hours = "%d:%02d" % (hr, min)

                # last_id = 0
                # lbr_hours = {}
                # total_hours = 0
                # total_minutes = 0
                # for org in org_labour_hours:
                #     print(org['labour_hours'])
                #     print(org['note_ticket__ticket_org__org_name'])
                #     if org['note_ticket__ticket_org_id'] != last_id:
                #         print('IF')
                #         hours = org['labour_hours']
                #         lbr_hours.update({org['note_ticket__ticket_org__org_name']: hours.strftime("%H:%M") })
                #     else:
                #         print('ELSE')
                #         print(org['labour_hours'])
                #         # t1 = lbr_hours[org['note_ticket__ticket_org__org_name']]
                #         # t1 = datetime.strptime(str(t1)+":00", '%H:%M:%S')
                #         # t2 = org['labour_hours']
                #         # t2 = datetime.strptime(str(t2), '%H:%M:%S')
                #         # time_zero = datetime.strptime('00:00:00', '%H:%M:%S')
                #         # print(t1.hour + t2.hour)
                #         # print((t1 - time_zero + t2).hour)
                #         # print((t1 - time_zero + t2).minute)
                #         hours  = org['labour_hours'].hour
                #         # hours  = '40:15:30'
                #         # hours = timedelta(hours=hours.hour, minutes=hours.minute)
                #         print(type(hours))
                #         lbr_hours.update({org['note_ticket__ticket_org__org_name']: hours })
                #     print(lbr_hours)
                #     total_hours += org['labour_hours'].hour
                #     print(total_hours)
                #     total_minutes += org['labour_hours'].minute
                #     last_id = org['note_ticket__ticket_org_id']

                if orgDict:
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'orgDict': orgDict,
                        'total_hours': total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_org_labourhour_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'UserTimes':
                try:
                    user_labour_hours = TicketNote.objects.values('note_ticket__ticket_caller_id',
                                                                  'note_ticket__ticket_caller__display_name',
                                                                  'note_ticket__ticket_caller__last_name',
                                                                  'labour_hours', 'note_created_at').filter(
                        labour_hours__isnull=False).filter(note_ticket__ticket_caller_id__isnull=False).filter(
                        note_created_at__gte=start_date).filter(note_created_at__lte=end_date).order_by(
                        'note_ticket__ticket_caller__display_name')
                except TicketNote.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                hoursList = []
                userhoursList = []
                userDict = {}
                last_id = 0

                for user in user_labour_hours:
                    hoursList.append(user['labour_hours'].strftime("%H:%M:%S"))
                    if last_id != user['note_ticket__ticket_caller__display_name']:
                        if last_id != 0:
                            totalSecs = 0
                            for hours in userhoursList:
                                if (last_id == 'Yasir Shaukat'):
                                    print(user['note_ticket__ticket_caller__display_name'])
                                    print('OK')
                                timeParts = [int(s) for s in hours.split(':')]
                                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                            totalSecs, sec = divmod(totalSecs, 60)
                            hr, min = divmod(totalSecs, 60)
                            userDict[last_id] = "%d:%02d" % (hr, min)
                            userhoursList.clear()
                        userhoursList.append(user['labour_hours'].strftime("%H:%M:%S"))
                    else:
                        userhoursList.append(user['labour_hours'].strftime("%H:%M:%S"))
                    last_id = user['note_ticket__ticket_caller__display_name']

                totalSecs = 0
                for hours in userhoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                userDict[last_id] = "%d:%02d" % (hr, min)

                totalSecs = 0
                for hours in hoursList:
                    timeParts = [int(s) for s in hours.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                total_hours = "%d:%02d" % (hr, min)

                # last_id = 0
                # lbr_hours = {}
                # total_hours = 0
                # total_minutes = 0
                # for user in user_labour_hours:
                #     if user['note_ticket__ticket_caller__display_name'] != last_id:
                #         hours = user['labour_hours']
                #         print()
                #         lbr_hours.update({user['note_ticket__ticket_caller__display_name']: hours.strftime("%H:%M") })
                #     else:
                #         t1 = lbr_hours[user['note_ticket__ticket_caller__display_name']]
                #         t1 = datetime.strptime(str(t1)+":00", '%H:%M:%S')
                #         t2 = user['labour_hours']
                #         t2 = datetime.strptime(str(t2), '%H:%M:%S')
                #         time_zero = datetime.strptime('00:00:00', '%H:%M:%S')
                #         hours  = (t1 - time_zero + t2).time()
                #         lbr_hours.update({user['note_ticket__ticket_caller__display_name']: hours.strftime("%H:%M") })
                #
                #     total_hours += user['labour_hours'].hour
                #     total_minutes += user['labour_hours'].minute
                #     last_id = user['note_ticket__ticket_caller__display_name']

                if userDict:
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'userDict': userDict,
                        'total_hours': total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_user_labourhour_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'OrgTimeOpen':
                try:
                    tickets = Ticket.objects.values('ticket_org__org_name', 'ticket_status', 'ticket_created_at',
                                                    'ticket_id', 'ticket_closed_at').filter(ticket_is_delete=0).filter(
                        ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).order_by(
                        'ticket_org_id')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                last_id = 0
                tot_hours = {}
                g_total_hours = 0
                if tickets:
                    for ticket in tickets:

                        if ticket['ticket_org__org_name'] != last_id:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round((hours) + (minutes / 100), 2)
                            # print("T")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_org__org_name']: total_hours})
                            # print(tot_hours)
                        else:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round(tot_hours[ticket['ticket_org__org_name']] + (hours) + (minutes / 100),
                                                2)
                            # print("S")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_org__org_name']: total_hours})
                            # print(tot_hours)

                        g_total_hours += round(((hours) + (minutes / 100)), 2)
                        # print(g_total_hours)
                        last_id = ticket['ticket_org__org_name']

                if tot_hours:
                    g_total_hours = round(g_total_hours, 2)
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tot_hours': tot_hours,
                        'g_total_hours': g_total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_org_totaltime_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))
            elif report_id == 'UserTimeOpen':
                try:
                    tickets = Ticket.objects.values('ticket_caller__first_name', 'ticket_status', 'ticket_created_at',
                                                    'ticket_id', 'ticket_closed_at').filter(ticket_is_delete=0).filter(
                        ticket_created_at__gte=start_date).filter(ticket_created_at__lte=end_date).order_by(
                        'ticket_caller_id')
                except Ticket.DoesNotExist:
                    messages.error(request, 'Request Failed! No Record Found.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

                last_id = 0
                tot_hours = {}
                g_total_hours = 0
                if tickets:
                    for ticket in tickets:

                        if ticket['ticket_caller__first_name'] != last_id:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round((hours) + (minutes / 100), 2)
                            # print("T")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_caller__first_name']: total_hours})
                            # print(tot_hours)
                        else:
                            if ticket['ticket_status'] == 0:
                                delta = datetime.now(timezone.utc) - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60
                            else:
                                delta = ticket['ticket_closed_at'] - ticket['ticket_created_at']
                                days, seconds = delta.days, delta.seconds
                                hours = days * 24 + seconds // 3600
                                minutes = (seconds % 3600) // 60

                            total_hours = round(
                                tot_hours[ticket['ticket_caller__first_name']] + (hours) + (minutes / 100), 2)
                            # print("S")
                            # print(total_hours)
                            tot_hours.update({ticket['ticket_caller__first_name']: total_hours})
                            # print(tot_hours)

                        g_total_hours += round(((hours) + (minutes / 100)), 2)
                        # print(g_total_hours)
                        last_id = ticket['ticket_caller__first_name']

                if tot_hours:
                    g_total_hours = round(g_total_hours, 2)
                    load_sidebar = get_sidebar(request)

                    context = {
                        'report_id': report_id,
                        'sidebar': load_sidebar,
                        'start_date': datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y'),
                        'end_date': datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y'),
                        'tot_hours': tot_hours,
                        'g_total_hours': g_total_hours,
                        'sort_by': sort_by
                    }

                    return render(request, 'itrak/Reports/summary_report_user_totaltime_result.html', context)

                else:
                    messages.error(request, 'Request Failed! No Record Found.Please try another Date Range.')
                    return redirect("/Home_getReportDateRange?summaryReport=" + str(report_id))

        else:
            return render_to_response('itrak/page-404.html')

    else:
        return render_to_response('itrak/page-404.html')


# Get Summary Report Ticket List End#


# Get Summary Report Result End#

# Get Report Writer Start #

@active_user_required
def reportWriterQueries(request):
    load_sidebar = get_sidebar(request)
    request.session['pair'] = ''
    request.session['selected_fields_array'] = ''
    request.session['unselected_fields_array'] = ''
    request.session['filter_statement'] = ''
    request.session['expressions'] = ''
    request.session['filter_expression_array'] = ''
    request.session['expression_content_array'] = ''
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Reports/report_writer.html', context)


# Get Report Writer End #

# New Query Writer Start #

@active_user_required
def newQuery(request):
    load_sidebar = get_sidebar(request)
    Pairs = DataSetsPair.objects.all()
    # return HttpResponse(Pairs)
    context = {
        'sidebar': load_sidebar,
        'pairs': Pairs,
    }
    if request.session['pair']:
        context['pair_set'] = int(request.session['pair'])
    else:
        request.session['pair'] = ''
        request.session['selected_fields_array'] = ''
        request.session['unselected_fields_array'] = ''
        request.session['filter_statement'] = ''
        request.session['expression'] = ''
        request.session['filter_expression_array'] = ''
        request.session['expression_content_array'] = ''

    return render(request, 'itrak/Reports/new_query.html', context)


# New Query Writer End #

# Get pair Fields Start #

@csrf_exempt
def getPairFields(request):
    if request.is_ajax() and request.method == 'POST':
        fields = DataSetsPairFields.objects.filter(df_pair_id=request.POST.get('data_pair'))
        request.session['pair'] = request.POST.get('data_pair')
        return render(request, 'itrak/Reports/data_pair_fields.html', {'fields': fields})


# Get pair Fields End #
#
#
# Get pair Selected Fields Start #

@csrf_exempt
def getPairSelectedFields(request):
    if request.is_ajax() and request.method == 'POST':
        selectedFields = request.session['selected_fields_array']
        unselectedFields = request.session['unselected_fields_array']
        return render(request, 'itrak/Reports/data_selected_pair_fields.html', {'selecetdFields': selectedFields, 'unselecetdFields': unselectedFields})


# Get pair Selected Fields End #

# Second Query Writer Start #

@active_user_required
def secondQuery(request):
    load_sidebar = get_sidebar(request)
    fields = DataSetsPairFields.objects.filter(df_pair_id=request.session['pair'])

    context = {}
    if request.session['filter_statement']:
        context['filter_statement'] = request.session['filter_statement']
    if request.session['expressions']:
        filter_expression_array = request.session['expressions']
        context['filter_expression_array'] = filter_expression_array
    if request.session['expression_content_array']:
        expression_content_array = request.session['expression_content_array']
        context['expression_content_array'] = zip(expression_content_array, filter_expression_array)
    context['sidebar'] = load_sidebar
    context['fields'] = fields
    return render(request, 'itrak/Reports/new_query2.html', context)


# second Query Writer End #

#  Get FieldsConditions Start #

@csrf_exempt
def getFieldsConditions(request):
    if request.is_ajax() and request.method == 'POST':
        field_type = DataSetsPairFields.objects.values('df_condition_type').filter(
            df_actual_column_name=request.POST.get('field_name')).first()
        conditions = DataSetsFieldsConditions.objects.filter(dc_type=field_type['df_condition_type'])
        options = ['<option value="None"></option>']
        for condition in conditions:
            if 'condition' in request.POST and condition.dc_name == request.POST['condition']:
                options.append('<option value="' + condition.dc_name + '" data-id="' + condition.dc_type_name + '" selected>' + condition.dc_name + '</option>')
            else:
                options.append('<option value="' + condition.dc_name + '" data-id="' + condition.dc_type_name + '">' + condition.dc_name + '</option>')
        return HttpResponse(options)

# Get Fields Conditions End #

#  Set Selected Fields Start #

@csrf_exempt
def setSelectedFields(request):
    if request.is_ajax() and request.method == 'POST':
        request.session['unselected_fields_array'] = request.POST.get('unselected_fields').split(",")
        request.session['selected_fields_array'] = request.POST.get('selected_fields').split(",")
        request.session['filter_statement'] = ''
        request.session['expressions'] = ''
        request.session['filter_expression_array'] = ''
        request.session['expression_content_array'] = ''
        return HttpResponse(request.session['selected_fields_array'])

# Set Selected Fields End #

# Third Query Writer Start #

@active_user_required
def thirdQuery(request):
    load_sidebar = get_sidebar(request)
    users = User.objects.values('id','first_name','last_name').filter(is_delete=0)
    # for key, value in request.session.items():
    #     print('{} => {}'.format(key, value))

    expression_content_array = request.session['expression_content_array']
    filter_expression_array = request.session['filter_expression_array']
    filter_statement = request.session['filter_statement'].split(" ") if request.session['filter_statement'] else ''
    selected_fields = request.session['selected_fields_array']
    selected_columns = []
    argument_list = []
    conditiondict = {
        "=": "exact",
        "<>": "exact",
        "In": "in",
        "Not In": "in",
        "Like": "contains",
        "Not Like": "contains",
        "Is Blank": "exact",
        "Is Not Blank": "exact",
        "Is Null": "isnull",
        "Is Not Null": "isnull",
        "Is True": "exact",
        "Is False": "exact",
        ">": "gt",
        "<": "lt",
        ">=": "gte",
        "<=": "lte",
        "Starts with": "startswith",
        "Starts Not with": "startswith",
        "Today": "range",
        "Yesterday": "range",
        "Tomorrow": "range",
        "This Week": "range",
        "Last Week": "range",
        "Next Week": "range",
        "This Month": "range",
        "Last Month": "range",
        "Next Month": "range",
        "This Year": "range",
        "Last Year": "range",
        "Next Year": "range",
        "Custom Date Range": "range"
    }

    for field in selected_fields:
        try:
            actual_field = DataSetsPairFields.objects.only('df_actual_column_name').get(df_name=field).df_actual_column_name
        except:
            return render_to_response('itrak/page-404.html')
        selected_columns.append(actual_field)

    print(filter_statement)
    print(filter_expression_array)
    counter = 0
    filter_operator = 'and'
    query_commit = 0
    query_not_commit = 0
    test = []
    kwargs = {}
    test1 = ''

    if filter_statement:
        if len(filter_statement) == 1:
            for key in filter_statement:
                try:
                    if len(key) == 1:
                        expression = filter_expression_array[key]
                        modelName = expression['modelName']
                        modelAttr = expression['modelAttr']
                        condition = expression['condition']
                        fieldValue = expression['fieldValue']
                        fieldLabel = expression['fieldLabel']

                        modelInstance = apps.get_model('itrak', modelName)
                        finalquery = modelInstance.objects.values(*tuple(selected_columns)).filter()
                        if condition == '<>' or condition == 'Not In' or condition == 'Not Like' or condition == 'Is Not Blank' or condition == 'Is Not Null' or condition == 'Is False' or condition == 'Starts Not with':
                            argument_list.append(~Q(**{modelAttr + '__' + conditiondict[condition]: fieldValue}))
                        else:
                            argument_list.append(Q(**{modelAttr + '__' + conditiondict[condition]: fieldValue}))
                        finalquery = finalquery.filter(reduce(operator.and_, argument_list))
                    else:
                        return render_to_response('itrak/page-404.html')
                except:
                    return render_to_response('itrak/page-404.html')
        else:
            for key in filter_statement:
                print(key)
                print(filter_operator)
                # try:
                if len(key) == 1:
                    print(key)
                    print(filter_expression_array[key])
                    expression = filter_expression_array[key]
                    modelName = expression['modelName']
                    modelAttr = expression['modelAttr']
                    condition = expression['condition']
                    fieldValue = expression['fieldValue']
                    fieldLabel = expression['fieldLabel']

                    print(modelName)
                    print(modelAttr)
                    print(condition)
                    print(fieldValue)
                    print(fieldLabel)
                    modelInstance = apps.get_model('itrak', modelName)
                    if counter == 0:
                        finalquery = modelInstance.objects.values(*tuple(selected_columns)).filter()
                    if query_not_commit == 0:
                        if condition == '<>' or condition == 'Not In' or condition == 'Not Like' or condition == 'Is Not Blank' or condition == 'Is Not Null' or condition == 'Is False' or condition == 'Starts Not with':
                            argument_list.append(~Q(**{modelAttr + '__'+conditiondict[condition]:fieldValue}))
                        else:
                            argument_list.append(Q(**{modelAttr + '__'+conditiondict[condition]:fieldValue}))
                    elif query_not_commit == 1:
                        query_not_commit == 0
                        if condition == '<>' or condition == 'Not In' or condition == 'Not Like' or condition == 'Is Not Blank' or condition == 'Is Not Null' or condition == 'Is False' or condition == 'Starts Not with':
                            argument_list.append(Q(**{modelAttr + '__'+conditiondict[condition]:fieldValue}))
                        else:
                            argument_list.append(~Q(**{modelAttr + '__'+conditiondict[condition]:fieldValue}))

                    kwargs.update({
                        '{0}__{1}'.format(modelAttr, conditiondict[condition]): fieldValue,
                    })

                    test.append(Q(**kwargs))

                    counter = counter + 1
                    if filter_operator == 'or' and query_commit == 1:
                        print('ORRRRRR')
                        argument_list.append(test1)
                        print(argument_list[0].__or__(argument_list[1]))
                        test1 = argument_list[0].__or__(argument_list[1])
                        print(argument_list)
                        print(argument_list)
                        # finalquery = finalquery.filter(reduce(operator.or_, argument_list))
                        argument_list.clear()
                    elif filter_operator == 'and' and query_commit == 1:
                        print('ANDDDDDDDDDDDDD')
                        print(reduce(operator.and_, argument_list))
                        # test1 = reduce(operator.and_, argument_list)
                        test1 = argument_list[0].__and__(argument_list[1])
                        print(test1)
                        print(argument_list)
                        # finalquery = finalquery.filter(reduce(operator.and_, argument_list))
                        argument_list.clear()
                elif key.lower() == 'and' or key.lower() == 'or':
                    filter_operator = key.lower()
                    test.append(' | ')
                    query_commit = 1
                    print(filter_operator)
                elif key.lower() == 'not':
                    query_not_commit = 1
                else:
                    return render_to_response('itrak/page-404.html')
                # except:
                #     return render_to_response('itrak/page-404.html')
            print(test)
            for i in test:
                print(i)
            print(test[0].__and__(test[2]).__or__(test[4]))
            finalquery = finalquery.filter(test1)
    else:
        print(selected_columns)
        print(selected_columns[0])
        try:
            modelName = DataSetsPairFields.objects.only('df_primary_table_name').get(df_actual_column_name=selected_columns[0]).df_primary_table_name
        except:
            return render_to_response('itrak/page-404.html')
        modelInstance = apps.get_model('itrak', modelName)
        finalquery = modelInstance.objects.values(*tuple(selected_columns)).filter()

    print(finalquery.query)
    print(finalquery)


    context = {
        'sidebar': load_sidebar,
        'users': users,
        'selected_fields': selected_fields,
        'records': finalquery
    }
    return render(request, 'itrak/Reports/new_query3.html', context)

# Third Query Writer End #

# Set Filters Start #

@csrf_exempt
def setFilters(request):
    if request.is_ajax() and request.method == 'POST':
        if request.POST.get('expression'):
            filter_expression = request.POST.get('expression').split("^")
            expression_content = request.POST.get('expression_content').split("|")
            expressions = []
            for exp in filter_expression:
                temp = exp.split("del\xa0\xa0\xa0")
                expressions.append(temp[1])
            request.session['expressions'] = expressions
            request.session['expression_content_array'] = expression_content
            filter_expression_array = {}
            for filter_exp in expression_content:
                filter_exp_dict = {}
                split_expression = filter_exp.split("',")
                field = split_expression[0].replace("'", "")
                filter_exp_dict['modelName'] = field.split(",")[1]
                filter_exp_dict['modelAttr'] = field.split(",")[0]
                filter_exp_dict['condition'] = split_expression[1].replace("'", "")
                filter_exp_dict['fieldValue'] = split_expression[2].replace("'", "")
                try:
                    fieldType = DataSetsPairFields.objects.only('df_condition_type').get(df_actual_column_name=filter_exp_dict['modelAttr']).df_condition_type
                except:
                    return render_to_response('itrak/page-404.html')
                # if (fieldType == '2' or fieldType == '4') and (filter_exp_dict['condition'] != 'In' or filter_exp_dict['condition'] != 'Not In'):
                #     filter_exp_dict['fieldValue'] = split_expression[2]+"'"
                if (filter_exp_dict['condition'] == 'In' or filter_exp_dict['condition'] == 'Not In'):
                    field_values_in = split_expression[2].replace("'", "")
                    filter_exp_dict['fieldValue'] = field_values_in.split(',')
                    print(filter_exp_dict['fieldValue'])
                    # filter_exp_dict['fieldValue'] = (','.join("'" + item + "'" for item in filter_exp_dict['fieldValue']))
                    # filter_exp_dict['fieldValue'] = list(filter_exp_dict['fieldValue'].split(","))
                if (fieldType == '2') and (filter_exp_dict['condition'] == 'Is Blank' or filter_exp_dict['condition'] == 'Is Not Blank'):
                    filter_exp_dict['fieldValue'] = ''
                if (fieldType == '1' or fieldType == '3' or fieldType == '4') and (filter_exp_dict['condition'] == 'Is Blank' or filter_exp_dict['condition'] == 'Is Not Blank' or filter_exp_dict['condition'] == 'Is True' or filter_exp_dict['condition'] == 'Is False'):
                    if (filter_exp_dict['condition'] == 'Is Blank' or filter_exp_dict['condition'] == 'Is Not Blank'):
                        filter_exp_dict['condition'] = 'Is Null' if filter_exp_dict['condition'] == 'Is Blank' else 'Is Not Null'
                    filter_exp_dict['fieldValue'] = 'True' if (filter_exp_dict['condition'] == 'Is Blank' or filter_exp_dict['condition'] == 'Is Not Blank') else 1
                if (fieldType == '4') and (filter_exp_dict['condition'] != 'Is Blank' and filter_exp_dict['condition'] != 'Is Not Blank' and filter_exp_dict['condition'] != 'Is Null' and filter_exp_dict['condition'] != 'Is Not Null'):
                    if filter_exp_dict['condition'] == '=' or filter_exp_dict['condition'] == '<>' or filter_exp_dict['condition'] == '<' or filter_exp_dict['condition'] == '>' or filter_exp_dict['condition'] == '>=' or filter_exp_dict['condition'] == '<=':
                        filter_exp_dict['fieldValue'] = datetime.strptime(filter_exp_dict['fieldValue'],'%m/%d/%Y').strftime('%Y-%m-%d')
                    else:
                        start_date = datetime.strptime(filter_exp_dict['fieldValue'].split(' - ')[0], '%m/%d/%Y').strftime('%Y-%m-%d')
                        end_date = datetime.strptime(filter_exp_dict['fieldValue'].split(' - ')[1] + " 23:59:59",'%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        filter_exp_dict['fieldValue'] = start_date+' - '+end_date
                        filter_exp_dict['fieldValue'] = filter_exp_dict['fieldValue'].split(' - ')
                    if filter_exp_dict['condition'] == '=':
                        filter_exp_dict['condition'] = 'Starts with'
                    elif filter_exp_dict['condition'] == '<>':
                        filter_exp_dict['condition'] = 'Starts Not with'
                    # print(filter_exp_dict['condition'])
                    # print(filter_exp_dict['fieldValue'])
                filter_exp_dict['fieldLabel'] = split_expression[3].split(",")[1]
                filter_expression_array[filter_exp_dict['fieldLabel'].replace("'", "")] = filter_exp_dict
            request.session['filter_expression_array'] = filter_expression_array
            request.session['filter_statement'] = request.POST.get('statement')
            return HttpResponse(expressions)
        return HttpResponse(1)

# Set Filters End #
