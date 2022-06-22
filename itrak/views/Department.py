from django.shortcuts import render, redirect, get_object_or_404, render_to_response, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Organization, Client, Department
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from django.core import signing
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


# Department Add Request Start#

@active_user_required
def addDepartment(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Department/dept_add.html', context)

# Department Add Request End#


# Department Save Request Start#

@active_user_required
def saveDepartment(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'dept_name' in request.POST and request.POST['dept_name']:
            dept_name = request.POST.get('dept_name')
        if 'is_internal' in request.POST and request.POST['is_internal']:
            is_internal = 'True'
        else:
            is_internal = 'False'
        org_id = request.user.user_org_id
        obj = Department(dep_name=dept_name, d_is_internal=is_internal, user_org_id=org_id)
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Department added.')
        return redirect('addDepartment')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Department cannot be added.Please try again.')
        return redirect('addDepartment')
# Department Save Request Start#


# Department List Request Start#

@active_user_required
def listDepartments(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Department/dept_list.html', context)

# Department List Request End#


# Department Edit Request Start#

@active_user_required
def editDepartment(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('DepID')
    try:
        dep_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Department.objects.get(pk=dep_id)
    except Department.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listDepartment')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Department/dept_edit.html', context)

# Department Edit Request End#

#Department Update Request Start
@active_user_required
def updateDepartment(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('dep_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Department.objects.get(pk=id)
        except Department.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listDepartment')
        else:
            if 'dep_name' in request.POST and request.POST['dep_name']:
                obj.dep_name = request.POST.get('dep_name')
            if 'is_internal' in request.POST and request.POST['is_internal']:
                obj.d_is_internal = 'True'
            else:
                obj.d_is_internal = 'False'
            if 'is_active' in request.POST and request.POST['is_active']:
                obj.d_is_active = 'True'
            else:
                obj.d_is_active = 'False'

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Department updated.')
            return redirect('listDepartment')
    else:
        messages.error(request, 'Request Failed! Department cannot be updated.Please try again.')
        return redirect('listDepartment')

# Department Update Request End#


# Department Delete Request Start#

@active_user_required
def deleteDepartment(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    dep_id = request.GET.get('DepID')
    try:
        id = signing.loads(dep_id,salt=settings.SALT_KEY)
        obj = Department.objects.get(pk=id)
    except Department.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listDepartment')
    else:
        obj.d_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Department deleted.')
        return redirect('listDepartment')

# Department Delete Request End#


# Department Add Request Start#

@active_user_required
def exportDepartment(request):
    return render(request, 'Organization/org_add.html')

# Department Add Request End#


#Datatable Code Start Here#
class DepartmentListJson(BaseDatatableView):
    # The model we're going to show
    model = Department

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
        return Department.objects.filter(d_is_delete=0).filter(user_org_id=org_id)
        # else:
        #     return Department.objects.filter(d_is_delete=0)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.dep_id,salt=settings.SALT_KEY)

        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_DeptEdit?DepID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_DeptDel?DepID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'dep_id':
            return '<a href="Home_ViewDepartment?DepID=' + str(rid) + '">'+str(row.dep_id)+'</a>' 
        elif column == 'd_is_active':
            if row.d_is_active == True:
                return escape('{0}'.format('Y'))
            else:
                return escape('{0}'.format('N'))
        elif column == 'd_is_internal':
            if row.d_is_internal == True:
                return escape('{0}'.format('Yes'))
            else:
                return escape('{0}'.format('No'))
        elif column == 'display':
            return '<a href="#modalDepUsers" class="bg-info text-white" onclick="GetUsersListByDep(event,'+str(row.dep_id)+');"> View Users </a>'
        else:
            return super(DepartmentListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(dep_id__icontains=search) | Q(dep_name__icontains=search))
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
    

#DEPARTMENT USERS EXCEL EXPORT STARTS

@csrf_exempt
def export_dep_users_xls(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id')
    dep_queryset = User.objects.filter(user_dep_id= dep_id).filter(is_delete=0)
    getDepartmentDataByDepID = Department.objects.get(pk=dep_id)
    dep_name = getDepartmentDataByDepID.dep_name
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-DepartmentUsersToExcel.xlsx'.format(
        date=datetime.now().strftime('%m-%d-%Y'),
    )
    workbook = Workbook()

    # Delete the default worksheet
    workbook.remove(workbook.active)

    # Define some styles and formatting that will be later used for cells
    header_font = Font(size=7, name='Segoe UI', bold=True, color='FFFFFF')
    centered_alignment = Alignment(horizontal='left')
    border_bottom = Border(
        bottom=Side(border_style='medium', color='21316f'),
    )
    wrapped_alignment = Alignment(
        vertical='top',
        wrap_text=True
    )
    
    columns = [
        ('Dep ', 7),
        ('User ID #', 7),
        ('Display Name', 20),
        ('First Name', 10),
        ('Last Name', 10),
        ('Email', 10),
        ('Phone', 10),
        ('Address1', 10),
        ('Address2', 10),
        ('City', 10),
        ('State', 10),
        ('Zip', 10),
    ]

    # Create a worksheet/tab with the title of the category
    worksheet = workbook.create_sheet(
        title='DepartmentUsersToExcel',
        index=0,
    )
    # Define the background color of the header cells
    fill = PatternFill(
        start_color='21316f',
        end_color='21316f',
        fill_type='solid',
    )
    row_num = 1

    # Assign values, styles, and formatting for each cell in the header
    for col_num, (column_title, column_width) in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        cell.border = border_bottom
        cell.alignment = centered_alignment
        cell.fill = fill
        # set column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = column_width
        
    # Iterate through all TicketTypes of a category
    for dep in dep_queryset:
        row_num += 1

        # Define data and formats for each cell in the row
        row = [
            (dep_name, 'Normal'),
            (dep.username, 'Normal'),
            (dep.last_name+','+dep.first_name, 'Normal'),
            (dep.first_name, 'Normal'),
            (dep.last_name, 'Normal'),
            (dep.email, 'Normal'),
            (dep.phone_no, 'Normal'),
            (dep.address1, 'Normal'),
            (dep.address2, 'Normal'),
            (dep.user_city, 'Normal'),
            (dep.user_state, 'Normal'),
            (dep.user_zip_code, 'Normal'),
        ]

        if int(row_num) % 2 == 0:
            row_fill = PatternFill(
                start_color='FFEFD5',
                end_color='FFEFD5',
                fill_type='solid',
            )
        else:
            row_fill = PatternFill(
                start_color='FFFFFF',
                end_color='FFFFFF',
                fill_type='solid',
            )
        print(row_num)

        row_font = Font(size=8, name='Segoe UI', bold=False, color='000000')
        # Assign values, styles, and formatting for each cell in the row
        for col_num, (cell_value, cell_format) in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.style = cell_format
            # if cell_format == 'Currency':
            #     cell.number_format = '#,##0.00 €'
            # if col_num == 8:
            #     cell.number_format = '[h]:mm;@'
            cell.alignment = wrapped_alignment
            cell.fill = row_fill
            cell.font = row_font

    # freeze the first row
    worksheet.freeze_panes = worksheet['A2']

    # set tab color
    worksheet.sheet_properties.tabColor = 'FFFFFF'

    workbook.save(response)

    return response

#ORGANIZATION USERS EXCEL EXPORT ENDS

@active_user_required
def depEmailNotification(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('DepID')
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    departmentActions = DepartmentAction.objects.all()
    departmentData = Department.objects.get(pk=id)
    SQL = '''
        SELECT 
            distinct UP.user_id
            ,1 as id
            ,UP.dep_id
            ,(
                select U.display_name
                from AT_Users U
                where U.id = UP.user_id
            ) as display_name
            ,(
                select count(*)
                from AT_DepartmentEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.dep_id = UP.dep_id
                and a.action_id = 1
            ) as On_Submit
            ,(
                select count(*)
                from AT_DepartmentEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.dep_id = UP.dep_id
                and a.action_id = 2
            ) as On_Assign
            ,(
                select count(*)
                from AT_DepartmentEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.dep_id = UP.dep_id
                and a.action_id = 3
            ) as On_Next_Action
            ,(
                select count(*)
                from AT_DepartmentEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.dep_id = UP.dep_id
                and a.action_id = 4
            ) as On_Note
            ,(
                select count(*)
                from AT_DepartmentEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.dep_id = UP.dep_id
                and a.action_id = 5
            ) as On_Close
            ,(
                select count(*)
                from AT_DepartmentEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.dep_id = UP.dep_id
                and a.action_id = 6
            ) as On_Escalate
        from AT_DepartmentEmailNotificationUserPermissions UP
        where UP.dep_id = %s
    '''
    departmentUsers = DepartmentEmailNotificationUserPermission.objects.raw(SQL,[id])
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'departmentActions': departmentActions,
        'departmentData': departmentData,
        'departmentUsers': departmentUsers
    }
    return render(request, 'itrak/Department/dep_Notification_permissions.html', context)

@csrf_exempt
def getModalDepEmailPermissionsByID(request):
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id')
        user_id = request.POST.get('user_id')
        departmentActions = DepartmentAction.objects.all()
        department = Department.objects.get(pk=dep_id)
        user = User.objects.get(pk=user_id)
        email_permit = DepartmentEmailNotificationUserPermission.objects.filter(dep_id=dep_id, user_id=user_id,email=1).values_list('action_id',flat=True)
        mobile_permit = DepartmentEmailNotificationUserPermission.objects.filter(dep_id=dep_id, user_id=user_id,mobile=1).values_list('action_id',flat=True)
        context = {
            'department': department,
            'email_permit': email_permit,
            'mobile_permit': mobile_permit,
            'departmentActions': departmentActions,
            'user': user
        }
        return render(request, 'itrak/Department/dep_permission_modal.html', context)

def updateDepEmailMobileNotifications(request):
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id')
        user_id = request.POST.get('user_id')
        DepartmentEmailNotificationUserPermission.objects.filter(dep_id=dep_id, user_id= user_id).delete()
        for email in request.POST.getlist('email'):
                permit_obj = DepartmentEmailNotificationUserPermission(dep_id=dep_id, user_id=user_id, email=1, action_id=email)
                permit_obj.save()
        for mobile in request.POST.getlist('mobile'):
                permit_obj = DepartmentEmailNotificationUserPermission(dep_id=dep_id, user_id=user_id, mobile=1, action_id=mobile)
                permit_obj.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect(reverse('depEmailNotification') + '?DepID='+str(dep_id))

def deleteDepEmailMobilePermissions(request):
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id')
        user_id = request.POST.get('user_id')
        DepartmentEmailNotificationUserPermission.objects.filter(dep_id=dep_id, user_id=user_id).delete()        
        messages.success(request, 'Request Succeed! Record successfully deleted.')
        return redirect(reverse('depEmailNotification') + '?DepID='+str(dep_id))

#Export Department List Start#

@csrf_exempt
def export_users_by_department_xls(request):
    """
    Downloads all movies as Excel file with a worksheet for each movie category
    """

    result_data = getArrayOfallUsersByDepartment()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename= DepartmentUsersToExcel.xlsx'.format()
    workbook = Workbook()

    # Delete the default worksheet
    workbook.remove(workbook.active)

    # Define some styles and formatting that will be later used for cells
    header_font = Font(size=7, name='Segoe UI', bold=True, color='FFFFFF')
    centered_alignment = Alignment(horizontal='left')
    border_bottom = Border(
        bottom=Side(border_style='medium', color='21316f'),
    )
    wrapped_alignment = Alignment(
        vertical='top',
        wrap_text=True
    )
    columns = [
        ('Department Name', 15),
        ('User ID',17),
        ('Display Name', 15),
        ('First Name', 20),
        ('Last Name', 15),
        ('Email', 23),
        ('Phone', 20),
        ('Address1', 23),
        ('Address2', 30),
        ('City', 30),
        ('State', 20),
        ('Zip', 20)
    ]
    # Create a worksheet/tab with the title of the category
    worksheet = workbook.create_sheet(
        title='DepartmentUsersToExcel',
        index=0,
    )
    # Define the background color of the header cells
    fill = PatternFill(
        start_color='21316f',
        end_color='21316f',
        fill_type='solid',
    )
    row_num = 1

    # Assign values, styles, and formatting for each cell in the header
    for col_num, (column_title, column_width) in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        cell.border = border_bottom
        cell.alignment = centered_alignment
        cell.fill = fill
        # set column width
        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = column_width
    
    # Iterate through all movies of a category
    for department in result_data:
        row_num += 1
        # Define data and formats for each cell in the row
        row = [
            (department["Department Name"], 'Normal'),
            (department["User ID"], 'Normal'),
            (department["Display Name"], 'Normal'),
            (department["First Name"], 'Normal'),
            (department["Last Name"], 'Normal'),
            (department["Email"], 'Normal'),
            (department["Phone"], 'Normal'),
            (department["Address1"], 'Normal'),
            (department["Address2"], 'Normal'),
            (department["City"], 'Normal'),
            (department["State"], 'Normal'),
            (department["Zip"], 'Normal')
        ]

        if department["Department Name"] != "":
            row_fill = PatternFill(
                start_color='FFEFD5',
                end_color='FFEFD5',
                fill_type='solid',
            )
        else:
            row_fill = PatternFill(
                start_color='FFFFFF',
                end_color='FFFFFF',
                fill_type='solid',
            )

        row_font = Font(size=8, name='Segoe UI', bold=False, color='000000')
        # Assign values, styles, and formatting for each cell in the row
        for col_num, (cell_value, cell_format) in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.style = cell_format
            # if cell_format == 'Currency':
            #     cell.number_format = '#,##0.00 €'
            # if col_num == 8:
            #     cell.number_format = '[h]:mm;@'
            cell.alignment = wrapped_alignment
            cell.fill = row_fill
            cell.font = row_font

    # freeze the first row
    worksheet.freeze_panes = worksheet['A2']

    # set tab color
    worksheet.sheet_properties.tabColor = 'FFFFFF'

    workbook.save(response)

    return response

#Export Department List End Here#

@active_user_required
def departmentUsers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/Department/department_users.html', context)

#GET ALL Department DATA FOR EJ2 GRID
@csrf_exempt
def getAllDepartmentsJson(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        allDepartments = Department.objects.filter(user_org_id=request.user.user_org_id).filter(d_is_delete=0,d_is_active=1)
    else:
        allDepartments = Department.objects.filter(d_is_delete=0,d_is_active=1)
    resultArray = []
    for department in allDepartments:
        rid = signing.dumps(department.dep_id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['dep_id'] =  department.dep_id
        resutlCurrentRecord['dep_name'] = department.dep_name
        if department.d_is_active == 1:
            resutlCurrentRecord['is_active'] = "Yes"
        else:
            resutlCurrentRecord['is_active'] = "No"

        if department.d_is_internal == 1:
            resutlCurrentRecord['is_internal'] = "Yes"
        else:
            resutlCurrentRecord['is_internal'] = "No"

        resutlCurrentRecord['dep_id_link'] = '<a href="Home_ViewDepartment?DepID=' + str(rid) + '">'+str(department.dep_id)+'</a>'
        resultArray.append(resutlCurrentRecord)
    
    return HttpResponse(json.dumps(resultArray), content_type="application/json")

#GET Department USERS EJ2 GRID JSON
@csrf_exempt
def getDepUsers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    departmentString = request.GET.get('$filter')
    if " and " in departmentString:
        searchedtext = departmentString.split("',tolower(cast(username, 'Edm.String'))))",1)[0] 
        searchedtext = searchedtext.split("and (substringof('",1)[1] 
        dep_id = departmentString.split("dep_id eq ",1)[1] 
        dep_id = dep_id.split(" and (s",1)[0] 
        depUsers = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_dep_id=int(dep_id)).filter(Q(username__contains=searchedtext)|Q(first_name__contains=searchedtext)|Q(last_name__contains=searchedtext))
        depUsersCount = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_dep_id=int(dep_id)).filter(Q(username__contains=searchedtext)|Q(first_name__contains=searchedtext)|Q(last_name__contains=searchedtext)).count()
        
    else: 
        dep_id = departmentString.split("eq ",1)[1] 
        dep_id = dep_id.strip()
        depUsers = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_dep_id=int(dep_id)) 
        depUsersCount = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_dep_id=int(dep_id)).count()
    
    resultArray = []
    for depUser in depUsers:
        rid = signing.dumps(depUser.id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['username'] = '<a href="Home_ViewUser?UserID=' + str(rid) + '">'+str(depUser.username)+'</a>'
        resutlCurrentRecord['first_name'] = depUser.first_name
        resutlCurrentRecord['last_name'] = depUser.last_name
        resultArray.append(resutlCurrentRecord)
    mainArray = {}
    mainArray['results'] = resultArray
    mainArray['__count'] = depUsersCount
    externalArray = {}
    externalArray['d'] = mainArray

    return HttpResponse(json.dumps(externalArray), content_type="application/json")

    # Department Edit Request Start#

@active_user_required
def viewDepartment(request):

    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('DepID')
    try:
        dep_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Department.objects.get(pk=dep_id)
    except Department.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listDepartment')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Department/dept_view.html', context)

# Department Edit Request End#

#Department ADD USER NOTIFICATION PERMISISON
@csrf_exempt
def getModalToAddUserPermissionsInDepartment(request):
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id')
        orgUsers = User.objects.filter(user_dep_id = dep_id, is_active = 1, is_delete = 0)
        bookedUsers = DepartmentEmailNotificationUserPermission.objects.filter(dep_id = dep_id).values_list('user_id',flat=True)
        context = {
            'orgUsers': orgUsers,
            'bookedUsers': bookedUsers,
            'dep_id': dep_id,
        }
        return render(request, 'itrak/Department/department_user_permission_modal.html', context)

# Org User Save Request Start#
@active_user_required
def saveDepartmentUserNotificationPermissions(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id')
        user_id = request.POST.get('user_id')
        p = DepartmentEmailNotificationUserPermission(
            dep_id = dep_id,
            user_id = user_id,
        )
        p.save()
        messages.success(request, 'Request Succeed! User added.')
        return redirect(reverse('depEmailNotification') + '?DepID='+str(dep_id))
    else:
        messages.error(request, 'Request Failed! User cannot be added.Please try again.')
        return redirect(reverse('depEmailNotification') + '?DepID='+str(dep_id))
# Org User Save Request Start#