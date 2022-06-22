from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, request, response
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
import time
from django.utils import timezone
import pandas as pd
from pytz import timezone as pytz_timezone
from django.db import connection
from functools import wraps
user_login_required = user_passes_test(lambda user: user.is_active, login_url='/') #Here user_passes_test decorator designates the user is active.

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


@login_required
def dashboardSettings(request):
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    user_id = request.user.id
    panel_left = DashboardSettings.objects.values('d_panel__panelGraph_text','d_panel__panelGraph_url','d_column_side','d_setting_id','d_expanded','d_data_display').filter(d_user_id=user_id).filter(d_column_side=0)
    panel_right = DashboardSettings.objects.values('d_panel__panelGraph_text','d_panel__panelGraph_url','d_column_side','d_setting_id','d_expanded','d_data_display').filter(d_user_id=user_id).filter(d_column_side=1)
    p_left = DashboardSettings.objects.filter(d_user_id=user_id).filter(d_column_side=0).count()
    p_right = DashboardSettings.objects.filter(d_user_id=user_id).filter(d_column_side=1).count()
    first_text = PanelGraph.objects.exclude(pk__in=
    DashboardSettings.objects.filter(d_user_id=request.user.id).values_list('d_panel_id', flat=True)).values_list('panelGraph_text').first()
    first_url = PanelGraph.objects.exclude(pk__in=
    DashboardSettings.objects.filter(d_user_id=request.user.id).values_list('d_panel_id', flat=True)).values_list('panelGraph_url').first()

    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'panel_left': panel_left,
        'panel_right': panel_right,
        'p_left': p_left,
        'p_right': p_right,
        'first_text':first_text,
        'first_url':first_url,
        'domain': request.META['HTTP_HOST']
    }
    # return HttpResponse(graphPanels)
    return render(request, 'itrak/DashboardSettings/dashboard_settings.html', context)

@csrf_exempt
def systemOverview(request):
    # Get User Type
    user_type = userType(request) 
    user_id = request.user.id
    org_id = request.user.user_org_id
    # accountsList = getMappedUserIDsWithCurrentUer(request)
    # accountsList = tuple(accountsList)
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        
        if user == 'Assigned Tickets':
            # kwargs = Q(ticket_assign_to_id=user_id)
            # tickets = Ticket.objects.filter(ticket_assign_to__isnull=False).filter(ticket_is_delete=0).filter(ticket_status=0).filter(kwargs)
            if user_type == 'superadmin':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                """
            elif user_type == 'agent':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0 
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                """
            elif user_type == 'manager':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                """
            elif user_type == 'enduser':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                        OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                        OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user == 'Unassigned Tickets':
            # tickets = Ticket.objects.filter(ticket_assign_to__isnull=True).filter(ticket_is_delete=0).filter(ticket_status=0)
            if user_type == 'superadmin':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NULL 
                    AND tic.ticket_is_delete = 0 
                    AND tic.ticket_status = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                """
            if user_type == 'agent':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NULL 
                    AND tic.ticket_is_delete = 0 
                    AND tic.ticket_status = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                """
            if user_type == 'manager':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NULL 
                    AND tic.ticket_is_delete = 0 
                    AND tic.ticket_status = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                """
            if user_type == 'enduser':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NULL 
                    AND tic.ticket_is_delete = 0 
                    AND tic.ticket_status = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                   AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                        OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                        OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user == 'Open Tickets':
            # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
            # tickets = Ticket.objects.filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs)
            if user_type == 'superadmin':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'  
                """
            elif user_type == 'agent':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'  
                """
            elif user_type == 'manager':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )

                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                """
            elif user_type == 'enduser':
                SQL  = """
                    SELECT tic.ticket_id
                        ,tic.ticket_status
                        ,tic.submitted_at
                        ,tic.ticket_modified_at
                        ,tic.subject
                        ,(
                            select pri.priority_name
                            from AT_Priority pri
                            where pri.priority_id = tic.priority_id
                        ) as priority
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_type_id
                        ) as ticket_type
                        ,(
                            select tt.ttype_name
                            from AT_TicketType tt
                            where tt.ttype_id = tic.ticket_subtype1_id
                        ) as ticket_subtype1
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_next_action_id
                        ) as ticket_next_action
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_assign_to_id
                        ) as ticket_assign_to
                        ,(
                            select au.display_name
                            from AT_Users au
                            where au.id = tic.ticket_caller_id
                        ) as ticket_caller
                        ,(
                            select sub_status_text
                            from AT_SubStatus ss
                            where ss.sub_status_id =  tic.ticket_sub_status_id
                        ) as ticket_sub_status
                    FROM AT_Tickets tic 
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                        OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                        OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'System Overview'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id)
        # assigned_tickets = Ticket.objects.filter(ticket_assign_to__isnull=False).filter(ticket_is_delete=0).filter(ticket_status=0).filter(kwargs)
        # unassigned_tickets = Ticket.objects.filter(ticket_assign_to__isnull=True).filter(ticket_is_delete=0).filter(ticket_status=0)
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # open_tickets = Ticket.objects.filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs)
        
        
        if user_type == 'superadmin':
            SQL  = """
                select 
                (
                    SELECT count(*) 
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                ) as assigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic
                    WHERE tic.[ticket_assign_to_id] IS NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                ) as unassigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                ) as open_tickets
            """
        elif user_type == 'agent':
            SQL  = """
                select 
                (
                    SELECT count(*) 
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0 
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    ) 
                ) as assigned_tickets
                ,(
                    SELECT count(*)  
                    FROM AT_Tickets tic 
                    WHERE tic.[ticket_assign_to_id] IS NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                ) as unassigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                ) as open_tickets
            """
        elif user_type == 'manager':
            SQL  = """
                select 
                (
                    SELECT count(*) 
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                        AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    )>0
                ) as assigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NULL 
                    AND tic.ticket_is_delete = 0 
                    AND tic.ticket_status = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                        AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    )>0
                ) as unassigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                ) as open_tickets
            """
        elif user_type == 'enduser':
            SQL  = """
                select 
                (
                    SELECT count(*) 
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NOT NULL 
                    AND tic.[ticket_is_delete] = 0 
                    AND tic.[ticket_status] = 0 
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                        OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                        OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                ) as assigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic 
                    WHERE tic.ticket_assign_to_id IS NULL 
                    AND tic.ticket_is_delete = 0 
                    AND tic.ticket_status = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""'
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                        OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                        OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                ) as unassigned_tickets
                ,(
                    SELECT count(*)
                    FROM AT_Tickets tic
                    WHERE 
                    (
                        tic.[ticket_status] = 0 
                        OR tic.[ticket_status] = 2
                    ) 
                    AND tic.[ticket_is_delete] = 0
                    AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                    AND tic.account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = tic.ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                        OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                        OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                ) as open_tickets
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        result = dictfetchall(cursor)
        assigned_tickets = result[0]['assigned_tickets']
        unassigned_tickets = result[0]['unassigned_tickets']
        open_tickets = result[0]['open_tickets']
        

        labels = ['Assigned Tickets', 'Open Tickets', 'Unassigned Tickets']
        values = [assigned_tickets, open_tickets, unassigned_tickets]
        retValues = {'Category': labels, 'Count': values}
        return JsonResponse(retValues)

@csrf_exempt
def openTicketsByTicketType(request):
    # Get User Type
    user_type = userType(request) 
    user_id = request.user.id
    org_id = request.user.user_org_id
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        if user_type == 'superadmin':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""'
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_type__has_parent=0).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_type__ttype_name=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Ticket Type'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_type__ttype_name').filter(ticket_type__has_parent=0).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))

        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT tt.ttype_name as ticket_type__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM [AT_Tickets] tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                GROUP BY tt.ttype_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT tt.ttype_name as ticket_type__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM [AT_Tickets] tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY tt.ttype_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT tt.ttype_name as ticket_type__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM [AT_Tickets] tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )

                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                GROUP BY tt.ttype_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT tt.ttype_name as ticket_type__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM [AT_Tickets] tic
                INNER JOIN AT_TicketType tt ON tic.ticket_type_id = tt.ttype_id
                WHERE tt.has_parent = 0
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )

                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY tt.ttype_name
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []
        for ticket in tickets:
            labels.append(ticket['ticket_type__ttype_name'])
            values.append(ticket['tcount'])
        retValues = {'Ticket Type': labels, 'Count': values}
        return JsonResponse(retValues)

@csrf_exempt
def openTicketsBySubtype(request):
    # Get User Type
    user_type = userType(request) 
    user_id = request.user.id
    org_id = request.user.user_org_id
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_subtype1_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_subtype1__ttype_name=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'  
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'   
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'   
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tt.ttype_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Subtype'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_subtype1__ttype_name').filter(ticket_subtype1_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT tt.ttype_name as ticket_subtype1__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'   
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                GROUP BY tt.ttype_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT tt.ttype_name as ticket_subtype1__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'   
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY tt.ttype_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT tt.ttype_name as ticket_subtype1__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'   
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                GROUP BY tt.ttype_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT tt.ttype_name as ticket_subtype1__ttype_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_TicketType tt ON (tic.ticket_subtype1_id = tt.ttype_id) 
                WHERE tic.ticket_subtype1_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'   
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY tt.ttype_name
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_subtype1__ttype_name'])
            values.append(ticket['tcount'])
        retValues = {'Subtype': labels, 'Count': values}

        return JsonResponse(retValues)


@csrf_exempt
def openTicketsBySubstatus(request):
    # Get User Type
    user_type = userType(request) 
    user_id = request.user.id
    org_id = request.user.user_org_id
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_sub_status__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_sub_status__sub_status_text=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""'
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND sta.sub_status_text = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND sta.sub_status_text = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND sta.sub_status_text = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND sta.sub_status_text = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Substatus'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_sub_status__sub_status_text').filter(ticket_sub_status__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        # return HttpResponse(tickets.query)

        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT sta.sub_status_text as ticket_sub_status__sub_status_text, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                GROUP BY sta.sub_status_text
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT sta.sub_status_text as ticket_sub_status__sub_status_text, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY sta.sub_status_text
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT sta.sub_status_text as ticket_sub_status__sub_status_text, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.user_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                GROUP BY sta.sub_status_text
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT sta.sub_status_text as ticket_sub_status__sub_status_text, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_SubStatus sta ON tic.ticket_sub_status_id = sta.sub_status_id 
                WHERE tic.ticket_sub_status_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY sta.sub_status_text
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_sub_status__sub_status_text'])
            values.append(ticket['tcount'])
        retValues = {'Substatus': labels, 'Count': values}

        return JsonResponse(retValues)


@csrf_exempt
def openTicketsByPriority(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(priority_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(priority__priority_name=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND pri.priority_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND pri.priority_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """ 
        elif user_type == 'manager':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND pri.priority_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND pri.priority_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Priority'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('priority__priority_name').filter(priority_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT pri.priority_name as priority__priority_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                GROUP BY pri.priority_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT pri.priority_name as priority__priority_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY pri.priority_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT pri.priority_name as priority__priority_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                GROUP BY pri.priority_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT pri.priority_name as priority__priority_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Priority pri ON tic.priority_id = pri.priority_id 
                WHERE tic.priority_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY pri.priority_name
            """
        
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        
        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['priority__priority_name'])
            values.append(ticket['tcount'])
        retValues = {'Priority': labels, 'Count': values}

        return JsonResponse(retValues)


@csrf_exempt
def openTicketsByOrganization(request):
    global_user = isGlobalUser(request)
    user_id = request.user.id
    org_id = request.user.user_org_id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_org_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_org__org_name=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL 
                AND tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                )
                AND org.org_name = '"""+str(user)+"""'
                AND tic.ticket_is_delete = 0 
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""'  """
                SQL = SQL+by_org
        elif user_type == 'agent':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL 
                AND tic.account_id IS NOT NULL
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                )
                AND org.org_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_is_delete = 0 
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' """
                SQL = SQL+by_org
        elif user_type == 'manager':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL
                AND tic.account_id IS NOT NULL
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND org.org_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND tic.ticket_is_delete = 0 
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' """
                SQL = SQL+by_org
        elif user_type == 'enduser':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL 
                AND tic.account_id IS NOT NULL
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND org.org_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' """
                SQL = SQL+by_org

        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Organization'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_org__org_name').filter(ticket_org_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT org.org_name as ticket_org__org_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' GROUP BY org.org_name """
                SQL = SQL+by_org
            else:
                group_by = """ GROUP BY org.org_name """
                SQL = SQL+group_by
        elif user_type == 'agent':
            SQL  = """
                SELECT org.org_name as ticket_org__org_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL
                AND tic.ticket_org_id =  '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                )
                AND tic.ticket_is_delete = 0
                
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' GROUP BY org.org_name """
                SQL = SQL+by_org
            else:
                group_by = """ GROUP BY org.org_name """
                SQL = SQL+group_by
        elif user_type == 'manager':
            SQL  = """
                SELECT org.org_name as ticket_org__org_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND tic.ticket_is_delete = 0
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' GROUP BY org.org_name """
                SQL = SQL+by_org
            else:
                group_by = """ GROUP BY org.org_name """
                SQL = SQL+group_by
        elif user_type == 'enduser':
            SQL  = """
                SELECT org.org_name as ticket_org__org_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN AT_Organizations org ON tic.[ticket_org_id] = org.org_id 
                WHERE tic.ticket_org_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
            if request.user.user_type_slug != global_user:
                by_org = """AND tic.ticket_org_id =  '"""+str(org_id)+"""' GROUP BY org.org_name """
                SQL = SQL+by_org
            else:
                group_by = """ GROUP BY org.org_name """
                SQL = SQL+group_by
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_org__org_name'])
            values.append(ticket['tcount'])
        retValues = {'Organization': labels, 'Count': values}

        return JsonResponse(retValues)


@csrf_exempt
def openTicketsByAccount(request):
    user_id = request.user.id
    # Get User Type
    org_id = request.user.user_org_id
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_client_id__isnull=False).filter(ticket_client__client_name=user).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL  = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND acc.acc_name = '"""+str(user)+"""'
                AND T.ticket_is_delete = 0 
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL 
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND acc.acc_name = '"""+str(user)+"""'
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL 
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND acc.acc_name = '"""+str(user)+"""'
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL
                AND T.ticket_org_id = '"""+str(org_id)+"""'  
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND acc.acc_name = '"""+str(user)+"""'
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Account'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        if user_type == 'superadmin':
            SQL  = """
                SELECT acc.acc_name as ticket_client__client_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL
                AND T.ticket_org_id = '"""+str(org_id)+"""'  
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                GROUP BY acc.acc_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT acc.acc_name as ticket_client__client_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL
                AND T.ticket_org_id = '"""+str(org_id)+"""'  
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY acc.acc_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT acc.acc_name as ticket_client__client_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL
                AND T.ticket_org_id = '"""+str(org_id)+"""'  
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                GROUP BY acc.acc_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT acc.acc_name as ticket_client__client_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN GlobalACCTS acc ON T.account_id = acc.id
                WHERE T.account_id IS NOT NULL 
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY acc.acc_name
            """

        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        
        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_client__client_name'])
            values.append(ticket['tcount'])
        retValues = {'Account': labels, 'Count': values}

        return JsonResponse(retValues)

@csrf_exempt
def availableTasksByAssignee(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        # return HttpResponse(request.POST['user'])
        user = request.POST['user']
        # ticket_lists = get_task_mgr_ticket_list(user_id)
        # tickets = TaskManager.objects.filter(task_assigned_to__isnull=False).filter(tmgr_ticket__isnull=False).filter(tmgr_is_complete=0).filter(task_assigned_to__display_name=user).filter(tmgr_is_delete=0).filter(tmgr_ticket_id__in=ticket_lists).annotate(tcount=Count('tmgr_task_id'))
        # tickets = TaskManager.objects.filter(task_assigned_to__isnull=False).filter(tmgr_ticket__isnull=False).filter(task_assigned_to__display_name=user).annotate(tcount=Count('tmgr_task_id'))
        if user_type == 'superadmin':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""' 
                AND T.ticket_org_id  = '"""+str(org_id)+"""' 
                AND U.display_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""'  
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""' 
                AND U.user_type = 1 -- End User
                AND T.account_id in (
                    select distinct account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0 
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""' 
                AND U.display_name = '"""+str(user)+"""'
                AND U.user_type = 1 -- End User
                AND T.account_id in (
                    select distinct account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        context = {
            'tickets': tickets,
            'title': 'Available Tasks By Assignee'
        }
        return render(request, 'itrak/DashboardSettings/get_record_task.html', context)
    else:
        if user_type == 'superadmin':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    count(TM.tmgr_task_id) AS tcount
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0 
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""' 
                GROUP BY U.display_name
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user_type == 'agent':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    count(TM.tmgr_task_id) AS tcount
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                GROUP BY U.display_name
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user_type == 'manager':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    count(TM.tmgr_task_id) AS tcount
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""'  
                AND U.user_type = 1 --End User
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                GROUP BY U.display_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    count(TM.tmgr_task_id) AS tcount
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0 
                AND TM.tmgr_org_id  = '"""+str(org_id)+"""'
                AND T.ticket_org_id  = '"""+str(org_id)+"""' 
                AND U.user_type = 1 --End User
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY U.display_name
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['task_assigned_to__display_name'])
            values.append(ticket['tcount'])
        retValues = {'Assignee': labels, 'Count': values}

        return JsonResponse(retValues)

@csrf_exempt
def openTasksByAssignee(request):
    user_id = request.user.id
    # Get User Type
    user_type = userType(request) 
    org_id = request.user.user_org_id   
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # ticket_lists = get_task_mgr_ticket_list(user_id)
        # tickets = TaskManager.objects.filter(task_assigned_to__isnull=False).filter(tmgr_ticket__isnull=False).filter(tmgr_is_complete=0).filter(task_assigned_to__display_name=user).filter(tmgr_is_delete=0).filter(tmgr_ticket_id__in=ticket_lists).annotate(tcount=Count('tmgr_task_id'))
        # return HttpResponse(tickets.query)
        if user_type == 'superadmin':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""'  
                AND U.display_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT TM.task_due_date
                    ,TM.task_note
                    ,TM.tmgr_ticket_id
                    ,(
                        select t.task_description
                        from AT_Task t
                        where t.task_id = TM.tmgr_task_id
                    ) as task_description
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tasks By Assignee'
        }
        return render(request, 'itrak/DashboardSettings/get_record_task.html', context)
    else:
        if user_type == 'superadmin':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    Count(TM.tmgr_task_id) AS [tcount] 
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                GROUP BY U.display_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    Count(TM.tmgr_task_id) AS [tcount] 
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY U.display_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    Count(TM.tmgr_task_id) AS [tcount] 
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User 
                GROUP BY U.display_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT U.display_name as task_assigned_to__display_name, 
                    Count(TM.tmgr_task_id) AS [tcount] 
                FROM AT_TaskManager TM
                INNER JOIN [AT_Users] U ON TM.task_assigned_to_id = U.id
                INNER JOIN AT_Tickets T ON TM.tmgr_ticket_id = T.ticket_id 
                WHERE TM.task_assigned_to_id IS NOT NULL 
                AND TM.tmgr_ticket_id IS NOT NULL 
                AND TM.tmgr_is_complete = 0 
                AND TM.tmgr_is_delete = 0 
                AND T.ticket_status = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User 
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY U.display_name
            """
            
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []
        for ticket in tickets:
            labels.append(ticket['task_assigned_to__display_name'])
            values.append(ticket['tcount'])
        retValues = {'Assignee': labels, 'Count': values}

        return JsonResponse(retValues)

@csrf_exempt
def openTicketsByDeptAssigned(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        # tickets = Ticket.objects.filter(ticket_assign_to__isnull=False).filter(ticket_assign_to__user_dep__isnull=False).filter(ticket_assign_to__user_dep__dep_name=user).filter(ticket_is_delete=0).filter(ticket_status=0).annotate(tcount=Count('ticket_id'))
        # return HttpResponse(tickets.query)
        if user_type == 'superadmin':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND dep.dep_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.dep_name = '"""+str(user)+"""'
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.dep_name = '"""+str(user)+"""'
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND usr.user_type = 1 -- End User
            """
        elif user_type == 'enduser':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.dep_name = '"""+str(user)+"""'
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND usr.user_type = 1 -- End User
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets by Assigned Department'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT dep.dep_name as ticket_assign_to__user_dep__dep_name, 
                    count(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                GROUP BY dep.dep_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT dep.dep_name as ticket_assign_to__user_dep__dep_name, 
                    count(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY dep.dep_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT dep.dep_name as ticket_assign_to__user_dep__dep_name, 
                    count(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND usr.user_type = 1 -- User
                GROUP BY dep.dep_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT dep.dep_name as ticket_assign_to__user_dep__dep_name, 
                    count(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic 
                INNER JOIN AT_Users usr ON tic.ticket_assign_to_id = usr.id 
                INNER JOIN AT_Departments dep ON usr.user_dep_id = dep.dep_id
                WHERE 1=1
                AND tic.ticket_assign_to_id IS NOT NULL 
                AND usr.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0
                AND usr.user_org_id  = '"""+str(org_id)+"""'
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""'  
                AND tic.ticket_status = 0
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND usr.user_type = 1 -- User
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY dep.dep_name
            """

        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_assign_to__user_dep__dep_name'])
            values.append(ticket['tcount'])
        retValues = {'Assigned Department': labels, 'Count': values}

        return JsonResponse(retValues)

@csrf_exempt
def openTicketsByDeptSubmitting(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # return HttpResponse(user)
        # tickets = Ticket.objects.filter(ticket_caller__isnull=False).filter(ticket_caller__user_dep__dep_name=user).filter(ticket_caller__user_dep__isnull=False).filter(ticket_is_delete=0).filter(ticket_status=0).annotate(tcount=Count('ticket_id'))
        # return HttpResponse(tickets.query)
        if user_type == 'superadmin':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic INNER JOIN AT_Users U ON tic.ticket_caller_id = U.id
                INNER JOIN AT_Departments dep ON U.user_dep_id = dep.dep_id 
                WHERE tic.ticket_caller_id IS NOT NULL 
                AND U.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.user_org_id  = '"""+str(org_id)+"""' 
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND dep.dep_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic INNER JOIN AT_Users U ON tic.ticket_caller_id = U.id
                INNER JOIN AT_Departments dep ON U.user_dep_id = dep.dep_id 
                WHERE tic.ticket_caller_id IS NOT NULL 
                AND U.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND dep.dep_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager' or user_type == 'enduser':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic INNER JOIN AT_Users U ON tic.ticket_caller_id = U.id
                INNER JOIN AT_Departments dep ON U.user_dep_id = dep.dep_id 
                WHERE tic.ticket_caller_id IS NOT NULL 
                AND U.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND dep.dep_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
            """
        
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets by Submitting Department'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT dep.dep_name as ticket_caller__user_dep__dep_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic INNER JOIN AT_Users U ON tic.ticket_caller_id = U.id
                INNER JOIN AT_Departments dep ON U.user_dep_id = dep.dep_id 
                WHERE tic.ticket_caller_id IS NOT NULL 
                AND U.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                GROUP BY dep.dep_name
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user_type == 'agent':
            SQL  = """
                SELECT dep.dep_name as ticket_caller__user_dep__dep_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic INNER JOIN AT_Users U ON tic.ticket_caller_id = U.id
                INNER JOIN AT_Departments dep ON U.user_dep_id = dep.dep_id 
                WHERE tic.ticket_caller_id IS NOT NULL 
                AND U.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                GROUP BY dep.dep_name
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user_type == 'manager' or user_type == 'enduser':
            SQL  = """
                SELECT dep.dep_name as ticket_caller__user_dep__dep_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic INNER JOIN AT_Users U ON tic.ticket_caller_id = U.id
                INNER JOIN AT_Departments dep ON U.user_dep_id = dep.dep_id 
                WHERE tic.ticket_caller_id IS NOT NULL 
                AND U.user_dep_id IS NOT NULL 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_status = 0
                AND dep.user_org_id  = '"""+str(org_id)+"""'
                AND tic.ticket_org_id  = '"""+str(org_id)+"""' 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                GROUP BY dep.dep_name
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        # tickets = Ticket.objects.values('ticket_caller__user_dep__dep_name').filter(ticket_caller__isnull=False).filter(ticket_caller__user_dep__isnull=False).filter(ticket_is_delete=0).filter(ticket_status=0).annotate(tcount=Count('ticket_id'))
        # return HttpResponse(tickets)
        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_caller__user_dep__dep_name'])
            values.append(ticket['tcount'])
        retValues = {'Submitting Department': labels, 'Count': values}

        return JsonResponse(retValues)


@csrf_exempt
def openTicketsByAssignee(request):
    org_id = request.user.user_org_id
    user_id = request.user.id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # user = user.split(',')
        # fName = user[0]
        # lName = user[1]
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_assign_to__isnull=False).filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_assign_to__display_name=user).filter(ticket_is_delete=0).filter(kwargs).\
            # annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND T.ticket_org_id = '"""+str(org_id)+"""'
            """
        elif user_type == 'agent':
            SQL = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND T.ticket_org_id = '"""+str(org_id)+"""'
            """
        elif user_type == 'manager':
            SQL = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND T.ticket_org_id = '"""+str(org_id)+"""'
            """
        elif user_type == 'enduser':
            SQL = """
                SELECT T.ticket_id
                    ,T.ticket_status
                    ,T.submitted_at
                    ,T.ticket_modified_at
                    ,T.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = T.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = T.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = T.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  T.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                AND T.ticket_org_id = '"""+str(org_id)+"""'
            """
        
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Assignee',
            'name':True
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        if user_type == 'superadmin':
            SQL = """
                SELECT U.display_name as ticket_assign_to__display_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id = '"""+str(org_id)+"""' 
                GROUP BY U.display_name
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT U.display_name as ticket_assign_to__display_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND T.ticket_org_id = '"""+str(org_id)+"""'
                GROUP BY U.display_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT U.display_name as ticket_assign_to__display_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND T.ticket_org_id = '"""+str(org_id)+"""'
                GROUP BY U.display_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT U.display_name as ticket_assign_to__display_name, 
                    count(T.ticket_id) AS [tcount] 
                FROM AT_Tickets T INNER JOIN AT_Users U ON T.ticket_assign_to_id = U.id 
                WHERE 
                T.ticket_assign_to_id IS NOT NULL 
                AND (
                    T.ticket_status = 0 
                    OR T.ticket_status = 2
                ) 
                AND T.ticket_is_delete = 0 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                AND T.ticket_org_id = '"""+str(org_id)+"""'
                GROUP BY U.display_name
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_assign_to__display_name'])
            values.append(ticket['tcount'])
        retValues = {'Assignee': labels, 'Count': values}

        return JsonResponse(retValues)


@csrf_exempt
def monthlyPerformance(request):
    org_id = request.user.user_org_id
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    user_id = request.user.id

    months = []
    months.append(currentMonth)

    years = []
    years.append(currentYear)

    if currentMonth-1 == 0:
        months.append(12)
        months.append(11)
        years.append(currentYear - 1)
        years.append(currentYear - 1)
    elif currentMonth-2 == 0:
        months.append(1)
        years.append(currentYear)
        months.append(12)
        years.append(currentYear - 1)
    else:
        months.append(currentMonth-1)
        months.append(currentMonth-2)
        years.append(currentYear)
        years.append(currentYear)

    month_names = []
    dates = []
    open_tickets = []
    close_tickets = []
    reopen_tickets = []
    
    # Get User Type
    user_type = userType(request) 
    for i in range(0,3):
        month_name = calendar.month_name[months[i]]
        month_names.append(month_name)
        date_range = calendar.monthrange(years[i],months[i])
        dates.append(str(years[i]) + "-" + str(months[i]) + "-" + str(1))
        dates.append(str(years[i]) + "-" + str(months[i]) + "-" + str(date_range[1]))
        start_date = str(years[i]) + "-" + str(months[i]) + "-" + str(1)
        end_date = str(years[i]) + "-" + str(months[i]) + "-" + str(date_range[1])
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                select
                (
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_created_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_open] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                ) as opened_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_closed_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_close] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0 
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""' 
                ) as closed_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_is_reopen_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                    AND [AT_Tickets].[ticket_is_reopen] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0 
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""' 
                ) as reopened_tickets
            """
        elif user_type == 'agent':
            SQL  = """
                select
                (
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_created_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_open] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""' 
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                ) as opened_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_closed_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_close] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                ) as closed_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_is_reopen_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                    AND [AT_Tickets].[ticket_is_reopen] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0 
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""' 
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                ) as reopened_tickets
            """
        elif user_type == 'manager':
            SQL  = """
                select
                (
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_created_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_open] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = [AT_Tickets].ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                ) as opened_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_closed_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_close] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = [AT_Tickets].ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                ) as closed_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_is_reopen_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                    AND [AT_Tickets].[ticket_is_reopen] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0 
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""' 
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = [AT_Tickets].ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                ) as reopened_tickets
            """
        elif user_type == 'enduser':
            SQL  = """
                select
                (
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_created_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_open] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = [AT_Tickets].ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        [AT_Tickets].ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_caller_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_next_action_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                ) as opened_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_closed_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""' 
                    AND [AT_Tickets].[ticket_is_close] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = [AT_Tickets].ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        [AT_Tickets].ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_caller_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_next_action_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                ) as closed_tickets
                ,(
                    SELECT count(*)
                    FROM [AT_Tickets] 
                    WHERE 
                    [AT_Tickets].[ticket_is_reopen_at] BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                    AND [AT_Tickets].[ticket_is_reopen] = 1 
                    AND [AT_Tickets].[ticket_is_delete] = 0
                    AND AT_Tickets.ticket_org_id = '"""+str(org_id)+"""'  
                    AND [AT_Tickets].account_id in (
                        select account_id
                        from AT_UserAccountRelation b
                        where b.user_id = '"""+str(user_id)+"""'
                    )
                    AND (
                        SELECT COUNT(*)
                        FROM AT_Users U
                        WHERE U.id = [AT_Tickets].ticket_created_by_id
                        AND U.user_type = 1 -- END USER
                    )>0
                    AND (
                        [AT_Tickets].ticket_assign_to_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_caller_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_next_action_id = '"""+str(user_id)+"""'
                        OR [AT_Tickets].ticket_created_by_id = '"""+str(user_id)+"""'
                    )
                ) as reopened_tickets
            """
            
        cursor = connection.cursor()
        cursor.execute(SQL)
        result = dictfetchall(cursor)
        opened_tickets = result[0]['opened_tickets']
        closed_tickets = result[0]['closed_tickets']
        reopened_tickets = result[0]['reopened_tickets']

        open_tickets.append(opened_tickets)
        close_tickets.append(closed_tickets)
        reopen_tickets.append(reopened_tickets)

    retValues = {'Months' : month_names, 'Years' : years, 'Opened' : open_tickets, 'Closed' : close_tickets, 'Reopened' : reopen_tickets}

    return JsonResponse(retValues)


@csrf_exempt
def openTicketsByNextAction(request):
    user_id = request.user.id
    org_id = request.user.user_org_id
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # tickets = Ticket.objects.filter(ticket_assign_to__isnull=False).filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_assign_to__first_name=fName,ticket_assign_to__last_name=lName).\
        #     annotate(tcount=Count('ticket_id'))
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.\
        #     filter(ticket_next_action__isnull=False).filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_next_action__display_name=user).filter(ticket_is_delete=0).filter(kwargs).\
        #     annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
            """
        elif user_type == 'agent':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
            """
        elif user_type == 'manager':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
            """
        elif user_type == 'enduser':
            SQL = """
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND U.display_name = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets by Next Action',
            'name': True
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_next_action__display_name').\
        #     filter(ticket_next_action__isnull=False).filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).\
        #     annotate(tcount=Count('ticket_id'))

        if user_type == 'superadmin':
            SQL  = """
                SELECT U.display_name as ticket_next_action__display_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount]
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                GROUP BY U.display_name
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            tickets = dictfetchall(cursor)
        elif user_type == 'agent':
            SQL  = """
                SELECT U.display_name as ticket_next_action__display_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount]
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_is_delete = 0 
                GROUP BY U.display_name
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT U.display_name as ticket_next_action__display_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount]
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL
                AND tic.ticket_org_id = '"""+str(org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND tic.ticket_is_delete = 0 
                GROUP BY U.display_name
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT U.display_name as ticket_next_action__display_name, 
                    COUNT_BIG(tic.ticket_id) AS [tcount]
                FROM AT_Tickets tic
                INNER JOIN AT_Users U ON tic.ticket_next_action_id = U.id 
                WHERE tic.ticket_next_action_id IS NOT NULL 
                AND tic.ticket_org_id = '"""+str(org_id)+"""'
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND U.user_type = 1 -- End User
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                GROUP BY U.display_name
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        
        # return HttpResponse(tickets)
        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_next_action__display_name'])
            values.append(ticket['tcount'])
        retValues = {'Next Action': labels, 'Count': values}

        return JsonResponse(retValues)

@csrf_exempt
def currentQtrPerformance(request):
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    user_id = request.user.id
    org_id = request.user.user_org_id
    months = []
    months.append(currentMonth)

    years = []
    years.append(currentYear)

    if currentMonth-1 == 0:
        months.append(12)
        months.append(11)
        years.append(currentYear - 1)
        years.append(currentYear - 1)
    elif currentMonth-2 == 0:
        months.append(1)
        years.append(currentYear)
        months.append(12)
        years.append(currentYear - 1)
    else:
        months.append(currentMonth-1)
        months.append(currentMonth-2)
        years.append(currentYear)
        years.append(currentYear)

    month_names = []
    dates = []
    open_tickets = []
    close_tickets = []
    reopen_tickets = []
    avgResolutions = []

    kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
    # Get User Type
    user_type = userType(request) 
    # return HttpResponse(user_type)
    for i in range(0,3):
        month_name = calendar.month_name[months[i]]
        month_names.append(month_name)
        date_range = calendar.monthrange(years[i],months[i])
        dates.append(str(years[i]) + "-" + str(months[i]) + "-" + str(1))
        dates.append(str(years[i]) + "-" + str(months[i]) + "-" + str(date_range[1]))
        start_date = str(years[i]) + "-" + str(months[i]) + "-" + str(1)
        end_date = str(years[i]) + "-" + str(months[i]) + "-" + str(date_range[1])
        
        if user_type == 'superadmin':
            # opened_tickets = Ticket.objects.filter(ticket_is_open=1,ticket_created_at__range=(start_date,end_date))\
            # .filter(ticket_is_delete=0).count()
            # open_tickets.append(opened_tickets)
            # closed_tickets = Ticket.objects.filter(ticket_is_close=1,ticket_closed_at__range=(start_date, end_date)) \
            #     .filter(ticket_is_delete=0).count()
            # closed_tickets1 = Ticket.objects.filter(ticket_is_close=1,ticket_closed_at__range=(start_date, end_date)) \
            #     .filter(ticket_is_delete=0)
            # if closed_tickets > 0:
            #     abc = 0
            #     for tick in closed_tickets1:
            #         delta = tick.ticket_closed_at - tick.ticket_created_at
            #         days, seconds = delta.days, delta.seconds
            #         hours = days * 24
            #         hours2 = delta.seconds // 3600
            #         minutes = int(delta.seconds % 3600 / 60)
            #         abc = abc + (hours+hours2)
            #     abc = int(abc/closed_tickets)
            #     min = int(minutes/closed_tickets)
            #     avgResolutions.append(str(abc)+':'+str(min))
            # else:
            #     avgResolutions.append('00:00')
            # close_tickets.append(closed_tickets)
            # reopened_tickets = Ticket.objects.filter(ticket_is_reopen=1, ticket_is_reopen_at__range=(start_date, end_date)) \
            #     .filter(ticket_is_delete=0).count()
            # reopen_tickets.append(reopened_tickets)
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_open = 1 
                AND T.ticket_is_delete = 0 
                AND T.ticket_org_id =  '"""+str(org_id)+"""'
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            result = dictfetchall(cursor)
            opened_tickets = result[0]['count']
            open_tickets.append(opened_tickets)

            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""' 
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets = dictfetchall(cursor)
            closed_tickets = closed_tickets[0]['count']
            close_tickets.append(closed_tickets)

            SQL  = """
                SELECT *
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets1 = dictfetchall(cursor)
            if closed_tickets > 0:
                abc = 0
                for tick in closed_tickets1:
                    delta = tick.ticket_closed_at - tick.ticket_created_at
                    days, seconds = delta.days, delta.seconds
                    hours = days * 24
                    hours2 = delta.seconds
                    minutes = int(delta.seconds % 3600 / 60)
                    abc = abc + (hours+hours2)
                abc = int(abc/closed_tickets)
                min = int(minutes/closed_tickets)
                avgResolutions.append(str(abc)+':'+str(min))
            else:
                avgResolutions.append('00:00')
            
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_reopen = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            reopened_tickets = dictfetchall(cursor)
            reopened_tickets = reopened_tickets[0]['count']
            reopen_tickets.append(reopened_tickets)
        elif user_type == 'agent':
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_open = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            result = dictfetchall(cursor)
            opened_tickets = result[0]['count']
            open_tickets.append(opened_tickets)

            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets = dictfetchall(cursor)
            closed_tickets = closed_tickets[0]['count']
            close_tickets.append(closed_tickets)

            SQL  = """
                SELECT *
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets1 = dictfetchall(cursor)
            if closed_tickets > 0:
                abc = 0
                for tick in closed_tickets1:
                    delta = tick.ticket_closed_at - tick.ticket_created_at
                    days, seconds = delta.days, delta.seconds
                    hours = days * 24
                    hours2 = delta.seconds
                    minutes = int(delta.seconds % 3600 / 60)
                    abc = abc + (hours+hours2)
                abc = int(abc/closed_tickets)
                min = int(minutes/closed_tickets)
                avgResolutions.append(str(abc)+':'+str(min))
            else:
                avgResolutions.append('00:00')
            
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_reopen = 1 
                AND T.ticket_is_delete = 0 
                AND T.ticket_org_id =  '"""+str(org_id)+"""' 
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            reopened_tickets = dictfetchall(cursor)
            reopened_tickets = reopened_tickets[0]['count']
            reopen_tickets.append(reopened_tickets)
        elif user_type == 'manager':
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_open = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            result = dictfetchall(cursor)
            opened_tickets = result[0]['count']
            open_tickets.append(opened_tickets)

            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets = dictfetchall(cursor)
            closed_tickets = closed_tickets[0]['count']
            close_tickets.append(closed_tickets)

            SQL  = """
                SELECT *
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets1 = dictfetchall(cursor)
            if closed_tickets > 0:
                abc = 0
                for tick in closed_tickets1:
                    delta = tick.ticket_closed_at - tick.ticket_created_at
                    days, seconds = delta.days, delta.seconds
                    hours = days * 24
                    hours2 = delta.seconds
                    minutes = int(delta.seconds % 3600 / 60)
                    abc = abc + (hours+hours2)
                abc = int(abc/closed_tickets)
                min = int(minutes/closed_tickets)
                avgResolutions.append(str(abc)+':'+str(min))
            else:
                avgResolutions.append('00:00')
            
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_reopen = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            reopened_tickets = dictfetchall(cursor)
            reopened_tickets = reopened_tickets[0]['count']
            reopen_tickets.append(reopened_tickets)
        elif user_type == 'enduser':
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_open = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            result = dictfetchall(cursor)
            opened_tickets = result[0]['count']
            open_tickets.append(opened_tickets)

            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets = dictfetchall(cursor)
            closed_tickets = closed_tickets[0]['count']
            close_tickets.append(closed_tickets)

            SQL  = """
                SELECT *
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_close = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            closed_tickets1 = dictfetchall(cursor)
            if closed_tickets > 0:
                abc = 0
                for tick in closed_tickets1:
                    delta = tick.ticket_closed_at - tick.ticket_created_at
                    days, seconds = delta.days, delta.seconds
                    hours = days * 24
                    hours2 = delta.seconds
                    minutes = int(delta.seconds % 3600 / 60)
                    abc = abc + (hours+hours2)
                abc = int(abc/closed_tickets)
                min = int(minutes/closed_tickets)
                avgResolutions.append(str(abc)+':'+str(min))
            else:
                avgResolutions.append('00:00')
            
            SQL  = """
                SELECT count(*) count 
                FROM AT_Tickets T
                WHERE 
                T.ticket_created_at BETWEEN '"""+str(start_date)+"""' AND '"""+str(end_date)+"""'  
                AND T.ticket_is_reopen = 1 
                AND T.ticket_is_delete = 0
                AND T.ticket_org_id =  '"""+str(org_id)+"""'  
                AND T.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                ) 
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = T.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND (
                    T.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR T.ticket_caller_id = '"""+str(user_id)+"""'
                    OR T.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR T.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """
            cursor = connection.cursor()
            cursor.execute(SQL)
            reopened_tickets = dictfetchall(cursor)
            reopened_tickets = reopened_tickets[0]['count']
            reopen_tickets.append(reopened_tickets)

    retValues = {'Months' : month_names, 'Years' : years, 'Opened' : open_tickets, 'Closed' : close_tickets, 'Reopened' : reopen_tickets, 'avgResolution' : avgResolutions}

    return JsonResponse(retValues)

def saveDashboardPanel(request):
    # return HttpResponse(request.POST)
    if request.method == 'POST':
        user = User.objects.get(id = request.user.id)
        left_options = request.POST.getlist('left-option-name[]')
        right_options = request.POST.getlist('right-option-name[]')
        left_loop_count = int(request.POST.get('left-loop-count'))
        right_loop_count = int(request.POST.get('right-loop-count'))
        if left_loop_count > 0 or right_loop_count > 0:
            DashboardSettings.objects.filter(d_user_id=request.user.id).delete()
        if left_loop_count > 0:
            left_expand = request.POST.getlist('left-expanded[]')
            left_data_display = request.POST.getlist('left_data_display_preference[]')
            # return HttpResponse(left_data_display)
            for i,j in zip(left_options,left_data_display):
                if i in left_expand:
                    panel_obj = PanelGraph.objects.filter(panelGraph_url=i).first()
                    if PanelGraph.objects.filter(panelGraph_url=i).exists():
                        panel_id = panel_obj.panelGraph_id
                        d = DashboardSettings(d_user_id=request.user.id,d_panel_id=panel_id,d_column_side=0,d_expanded=1,d_data_display=j)
                        d.save()
                else:
                    panel_obj = PanelGraph.objects.filter(panelGraph_url=i).first()
                    if PanelGraph.objects.filter(panelGraph_url=i).exists():
                        panel_id = panel_obj.panelGraph_id
                        d = DashboardSettings(d_user_id=request.user.id,d_panel_id=panel_id,d_column_side=0,d_expanded=0,d_data_display=j)
                        d.save()
        if right_loop_count > 0:
            right_expand = request.POST.getlist('right-expanded[]')
            right_data_display = request.POST.getlist('right_data_display_preference[]')
            for i,j in zip(right_options,right_data_display):
                if i in right_expand:
                    panel_obj = PanelGraph.objects.filter(panelGraph_url=i).first()
                    if PanelGraph.objects.filter(panelGraph_url=i).exists():
                        panel_id = panel_obj.panelGraph_id
                        d = DashboardSettings(d_user_id=request.user.id,d_panel_id=panel_id,d_column_side=1,d_expanded=1,d_data_display=j)
                        d.save()
                else:
                    panel_obj = PanelGraph.objects.filter(panelGraph_url=i).first()
                    if PanelGraph.objects.filter(panelGraph_url=i).exists():
                        panel_id = panel_obj.panelGraph_id
                        d = DashboardSettings(d_user_id=request.user.id,d_panel_id=panel_id,d_column_side=1,d_expanded=0,d_data_display=j)
                        d.save()
        if left_loop_count == 0 and right_loop_count == 0:
            messages.error(request, 'Please Add atleast one graph!')
            return redirect('dashboardSettings')
        messages.success(request, 'Request Succeed! Settings added.')
        return redirect('home')

@active_user_required
@login_required
def mySettings(request):
    load_sidebar = get_sidebar(request)
    user_check = MySettings.objects.filter(m_user_id=request.user.id).first()
    tz_names = pytz.common_timezones
    numeric_offset = [int(datetime.now(pytz_timezone(tz)).strftime('%z')) for tz in tz_names]
    zones = pd.Series(numeric_offset,index=tz_names).sort_values()
    timezones = zones.index.tolist()

    context = {
        'sidebar': load_sidebar,
        'timezones': timezones,
        'timezones': pytz.all_timezones,
        'user': user_check,
    }
    return render(request, 'itrak/DashboardSettings/my_settings.html', context)

def saveMySettings(request):
    org_id = request.user.user_org_id
    # user_id = request.user.id
    if request.method == 'POST':
        if 'default_home_page' in request.POST and request.POST['default_home_page']:
            default_home_page = request.POST.get('default_home_page')
        if 'ticket_screen' in request.POST and request.POST['ticket_screen']:
            ticket_screen = request.POST.get('ticket_screen')
        if 'redirect_to' in request.POST and request.POST['redirect_to']:
            redirect_to = request.POST.get('redirect_to')
        if 'dashboard_reload' in request.POST and request.POST['dashboard_reload']:
            dashboard_reload = request.POST.get('dashboard_reload')
        else:
            dashboard_reload = 0
        if 'show_reload' in request.POST:
            show_reload = 'True'
        else:
            show_reload = 'False'
        if 'phone' in request.POST and request.POST['phone'] & 'dial_code' in request.POST and request.POST['dial_code']:
            phone = request.POST.get('phone')
            dial_code = request.POST.get('dial_code')
            full_phone = dial_code+'-'+phone
        else:
            full_phone = None
        # if 'dial_code' in request.POST and request.POST['dial_code']:
        #     dial_code = request.POST.get('dial_code')
        #     dial_code = '+'+dial_code
        # else:
        #     dial_code = None
        if 'email' in request.POST and request.POST['email']:
            email = request.POST.get('email')
        else:
            email = None
        if 'sms_email' in request.POST and request.POST['sms_email']:
            sms_email = request.POST.get('sms_email')
        else:
            sms_email = None
        if 'address1' in request.POST and request.POST['address1']:
            address1 = request.POST.get('address1')
        else:
            address1 = None
        if 'address2' in request.POST and request.POST['address2']:
            address2 = request.POST.get('address2')
        else:
            address2 = None
        if 'city' in request.POST and request.POST['city']:
            city = request.POST.get('city')
        else:
            city = None
        if 'state' in request.POST and request.POST['state']:
            state = request.POST.get('state')
        else:
            state = None
        if 'zip' in request.POST and request.POST['zip']:
            zip = request.POST.get('zip')
        else:
            zip = None
        if 'country' in request.POST and request.POST['country']:
            country = request.POST.get('country')
        else:
            country = None
        user_check = MySettings.objects.filter(m_user_id=request.user.id).count()
        if user_check > 0:
            MySettings.objects.filter(m_user_id=request.user.id).update(m_time_zone=request.POST.get('time_zone'),m_default_page=default_home_page,m_ticket_screen=ticket_screen,m_redirect_to=redirect_to,m_dashboard_reload=dashboard_reload,m_show_reload=show_reload,m_phone=full_phone,m_email=email,m_mob_sms_email=sms_email,m_address1=address1,m_address2=address2,m_user_city=city,m_user_state=state,m_user_zip_code=zip,m_user_country=country,m_modified_at=timezone.now(),m_org_id=org_id)
        elif user_check == 0:
            m = MySettings(m_user_id=request.user.id,m_time_zone=request.POST.get('time_zone'),m_default_page=default_home_page,m_ticket_screen=ticket_screen,m_redirect_to=redirect_to,m_dashboard_reload=dashboard_reload,m_show_reload=show_reload,m_phone=dial_code+'-'+phone,m_email=email,m_mob_sms_email=sms_email,m_address1=address1,m_address2=address2,m_user_city=city,m_user_state=state,m_user_zip_code=zip,m_user_country=country,m_org_id=org_id)
            m.save()
        messages.success(request, 'Request Succeeded! Settings Updated.')
        return redirect('mySettings')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Settings cannot be updated.Please try again.')
        return redirect('mySettings')
@login_required
def changePassword(request):
    load_sidebar = get_sidebar(request)
    obj = User.objects.get(username=request.user.username)
    context = {
            'sidebar': load_sidebar,
            'user': obj,
    }
    return render(request, 'itrak/DashboardSettings/change_password.html', context)

def PasswordChange(request): 
    if request.method == 'POST':
        password = request.POST['old_password']
        # return HttpResponse(password)
        if request.user.check_password(password):
            obj = User.objects.get(pk=request.user.id)
            obj.set_password(request.POST.get('password1'))
            obj.save()
            messages.success(request, 'Password has been updated!')
            return redirect('changePassword')
        else:
            messages.error(request, 'Current Password is wrong! Password cannot be updated.Please try again.')
            return redirect('changePassword')


# Open tickets by clients
@csrf_exempt
def openTicketsByClients(request):
    user_id = request.user.id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_org_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_org__org_name=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN GlobalACCTS acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.client = '"""+str(user)+"""'
                AND tic.ticket_is_delete = 0
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
            """
        elif user_type == 'agent':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.client = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
            """
        elif user_type == 'manager':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.client = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
            """
        elif user_type == 'enduser':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.client = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
            """

        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Parent Accounts'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_org__org_name').filter(ticket_org_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT acct.client as ticket_acct__client, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.client
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT acct.client as ticket_acct__client, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_is_delete = 0
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""' 
                GROUP BY acct.client
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT acct.client as ticket_acct__client, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.client
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT acct.client as ticket_acct__client, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.client
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_acct__client'])
            values.append(ticket['tcount'])
        retValues = {'Clients': labels, 'Count': values}

        return JsonResponse(retValues)
# open tickets end

@csrf_exempt
def openTicketsByCountry(request):
    user_id = request.user.id
    # Get User Type
    user_type = userType(request) 
    if 'user' in request.POST and request.POST['user']:
        user = request.POST['user']
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.filter(ticket_org_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_org__org_name=user).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        if user_type == 'superadmin':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN GlobalACCTS acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.country = '"""+str(user)+"""'
                AND tic.ticket_is_delete = 0
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""' 
            """
        elif user_type == 'agent':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""' 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.country = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_is_delete = 0 
            """
        elif user_type == 'manager':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.country = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
            """
        elif user_type == 'enduser':
            SQL ="""
                SELECT tic.ticket_id
                    ,tic.ticket_status
                    ,tic.submitted_at
                    ,tic.ticket_modified_at
                    ,tic.subject
                    ,(
                        select pri.priority_name
                        from AT_Priority pri
                        where pri.priority_id = tic.priority_id
                    ) as priority
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_type_id
                    ) as ticket_type
                    ,(
                        select tt.ttype_name
                        from AT_TicketType tt
                        where tt.ttype_id = tic.ticket_subtype1_id
                    ) as ticket_subtype1
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_next_action_id
                    ) as ticket_next_action
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_assign_to_id
                    ) as ticket_assign_to
                    ,(
                        select au.display_name
                        from AT_Users au
                        where au.id = tic.ticket_caller_id
                    ) as ticket_caller
                    ,(
                        select sub_status_text
                        from AT_SubStatus ss
                        where ss.sub_status_id =  tic.ticket_sub_status_id
                    ) as ticket_sub_status
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND acct.country = '"""+str(user)+"""'
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0 
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
            """

        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)
        context = {
            'tickets': tickets,
            'title': 'Open Tickets By Country'
        }
        return render(request, 'itrak/DashboardSettings/get_record_ticket.html', context)
    else:
        # kwargs = Q(ticket_assign_to_id=user_id) | Q(ticket_caller_id=user_id) | Q(ticket_next_action_id=user_id) | Q(ticket_created_by_id=user_id)
        # tickets = Ticket.objects.values('ticket_org__org_name').filter(ticket_org_id__isnull=False).\
        #     filter(Q(ticket_status=0) | Q(ticket_status=2)).filter(ticket_is_delete=0).filter(kwargs).annotate(tcount=Count('ticket_id'))
        
        # return HttpResponse(user_type)
        if user_type == 'superadmin':
            SQL  = """
                SELECT acct.country as ticket_acct__country, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.country
            """
        elif user_type == 'agent':
            SQL  = """
                SELECT acct.country as ticket_acct__country, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.country
            """
        elif user_type == 'manager':
            SQL  = """
                SELECT acct.country as ticket_acct__country, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND tic.ticket_is_delete = 0 
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.country
            """
        elif user_type == 'enduser':
            SQL  = """
                SELECT acct.country as ticket_acct__country, 
                    COUNT_BIG(tic.ticket_id) AS [tcount] 
                FROM AT_Tickets tic
                INNER JOIN globalaccts acct ON tic.[account_id] = acct.id 
                WHERE tic.account_id IS NOT NULL 
                AND (
                    tic.ticket_status = 0 
                    OR tic.ticket_status = 2
                ) 
                AND tic.account_id in (
                    select account_id
                    from AT_UserAccountRelation b
                    where b.user_id = '"""+str(user_id)+"""'
                )
                AND (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = tic.ticket_created_by_id
                    AND U.user_type = 1 -- END USER
                )>0
                AND tic.ticket_is_delete = 0 
                AND (
                    tic.ticket_assign_to_id = '"""+str(user_id)+"""'
                    OR tic.ticket_caller_id = '"""+str(user_id)+"""'
                    OR tic.ticket_next_action_id = '"""+str(user_id)+"""'
                    OR tic.ticket_created_by_id = '"""+str(user_id)+"""'
                )
                AND tic.ticket_org_id =  '"""+str(request.user.user_org_id)+"""'
                GROUP BY acct.country
            """
        cursor = connection.cursor()
        cursor.execute(SQL)
        tickets = dictfetchall(cursor)

        labels = []
        values = []

        for ticket in tickets:
            labels.append(ticket['ticket_acct__country'])
            values.append(ticket['tcount'])
        retValues = {'Country': labels, 'Count': values}

        return JsonResponse(retValues)


def savePhoneNumber(request):
    if request.method == 'POST':
        user_id  = request.user.id
        print(user_id)
        phone_number = request.POST.get('phone')
        dial_code = request.POST.get('dialcode')
        phone = dial_code+  '-' +phone_number
        print(phone)
        # m = MySettings(m_user_id=request.user.id,m_phone=phone)
        # m.save()
        return HttpResponse()