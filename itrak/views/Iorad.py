from django.shortcuts import render, redirect, get_object_or_404, render_to_response, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Iorad
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from django.core import signing
from django.db import connection
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


# List Iorad Tutorials Request Start#

@active_user_required
def listIoradTutorials(request):
    load_sidebar = get_sidebar(request)
    user_type = userType(request)
    context = {
        'sidebar': load_sidebar,
        'user_type': user_type
    }
    return render(request, 'itrak/Iorad/iorad_list.html', context)

# List Iorad Tutorials Request End#

def getIoradTutorials(request):
    user_type = userType(request)
    result = Iorad.objects.filter(iorad_is_delete = 0)
    mainArray = []
    for row in result:
        innerArray = {}
        innerArray['iorad_id'] = row.iorad_id
        if user_type == 'superadmin':
            innerArray['action'] = "<a id='more' onclick='viewIorad("+str(row.iorad_id)+")'><i  class='fa fa-eye'></i></a> | <a id='more' onclick='editIorad("+str(row.iorad_id)+")'><i  class='fa fa-pencil'></i></a> | <a id='more' onclick='deleteIorad("+str(row.iorad_id)+")'><i  class='fa fa-trash'></i></a></a>"
        else:
            innerArray['action'] = "<a id='more' onclick='viewIorad("+str(row.iorad_id)+")'><i class='fa fa-eye'></i></a>"
        innerArray['iorad_title'] = row.iorad_title
        innerArray['iorad_link'] = row.iorad_link
        mainArray.append(innerArray)
    return HttpResponse(json.dumps(mainArray), content_type="application/json")

def openAddIoradModal(request):
    context = {}
    if request.method == 'POST' and request.is_ajax():
        return render(request,'itrak/Iorad/add_iorad.html',context)


@active_user_required
def saveIorad(request):
    if request.method == 'POST':
        if 'iorad_title' in request.POST and request.POST['iorad_title']:
            iorad_title = request.POST.get('iorad_title')
        if 'iorad_link' in request.POST and request.POST['iorad_link']:
            iorad_link = request.POST.get('iorad_link')

        obj = Iorad(iorad_title=iorad_title, iorad_link=iorad_link)
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Iorad added.')
        return redirect('listIoradTutorials')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! iorad_link cannot be added.Please try again.')
        return redirect('listIoradTutorials')

def openEditIoradModal(request):
    context = {}
    if request.method == 'POST' and request.is_ajax():
        iorad_id = request.POST.get('iorad_id')
        try:
            data = Iorad.objects.get(pk =iorad_id)
        except Iorad.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not data:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listIoradTutorials')
        else:
            load_sidebar = get_sidebar(request)
            context = {
                'sidebar': load_sidebar,
                'data': data
            }
            return render(request, 'itrak/Iorad/edit_iorad.html', context)

def updateIorad(request):
    if request.method == 'POST':
        iorad_id = request.POST.get('iorad_id')
        try:
            obj = Iorad.objects.get(pk=iorad_id)
        except Iorad.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listIoradTutorials')
        else:
            if 'iorad_title' in request.POST and request.POST['iorad_title']:
                obj.iorad_title = request.POST.get('iorad_title')
            if 'iorad_link' in request.POST and request.POST['iorad_link']:
                obj.iorad_link = request.POST.get('iorad_link')

            obj.save()

            messages.success(request, 'Request Succeed! Iorad updated.')
            return redirect('listIoradTutorials')
    else:
        messages.error(request, 'Request Failed! Iorad cannot be updated.Please try again.')
        return redirect('listIoradTutorials')

def openDelIoradModal(request):
    context = {}
    if request.method == 'POST' and request.is_ajax():
        iorad_id = request.POST.get('iorad_id')
        try:
            data = Iorad.objects.get(pk =iorad_id)
        except Iorad.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not data:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listIoradTutorials')
        else:
            load_sidebar = get_sidebar(request)
            context = {
                'sidebar': load_sidebar,
                'data': data
            }
            return render(request, 'itrak/Iorad/delete_iorad.html', context)

@active_user_required
def deleteIorad(request):
    iorad_id = request.POST.get('iorad_id')
    try:
        obj = Iorad.objects.get(pk=iorad_id)
    except Iorad.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listIoradTutorials')
    else:
        obj.iorad_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Iorad deleted.')
        return redirect('listIoradTutorials')

def viewIorad(request):
    context = {}
    if request.method == 'POST' and request.is_ajax():
        iorad_id = request.POST.get('iorad_id')
        try:
            data = Iorad.objects.get(pk =iorad_id)
        except Iorad.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not data:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listIoradTutorials')
        else:
            load_sidebar = get_sidebar(request)
            context = {
                'sidebar': load_sidebar,
                'data': data
            }
            return render(request, 'itrak/Iorad/view_iorad.html', context)

def forwardIoradTutorial(request):
    if 'iorad_id' in request.POST and request.POST['iorad_id']:
        iorad_id = request.POST.get('iorad_id')
    else:
        iorad_id = 0

    SQL = """
        SELECT TOP 1 ior.iorad_id, ior.iorad_title, ior.iorad_link
        from AT_Iorad ior
        where ior.iorad_id > """+str(iorad_id)+"""
        and ior.iorad_is_delete = 0
        order by ior.iorad_id
    """
    cursor = connection.cursor()
    cursor.execute(SQL)
    result = cursor.fetchall()

    innerArray = {}
    if len(result) > 0:
        for index, tuple in enumerate(result):
            innerArray['iorad_id'] = tuple[0]
            innerArray['iorad_title'] = tuple[1]
            innerArray['iorad_link'] = tuple[2]
            innerArray['status'] = 1
    else:
        innerArray['status'] = 0
    return HttpResponse(json.dumps(innerArray), content_type="application/json")

def backwardIoradTutorial(request):
    if 'iorad_id' in request.POST and request.POST['iorad_id']:
        iorad_id = request.POST.get('iorad_id')
    else:
        iorad_id = 0

    SQL = """
        SELECT TOP 1 ior.iorad_id, ior.iorad_title, ior.iorad_link
        from AT_Iorad ior
        where ior.iorad_id < """+str(iorad_id)+"""
        and ior.iorad_is_delete = 0
        order by ior.iorad_id desc
    """
    cursor = connection.cursor()
    cursor.execute(SQL)
    result = cursor.fetchall()

    innerArray = {}
    if len(result) > 0:
        for index, tuple in enumerate(result):
            innerArray['iorad_id'] = tuple[0]
            innerArray['iorad_title'] = tuple[1]
            innerArray['iorad_link'] = tuple[2]
            innerArray['status'] = 1
    else:
        innerArray['status'] = 0
    return HttpResponse(json.dumps(innerArray), content_type="application/json")

def IoradTutorials(request):
    context = {}
    load_sidebar = get_sidebar(request)
    SQL = """
        SELECT TOP 1 ior.iorad_id, ior.iorad_title, ior.iorad_link
        from AT_Iorad ior
        where 1=1
        and ior.iorad_is_delete = 0
        order by ior.iorad_id
    """

    cursor = connection.cursor()
    cursor.execute(SQL)
    result = cursor.fetchall()
    innerArray = {}
    for index, tuple in enumerate(result):
        innerArray['iorad_id'] = tuple[0]
        innerArray['iorad_title'] = tuple[1]
        innerArray['iorad_link'] = tuple[2]

    context['result'] = innerArray
    context['sidebar'] = load_sidebar
    
    return render(request,'itrak/Iorad/iorad_tutorials.html',context)




