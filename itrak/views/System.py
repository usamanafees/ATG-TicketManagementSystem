from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Organization, Client
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from django.core import signing
from django.core import serializers
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.exceptions import PermissionDenied
from functools import wraps
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

@active_user_required
def addHoursOfOperation(request):
    if request.user.admin != 1:
        raise PermissionDenied("You are not allowed")
    user_id = request.user.id
    org_id = request.user.user_org_id
    try:
        data = HoursOfOperation.objects.filter(operation_user_id=user_id).filter(sys_is_delete=0).first()
        # if user_id != 3108:
        datesclosed = DatesClosed.objects.filter(date_user_id=user_id).filter(date_is_delete=0)
        # else:
        #     datesclosed = DatesClosed.objects.filter(date_is_delete=0)
    except HoursOfOperation.DoesNotExist:
        data = ''
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'datesclosed':datesclosed,
        'data': data,
    }
    return render(request, 'itrak/System/system_add_hours_of_operation.html', context)

@active_user_required
def saveHoursOfOperation(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    user_id = request.user.id
    org_id = request.user.user_org_id
    if request.method == 'POST':
        # If Object not Exists then save the Record
        if not HoursOfOperation.objects.filter(operation_user_id=user_id, operation_org_id=org_id).exists():
             # For Hours of Operation History Modal
            if 'inp_Recalculation' in request.POST:  
                recalculation = request.POST.get('inp_Recalculation')

            # For Work day
            if 'chkWorkday24' in request.POST and request.method == 'POST' and request.POST.get('chkWorkday24') != '':
                db_workday =  '' 
                chkWorkday24 = request.POST.get('chkWorkday24')
                if chkWorkday24 != db_workday: 
                    message = 'Workday24Hours'
                    save_history = CreateHistoryLog(db_workday,chkWorkday24,message,recalculation,user_id)
            else:    
                if 'time_begins' in request.POST and request.method == 'POST' and request.POST.get('time_begins') != '':
                    db_start_time = ''
                    time_begins = request.POST.get('time_begins')
                    if time_begins != db_start_time:
                        # return HttpResponse('WorkdayBegins')
                        message = 'WorkdayBegins'
                        save_history = CreateHistoryLog(db_start_time,time_begins,message,recalculation,user_id)
                        
                if 'time_ends' in request.POST and request.method == 'POST' and request.POST.get('time_ends') != '':
                    db_end_time = ''
                    time_ends = request.POST.get('time_ends')
                    if time_ends != db_end_time:
                        # return HttpResponse('WorkdayEnds')   
                        message = 'WorkdayEnds'
                        save_history = CreateHistoryLog(db_end_time,time_ends,message,recalculation,user_id) 
            # For Monday
            if  'inp_Monday' in request.POST and request.method == 'POST' and request.POST.get('inp_Monday') != '': 
                    old = ''
                    new = 'Monday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            #For Tuesday:
            if  'inp_Tuesday' in request.POST and request.method == 'POST' and request.POST.get('inp_Tuesday') != '':
                    old = ''
                    new = 'Tuesday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            #For Wednesday:
            if  'inp_Wednesday' in request.POST and request.method == 'POST' and request.POST.get('inp_Wednesday') != '':
                    old = ''
                    new = 'Wednesday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            #For Thursday:
            if  'inp_Thursday' in request.POST and request.method == 'POST' and request.POST.get('inp_Thursday') != '': 
                    old = ''
                    new = 'Thursday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            #For Friday:
            if  'inp_Friday' in request.POST and request.method == 'POST' and request.POST.get('inp_Friday') != '': 
                    old = ''
                    new = 'Friday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)
 
            #For Saturday:
            if  'inp_Saturday' in request.POST and request.method == 'POST' and request.POST.get('inp_Saturday') != '': 
                    old = ''
                    new = 'Saturday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            #For Sunday:
            if  'inp_Sunday' in request.POST and request.method == 'POST' and request.POST.get('inp_Sunday') != '':
                    old = ''
                    new = 'Sunday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)


            open_tickets_only = request.POST.get('inp_Recalculation') if 'inp_Recalculation' in request.POST else 'Open'          
            work_day = request.POST.get('chkWorkday24') if 'chkWorkday24' in request.POST else ''            
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
            HoursOfOperation.objects.create(
                open_tickets_only=open_tickets_only,
                work_day=work_day,
                start_hour=start_hour,
                start_minutes=start_minutes,
                start_AM_PM=start_AM_PM,
                end_hour=end_hour,
                end_minutes=end_minutes,
                end_AM_PM=end_AM_PM,
                monday=monday,
                tuesday=tuesday,
                wednesday=wednesday,
                thursday=thursday,
                friday=friday,
                saturday=saturday,
                sunday=sunday,
                operation_user_id = user_id,
                operation_org_id=org_id
            )
            messages.success(request, 'Request Succeed! Hours Of Operation added.')
            return HttpResponse('response')
        else:
            obj = HoursOfOperation.objects.filter(operation_user_id=user_id).first()
            # For Hours of Operation History Modal
            if 'inp_Recalculation' in request.POST:  
                recalculation = request.POST.get('inp_Recalculation')

            if  obj.work_day == 'ON' and 'chkWorkday24' not in request.POST:
                db_workday =  obj.work_day 
                chkWorkday24 = ''
                if chkWorkday24 != db_workday: 
                    message = 'Workday24Hours'
                    save_history = CreateHistoryLog(db_workday,chkWorkday24,message,recalculation,user_id)
            # For Work day
            if 'chkWorkday24' in request.POST and request.method == 'POST' and request.POST.get('chkWorkday24') != '':
                db_workday =  obj.work_day 
                chkWorkday24 = request.POST.get('chkWorkday24')
                if chkWorkday24 != db_workday: 
                    message = 'Workday24Hours'
                    save_history = CreateHistoryLog(db_workday,chkWorkday24,message,recalculation,user_id)
            else:    
                if 'time_begins' in request.POST and request.method == 'POST' and request.POST.get('time_begins') != '':
                    db_start_time = obj.start_hour +':'+ obj.start_minutes+' '+obj.start_AM_PM
                    time_begins = request.POST.get('time_begins')
                    if time_begins != db_start_time:
                        # return HttpResponse('WorkdayBegins')
                        message = 'WorkdayBegins'
                        save_history = CreateHistoryLog(db_start_time,time_begins,message,recalculatio,user_id)
                        
                if 'time_ends' in request.POST and request.method == 'POST' and request.POST.get('time_ends') != '':
                    db_end_time = obj.end_hour +':'+ obj.end_minutes+' '+obj.end_AM_PM
                    time_ends = request.POST.get('time_ends')
                    if time_ends != db_end_time:
                        # return HttpResponse('WorkdayEnds')   
                        message = 'WorkdayEnds'
                        save_history = CreateHistoryLog(db_end_time,time_ends,message,recalculation,user_id) 
            # For Monday
            if  'inp_Monday' in request.POST and request.method == 'POST' and request.POST.get('inp_Monday') != '':
                db_value =  obj.monday 
                day = request.POST.get('inp_Monday')
                if db_value != day: 
                    old = ''
                    new = 'Monday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.monday == 'on' and 'inp_Monday' not in request.POST:   
                db_value =  obj.monday 
                day = ''
                if db_value != day: 
                    old = 'Monday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)   

            #For Tuesday:
            if  'inp_Tuesday' in request.POST and request.method == 'POST' and request.POST.get('inp_Tuesday') != '':
                db_value =  obj.tuesday 
                day = request.POST.get('inp_Tuesday')
                if db_value != day: 
                    old = ''
                    new = 'Tuesday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.tuesday == 'on' and 'inp_Tuesday' not in request.POST:   
                db_value =  obj.tuesday 
                day = ''
                if db_value != day: 
                    old = 'Tuesday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id) 

            #For Wednesday:
            if  'inp_Wednesday' in request.POST and request.method == 'POST' and request.POST.get('inp_Wednesday') != '':
                db_value =  obj.wednesday 
                day = request.POST.get('inp_Wednesday')
                if db_value != day: 
                    old = ''
                    new = 'Wednesday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.wednesday == 'on' and 'inp_Wednesday' not in request.POST:   
                db_value =  obj.wednesday 
                day = ''
                if db_value != day: 
                    old = 'Wednesday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)  

            #For Thursday:
            if  'inp_Thursday' in request.POST and request.method == 'POST' and request.POST.get('inp_Thursday') != '':
                db_value =  obj.thursday 
                day = request.POST.get('inp_Thursday')
                if db_value != day: 
                    old = ''
                    new = 'Thursday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.thursday == 'on' and 'inp_Thursday' not in request.POST:   
                db_value =  obj.thursday 
                day = ''
                if db_value != day: 
                    old = 'Thursday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)   

            #For Friday:
            if  'inp_Friday' in request.POST and request.method == 'POST' and request.POST.get('inp_Friday') != '':
                db_value =  obj.friday 
                day = request.POST.get('inp_Friday')
                if db_value != day: 
                    old = ''
                    new = 'Friday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.friday == 'on' and 'inp_Friday' not in request.POST:   
                db_value =  obj.friday 
                day = ''
                if db_value != day: 
                    old = 'Friday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)  

            #For Saturday:
            if  'inp_Saturday' in request.POST and request.method == 'POST' and request.POST.get('inp_Saturday') != '':
                db_value =  obj.saturday 
                day = request.POST.get('inp_Saturday')
                if db_value != day: 
                    old = ''
                    new = 'Saturday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.saturday == 'on' and 'inp_Saturday' not in request.POST:   
                db_value =  obj.saturday 
                day = ''
                if db_value != day: 
                    old = 'Saturday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)   

            #For Sunday:
            if  'inp_Sunday' in request.POST and request.method == 'POST' and request.POST.get('inp_Sunday') != '':
                db_value =  obj.sunday 
                day = request.POST.get('inp_Sunday')
                if db_value != day: 
                    old = ''
                    new = 'Sunday'
                    message = '	NonWorkDay Added'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)

            elif obj.sunday == 'on' and 'inp_Sunday' not in request.POST:   
                db_value =  obj.sunday 
                day = ''
                if db_value != day: 
                    old = 'Sunday'
                    new = ''
                    message = 'NonWorkDay Removed'
                    save_history = CreateHistoryLog(old,new,message,recalculation,user_id)                                             

            obj.open_tickets_only = request.POST.get('inp_Recalculation') if 'inp_Recalculation' in request.POST else 'Open'     
            obj.work_day = request.POST.get('chkWorkday24') if 'chkWorkday24' in request.POST else ''            
            obj.start_hour = request.POST.get('inp_starthour') if 'inp_starthour' in request.POST else '12'            
            obj.start_minutes = request.POST.get('inp_startminutes') if 'inp_startminutes' in request.POST else '00'            
            obj.start_AM_PM = request.POST.get('inp_startAMPM') if 'inp_startAMPM' in request.POST else 'AM'            
            obj.end_hour = request.POST.get('inp_endhour') if 'inp_endhour' in request.POST else '11'            
            obj.end_minutes = request.POST.get('inp_endminutes') if 'inp_endminutes' in request.POST else '30'            
            obj.end_AM_PM = request.POST.get('inp_endAMPM') if 'inp_endAMPM' in request.POST else 'PM'            
            obj.monday = request.POST.get('inp_Monday') if 'inp_Monday' in request.POST else ''            
            obj.tuesday = request.POST.get('inp_Tuesday') if 'inp_Tuesday' in request.POST else ''            
            obj.wednesday = request.POST.get('inp_Wednesday') if 'inp_Wednesday' in request.POST else ''            
            obj.thursday = request.POST.get('inp_Thursday') if 'inp_Thursday' in request.POST else ''            
            obj.friday = request.POST.get('inp_Friday') if 'inp_Friday' in request.POST else ''            
            obj.saturday = request.POST.get('inp_Saturday') if 'inp_Saturday' in request.POST else ''
            obj.sunday = request.POST.get('inp_Sunday') if 'inp_Sunday' in request.POST else ''
            obj.save()
            # for HistoryHoursofOPeration table

            HistoryHoursOfOperation.objects.create(
            hhop_recalculation= request.POST.get('inp_Recalculation') if 'inp_Recalculation' in request.POST else '' ,
            hhop_previous_value=request.POST.get('time_begins') if 'time_begins' in request.POST else '',
            hhop_current_value=request.POST.get('time_ends') if 'time_ends' in request.POST else '',
            hhop_type = request.POST.get('inp_Recalculation') if 'inp_Recalculation' in request.POST else '' ,
            hhop_org_id = org_id,

            )

            messages.success(request, 'Request Succeed! Hours Of Operation updated.')
            return HttpResponse('response')
    else:
        messages.error(request, 'Request Failed! Hours Of Operation cannot be updated.Please try again.')
        return HttpResponse('error response')

@active_user_required
def saveDatesClosed(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
        # if 'comment' in request.POST and request.POST['comment'] == '':
        #     messages.error(request, 'Request Failed! Please enter comment.')
        #     return HttpResponse('error response')
    user_id = request.user.id
    org_id = request.user.user_org_id
    if request.method == 'POST':
        if 'date_closed' in request.POST and request.POST['date_closed'] != '':
            if DatesClosed.objects.filter(date_org_id=org_id,date_user_id=user_id).filter(date_closed=request.POST['date_closed']).filter(date_is_delete=0).exists():
                messages.error(request, 'Request Failed! Record already exist.')
                return HttpResponse('error response')
            else:
                date_closed = request.POST.get('date_closed')
                comment = request.POST.get('comment') if 'comment' in request.POST else ''      
                
                obj = DatesClosed(date_closed=date_closed, comment=comment,date_org_id=org_id,date_user_id=user_id)
                obj.save()
               
                # For History
                if 'inp_Recalculation' in request.POST and request.method == 'POST' and request.POST.get('inp_Recalculation') != '':  
                    recalculation = request.POST.get('inp_Recalculation')
                    data = HoursOfOperation.objects.filter(operation_org_id=org_id,operation_user_id=user_id).filter(sys_is_delete=0).first()
                    if data:
                        data.open_tickets_only = recalculation
                        data.save()
                else:
                    messages.error(request, 'Request Failed! Please Select Time Open Recalculation From Hours of Operation.')
                    return HttpResponse('error response')       

                latest_record = DatesClosed.objects.last()
                db_value =  latest_record.date_closed
                month=db_value.split('-')[0] 
                day=db_value.split('-')[1]  
                year=db_value.split('-')[2] 
                db_formated_value = month+'/'+day+'/'+year
                old = ''
                message = 'Holiday Added'
                save_history = CreateHistoryLog(old,db_formated_value,message,recalculation,user_id)
     
                messages.success(request, 'Request Succeed! Dates Closed added.')
                return HttpResponse('success response')
        else:
            messages.error(request, 'Request Failed! Please enter Date Closed.')
            return HttpResponse('error response')
    else:
        messages.error(request, 'Request Failed! Dates Closed cannot be added.Please try again.')
        return HttpResponse('error response')

#Delete Date Closed in Hours of Operation
@active_user_required 
def deleteDatesClosed(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET['date_id']
    try:
       obj  = DatesClosed.objects.get(pk=id)
    except DatesClosed.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return HttpResponse('error response')
    else:
        obj.date_is_delete = 1
        obj.save()

        # For History
        if 'inp_Recalculation' in request.POST and request.method == 'POST' and request.POST.get('inp_Recalculation') != '':  
            recalculation = request.POST.get('inp_Recalculation')
            data = HoursOfOperation.objects.filter(sys_is_delete=0).first()
            data.open_tickets_only = recalculation
            data.save()
        else:
            recalculation = ''  

        db_value = obj.date_closed
        month=db_value.split('-')[0] 
        day=db_value.split('-')[1]  
        year=db_value.split('-')[2] 
        db_formated_value = month+'/'+day+'/'+year
        new = ''
        message = 'Holiday Removed'
        save_history = CreateHistoryLog(db_formated_value,new,message,recalculation)

        messages.success(request, 'Request Success! Date Closed deleted.')
        return redirect('addHoursOfOperation') 


@active_user_required
def addSiteAppearance(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    try:
        data = SiteAppearance.objects.filter(site_org_id=org_id).filter(site_user_id=user_id).filter(site_is_delete=0).first()
    except SiteAppearance.DoesNotExist:
        data = ''
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'data': data,
    }
    return render(request, 'itrak/System/site_appearance.html', context)
    
@active_user_required
def saveSiteAppearance(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if 'site_title' in request.POST and request.POST['site_title'] == '':
        messages.error(request, 'Request Failed! Site Appearance cannot be added.Please try again.')
        return redirect('addSystemSettings')

    if request.method == 'POST':
        # If Object not Exists then save the Record
        org_id = request.user.user_org_id
        user_id = request.user.id
        if not SiteAppearance.objects.filter(site_org_id=org_id,site_user_id=user_id).exists():
            
            site_title = request.POST.get('site_title') if 'site_title' in request.POST else ''          
            home_screen = request.POST.get('home_screen') if 'home_screen' in request.POST else ''            
            home_agent = request.POST.get('home_agent') if 'home_agent' in request.POST else ''            
            login_screen = request.POST.get('login_screen') if 'login_screen' in request.POST else ''            
            # upload_favicon = request.FILES['upload_favicon'] if 'upload_favicon' in request.POST else ''            
            # upload_left_logo = request.FILES['upload_left_logo'] if 'upload_left_logo' in request.POST else ''            
            left_logo_url = request.POST.get('left_logo_url') if 'left_logo_url' in request.POST else ''            
            # upload_right_logo = request.FILES['upload_right_logo'] if 'upload_right_logo' in request.POST else ''            
            right_logo_url = request.POST.get('right_logo_url') if 'right_logo_url' in request.POST else ''            

            SiteAppearance.objects.create(
                site_title=site_title,
                home_screen=home_screen,
                home_agent=home_agent,
                login_screen=login_screen,
                # upload_favicon=upload_favicon,
                # upload_left_logo=upload_left_logo,
                left_logo_url=left_logo_url,
                # upload_right_logo=upload_right_logo,
                right_logo_url=right_logo_url,
                site_org_id = org_id,
                site_user_id = user_id,
            )
            messages.success(request, 'Request Succeed! Site Appearance added.')
            return redirect('addSystemSettings')
        else:
            obj = SiteAppearance.objects.filter(site_org_id=org_id,site_user_id = user_id).first()            
            obj.site_title = request.POST.get('site_title') if 'site_title' in request.POST else ''          
            obj.home_screen = request.POST.get('home_screen') if 'home_screen' in request.POST else ''            
            obj.home_agent = request.POST.get('home_agent') if 'home_agent' in request.POST else ''            
            obj.login_screen = request.POST.get('login_screen') if 'login_screen' in request.POST else ''            
            # obj.upload_favicon = request.FILES['fileup'] if 'fileup' in request.POST else ''            
            # obj.upload_left_logo = request.FILES['upload_left_logo'] if 'upload_left_logo' in request.POST else ''            
            obj.left_logo_url = request.POST.get('left_logo_url') if 'left_logo_url' in request.POST else ''            
            # obj.upload_right_logo = request.FILES['upload_right_logo'] if 'upload_right_logo' in request.POST else ''
            obj.right_logo_url = request.POST.get('right_logo_url') if 'right_logo_url' in request.POST else ''   
            obj.save()
            messages.success(request, 'Request Succeed! Site Appearance updated.')
            return redirect('addSystemSettings')
    else:
        messages.error(request, 'Request Failed! Site Appearance cannot be updated. Please try again.')
        return redirect('addSystemSettings')

@active_user_required
def saveSiteAppearanceFiles(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST' and len(request.FILES) != 0:
        org_id = request.user.user_org_id
        user_id = request.user.id
        if 'upload_favicon' in request.FILES:
            myfile = request.FILES['upload_favicon']
            obj = SiteAppearance.objects.filter(site_org_id=org_id).filter(site_user_id = user_id).first()
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            obj.upload_favicon = fs.url(filename)
            obj.save()
            messages.success(request, 'Request Succeed! file uploaded successfully.')
            return redirect('addSystemSettings')
        elif 'upload_left_logo' in request.FILES:
            myfile = request.FILES['upload_left_logo']
            obj = SiteAppearance.objects.filter(site_org_id=org_id).filter(site_user_id = user_id).first()
            print(obj)
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            obj.upload_left_logo = fs.url(filename)
            obj.save()
            messages.success(request, 'Request Succeed! file uploaded successfully.')
            return redirect('addSystemSettings')
        elif 'upload_right_logo' in request.FILES:
            myfile = request.FILES['upload_right_logo']
            obj = SiteAppearance.objects.filter(site_org_id=org_id).filter(site_user_id = user_id).first()
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            obj.upload_right_logo = fs.url(filename)
            obj.save()
            messages.success(request, 'Request Succeed! file uploaded successfully.')
            return redirect('addSystemSettings')
        else:
            messages.error(request, 'Request Failed! file is not uploaded. Please try again.')
            return redirect('addSystemSettings')
    else:
        messages.error(request, 'Request Failed! file is not uploaded. Please try again.')
        return redirect('addSystemSettings')

@active_user_required
def addEmailSettings(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    try:
        data = EmailSettings.objects.filter(email_org_id=org_id,email_user_id = user_id).filter(is_delete=0).first()
    except EmailSettings.DoesNotExist:
        data = ''
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'data': data,
    }
    return render(request, 'itrak/System/email_settings.html', context)

@active_user_required
def saveEmailSettings(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    errors_list = []
    if 'email_server' not in request.POST or request.POST['email_server'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Email Server.'))
    if 'user_name' not in request.POST or request.POST['user_name'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Server User Name.'))
    # if 'password' not in request.POST or request.POST['password'] == '':
    #     messages.error(request, 'Request Failed! Please Enter Server Password.')
    if 'email_sender_address' not in request.POST or request.POST['email_sender_address'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Email Sender Address.'))
    if 'email_sender_name' not in request.POST or request.POST['email_sender_name'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Email Sender Name.'))
    if errors_list:
        return redirect('addEmailSettings')

    if request.method == 'POST':
        if not EmailSettings.objects.filter(email_org_id=org_id,email_user_id = user_id).exists():            
            email_server = request.POST.get('email_server') if 'email_server' in request.POST else ''          
            tls_encription = request.POST.get('tls_encription') if 'tls_encription' in request.POST else ''            
            port = request.POST.get('port') if 'port' in request.POST else ''            
            user_auth = request.POST.get('user_auth') if 'user_auth' in request.POST else '' 
            user_name = request.POST.get('user_name') if 'user_name' in request.POST else ''            
            password = request.POST.get('password') if 'password' in request.POST else ''            
            email_sender_address = request.POST.get('email_sender_address') if 'email_sender_address' in request.POST else ''            
            email_sender_name = request.POST.get('email_sender_name') if 'email_sender_name' in request.POST else ''            
            outgoing_email = request.POST.get('outgoing_email') if 'outgoing_email' in request.POST else ''            
            return_email_address = request.POST.get('return_email_address') if 'return_email_address' in request.POST else ''            
            reply_separation_text = request.POST.get('reply_separation_text') if 'reply_separation_text' in request.POST else ''            
            use_html_format = request.POST.get('use_html_format') if 'use_html_format' in request.POST else ''           
            email_to_initiator = request.POST.get('email_to_initiator') if 'email_to_initiator' in request.POST else ''            
            email_on_substatus_change = request.POST.get('email_on_substatus_change') if 'email_on_substatus_change' in request.POST else ''            
            suppression_of_email_notifications = request.POST.get('suppression_of_email_notifications') if 'suppression_of_email_notifications' in request.POST else ''            
            allow_for_agents = request.POST.get('allow_for_agents') if 'allow_for_agents' in request.POST else ''            
            sorting_order = request.POST.get('sorting_order') if 'sorting_order' in request.POST else ''            

            EmailSettings.objects.create(
                email_server = email_server,
                tls_encription = tls_encription,
                port = port,
                user_auth = user_auth,
                user_name = user_name,
                password = password,
                email_sender_address = email_sender_address,
                email_sender_name = email_sender_name,
                outgoing_email = outgoing_email,
                return_email_address = return_email_address,
                reply_separation_text = reply_separation_text,
                use_html_format = use_html_format,
                email_to_initiator = email_to_initiator,
                email_on_substatus_change = email_on_substatus_change,
                suppression_of_email_notifications = suppression_of_email_notifications,
                allow_for_agents = allow_for_agents,
                sorting_order = sorting_order,
                email_org_id = org_id,
                email_user_id = user_id
            )
            messages.success(request, 'Request Succeed! Email Settings added.')
            return redirect('addEmailSettings')
        else:
            obj = EmailSettings.objects.filter(email_org_id=org_id,email_user_id = user_id).first()       
            obj.email_server = request.POST.get('email_server') if 'email_server' in request.POST else ''          
            obj.tls_encription = request.POST.get('tls_encription') if 'tls_encription' in request.POST else ''            
            obj.port = request.POST.get('port') if 'port' in request.POST else ''            
            obj.user_auth = request.POST.get('user_auth') if 'user_auth' in request.POST else '' 
            obj.user_name = request.POST.get('user_name') if 'user_name' in request.POST else ''            
            obj.password = request.POST.get('password') if 'password' in request.POST else ''            
            obj.email_sender_address = request.POST.get('email_sender_address') if 'email_sender_address' in request.POST else ''            
            obj.email_sender_name = request.POST.get('email_sender_name') if 'email_sender_name' in request.POST else ''            
            obj.outgoing_email = request.POST.get('outgoing_email') if 'outgoing_email' in request.POST else ''            
            obj.return_email_address = request.POST.get('return_email_address') if 'return_email_address' in request.POST else ''            
            obj.reply_separation_text = request.POST.get('reply_separation_text') if 'reply_separation_text' in request.POST else ''            
            obj.use_html_format = request.POST.get('use_html_format') if 'use_html_format' in request.POST else ''           
            obj.email_to_initiator = request.POST.get('email_to_initiator') if 'email_to_initiator' in request.POST else ''            
            obj.email_on_substatus_change = request.POST.get('email_on_substatus_change') if 'email_on_substatus_change' in request.POST else ''            
            obj.suppression_of_email_notifications = request.POST.get('suppression_of_email_notifications') if 'suppression_of_email_notifications' in request.POST else ''            
            obj.allow_for_agents = request.POST.get('allow_for_agents') if 'allow_for_agents' in request.POST else ''            
            obj.sorting_order = request.POST.get('sorting_order') if 'sorting_order' in request.POST else ''    
            obj.save()            

            messages.success(request, 'Request Succeed! Email Settings updated.')
            return redirect('addEmailSettings')
    else:
        messages.error(request, 'Request Failed! Email Settings cannot be updated. Please try again.')
        return redirect('addEmailSettings')

@active_user_required
def viewEmailLogs(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    try:
        if user_id != 3108:
            data = Emails.objects.filter(org_id=org_id)
        else:
            data = Emails.objects.all()
        print("data")
        print(data)
    except EmailSettings.DoesNotExist:
        data = ''
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'data': data,
    }
    return render(request, 'itrak/System/view_email_logs.html', context)
    # return HttpResponse("Hello Hi!")

class EmailsListJson(BaseDatatableView):
    # The model we're going to show
    model = EmailLog
    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        org_id = self.request.user.user_org_id
        user_id = self.request.user.id
        # global_user = isGlobalUser(self.request)
        # if self.request.user.user_type_slug != global_user:
        return EmailLog.objects.filter(log_org_id=org_id)
        # else:
        #     return EmailLog.objects.filter()
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        user_id = self.request.user.id  # Get user_id from request
        if column == 'body':
            rid = signing.dumps(row.email_id, salt=settings.SALT_KEY)
            return '<a href="javascript:void(0)" email_id='+ str(rid) + ' id="email_body" data-toggle="modal" data-target="#viewEmailBodyModal">View Body</a>'
        elif column == 'auto_date':
            uTimeZone = MySettings.objects.filter(m_user_id=user_id).first().m_time_zone 
            if uTimeZone is None or uTimeZone == 'NULL':
                uTimeZone = settings.TIME_ZONE
                # uTimeZone = datetime.now(timezone.utc)
            local_dt = row.auto_date.astimezone(pytz.timezone(uTimeZone))
            return datetime.strptime(str(local_dt), '%Y-%m-%d %H:%M:%S.%f%z').strftime('%m/%d/%Y %I:%M %p')   
        else:
            return super(EmailsListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # qs = qs.filter(Q(send_date__icontains=search) | Q(to_user_id__icontains=search) | Q(to_email__icontains=search) | Q(subject__icontains=search) | Q(body__icontains=search) | Q(mailed_date__icontains=search) | Q(rc__icontains=search) | Q(ticket__icontains=search))
            qs = qs.filter(Q(to__icontains=search) | Q(subject__icontains=search) | Q(body__icontains=search) | Q(event_name__icontains=search)| Q(action_item__icontains=search))
            # qs = qs.filter(name__istartswith=search)
        return qs


class HoursOfOperationListJson(BaseDatatableView):
     # The model we're going to show
    model = HoursOfOperation
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
        # if user_id != 3108:
        return HistoryHoursOfOperation.objects.filter(hhop_org_id=org_id).filter(hhop_is_active=1).filter(hhop_is_delete=0)
        # else:
            # return HistoryHoursOfOperation.objects.filter(hhop_is_active=1).filter(hhop_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column

        if column == 'hhop_modified_at':
            local_dt = row.hhop_modified_at
            # BusinessRules.objects.values_list('br_modified_at', flat=True).get(pk=rid)
            return datetime.strptime(str(local_dt), '%Y-%m-%d %H:%M:%S.%f%z').strftime('%m/%d/%Y %I:%M %p')

        elif column == 'hhop_recalculation':
            recalculation = HistoryHoursOfOperation.objects.values_list('hhop_recalculation', flat=True).get(pk=str(row.hhop_id))
            if recalculation == 'Open':
                return 'Open Tickets Only'
            elif recalculation == 'OpenClosed':
                return 'Open and Closed Tickets'

                
        else:
            return super(HoursOfOperationListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # qs = qs.filter(Q(send_date__icontains=search) | Q(to_user_id__icontains=search) | Q(to_email__icontains=search) | Q(subject__icontains=search) | Q(body__icontains=search) | Q(mailed_date__icontains=search) | Q(rc__icontains=search) | Q(ticket__icontains=search))
            qs = qs.filter(Q(hhop_type__icontains=search) | Q(hhop_current_value__icontains=search) | Q(hhop_previous_value__icontains=search) | Q(hhop_modified_by__icontains=search) | Q(hhop_recalculation__icontains=search) | Q(hhop_modified_by__icontains=search))
            # qs = qs.filter(name__istartswith=search)
        return qs
        
# View Email Body Request Start#

@csrf_exempt
def viewEmailBody(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.is_ajax():
        if request.method == 'POST':
            id=request.POST.get('email_id')
            email_id = signing.loads(id, salt=settings.SALT_KEY)
            print(email_id)
            to = EmailLog.objects.values_list('to', flat=True).filter(email_id=email_id).first()
            subject = EmailLog.objects.values_list('subject', flat=True).filter(email_id=email_id).first()
            body = EmailLog.objects.values_list('body', flat=True).filter(email_id=email_id).first()
            # print(data)
            return HttpResponse(json.dumps({'to':to, 'subject': subject, 'body' : body}), content_type="application/json")

# View Email Body Request End#

@active_user_required
def removeFaviconSiteAppearance(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    obj = SiteAppearance.objects.filter(site_org_id=org_id,site_user_id=user_id).first()
    obj.upload_favicon = ''
    obj.save()

    messages.success(request, 'Request Succeed! Favicon deleted.')
    return redirect('addSystemSettings')

@active_user_required
def removeLeftLogoSiteAppearance(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    obj = SiteAppearance.objects.filter(site_org_id=org_id,site_user_id=user_id).first()
    obj.upload_left_logo = ''
    obj.save()

    messages.success(request, 'Request Succeed! Left Logo deleted.')
    return redirect('addSystemSettings')

@active_user_required
def removeRightLogoSiteAppearance(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    obj = SiteAppearance.objects.filter(site_org_id=org_id,site_user_id=user_id).first()
    obj.upload_right_logo = ''
    obj.save()

    messages.success(request, 'Request Succeed! Right Logo deleted.')
    return redirect('addSystemSettings')

# check SMTP settings
@csrf_exempt
def smtpConnectionTest(request):
    if request.is_ajax() and request.method == 'POST':
        try:
            emailServer = request.POST.get('email_server')
            port = request.POST.get('port')
            userName = request.POST.get('user_name')
            password = request.POST.get('password')
            emailTo = request.POST.get('email_to')
            s = smtplib.SMTP(emailServer+': '+port)
            s.starttls()
            s.login(userName, password)
            s.sendmail(userName, emailTo, "Test Email by SMTP")
            s.quit()
            msg = 'Success! Email sent.'
        except:
            msg = 'Error! Wrong Mail Server Credentials.'
        return HttpResponse(json.dumps(msg), content_type="application/json")
    else:
        return HttpResponse(json.dumps("Not valid ajax call."), content_type="application/json")