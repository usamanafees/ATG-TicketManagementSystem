from django.shortcuts import render, redirect, get_object_or_404, render_to_response, reverse
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


# Client Add Request Start#

@active_user_required
def addClient(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    data = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
    context = {
        'sidebar': load_sidebar,
        'data': data
    }
    return render(request, 'itrak/Client/client_add.html', context)

# Client Add Request End#


# Client Save Request Start#

@active_user_required
def saveClient(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'client_cus_id' in request.POST and request.POST['client_cus_id']:
            client_cus_id = request.POST.get('client_cus_id')
        if 'client_name' in request.POST and request.POST['client_name']:
            client_name = request.POST.get('client_name')
        if 'contact_person' in request.POST:
            contact_person = request.POST.get('contact_person')
        if 'email' in request.POST:
            email = request.POST.get('email')
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
        if 'phone2' in request.POST:
            phone2 = request.POST.get('phone2')
        if 'fax' in request.POST:
            fax = request.POST.get('fax')
        if 'address1' in request.POST:
            address1 = request.POST.get('address1')
        if 'address2' in request.POST:
            address2 = request.POST.get('address2')
        if 'city' in request.POST:
            city = request.POST.get('city')
        if 'state' in request.POST:
            state = request.POST.get('state')
        if 'zip' in request.POST:
            zip = request.POST.get('zip')
        if 'org_id' in request.POST:
            org_id = request.POST.get('org_id')

        obj = Client(client_cus_id=client_cus_id, client_name=client_name, client_contact_person=contact_person, client_email=email, client_phone=phone, client_second_phone=phone2, client_fax=fax, client_address1=address1, client_address2=address2, client_city=city, client_state=state, client_zip_code=zip, client_org_id=org_id)
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Client added.')
        return redirect('addClient')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Client cannot be added.Please try again.')
        return redirect('addClient')
# Client Save Request Start#


# Organization List Request Start#

@active_user_required
def listClients(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Client/client_list.html', context)

# Organization List Request End#


# Organization Edit Request Start#

@active_user_required
def editClient(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('clientID')
    try:
        try:
            client_id = signing.loads(id,salt=settings.SALT_KEY)
        except signing.BadSignature:
            return render_to_response('itrak/page-404.html')
        data = Client.objects.get(pk=client_id)
        data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
    except Client.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listClient')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Client/client_edit.html', context)

# Organization Edit Request End#

#Organization Update Request Start
@active_user_required
def updateClient(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('client_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Client.objects.get(pk=id)
        except Client.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listClient')
        else:
            if 'client_cus_id' in request.POST and request.POST['client_cus_id']:
                obj.client_cus_id = request.POST.get('client_cus_id')
            if 'client_name' in request.POST and request.POST['client_name']:
                obj.client_name = request.POST.get('client_name')
            if 'contact_person' in request.POST:
                obj.client_contact_person = request.POST.get('contact_person')
            if 'email' in request.POST:
                obj.client_email = request.POST.get('email')
            if 'phone' in request.POST:
                obj.client_phone = request.POST.get('phone')
            if 'phone2' in request.POST:
                obj.client_second_phone = request.POST.get('phone2')
            if 'fax' in request.POST:
                obj.client_fax = request.POST.get('fax')
            if 'address1' in request.POST:
                obj.client_address1 = request.POST.get('address1')
            if 'address2' in request.POST:
                obj.client_address2 = request.POST.get('address2')
            if 'city' in request.POST:
                obj.client_city = request.POST.get('city')
            if 'state' in request.POST:
                obj.client_state = request.POST.get('state')
            if 'zip' in request.POST:
                obj.client_zip_code = request.POST.get('zip')
            if 'org_id' in request.POST:
                obj.client_org_id = request.POST.get('org_id')
            if 'country' in request.POST:
                obj.client_country = request.POST.get('country')
                

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Client updated.')
            return redirect('listClient')
    else:
        messages.error(request, 'Request Failed! Client cannot be updated.Please try again.')
        return redirect('listClient')

# Organization Update Request End#


# Organization Delete Request Start#

@active_user_required
def deleteClient(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    client_id = request.GET.get('clientID')
    try:
        id = signing.loads(client_id,salt=settings.SALT_KEY)
        obj = Client.objects.get(pk=id)
    except Client.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listClient')
    else:
        obj.cl_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Client deleted.')
        return redirect('listClient')

# Organization Delete Request End#


# Organization Add Request Start#

@active_user_required
def exportOrganization(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    return render(request, 'Organization/org_add.html')

# Organization Add Request End#


#Datatable Code Start Here#
class ClientListJson(BaseDatatableView):
    # The model we're going to show
    model = Client

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
        if self.request.user.admin != 1:
            return render(request, 'itrak\page-404.html')
        return Client.objects.filter(cl_is_active=1).filter(cl_is_delete=0)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.client_id,salt=settings.SALT_KEY)

        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_ClientEdit?clientID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_ClientDel?clientID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'display':
            return '<a href="#modalClientUsers" class="bg-info text-white" onclick="GetUsersListByClient(event,'+str(row.client_id)+');"> View Users </a>'
        elif column == 'client_cus_id': 
            return '<a href="Home_ViewClient?clientID=' + str(rid) + '">'+str(row.client_cus_id)+'</a>' 

        else:
            return super(ClientListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(client_cus_id__icontains=search) | Q(client_name__icontains=search) | Q(client_org__org_name__icontains=search) | Q(client_phone__icontains=search) | Q(client_fax__icontains=search) | Q(client_email__icontains=search) | Q(client_contact_person__icontains=search) | Q(client_address1__icontains=search))
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

#CLIENT USERS EXCEL EXPORT STARTS

@csrf_exempt
def export_client_users_xls(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
    client_queryset = User.objects.filter(user_client_id = client_id).filter(is_delete=0)
    getClientDataByClientID = Client.objects.get(pk=client_id)
    client_name = getClientDataByClientID.client_name
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-ClientUsersToExcel.xlsx'.format(
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
        ('Client', 7),
        ('User ID', 7),
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
        title='ClientUsersToExcel',
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
    for client in client_queryset:
        row_num += 1

        # Define data and formats for each cell in the row
        row = [
            (client_name, 'Normal'),
            (client.username, 'Normal'),
            (client.last_name+','+client.first_name, 'Normal'),
            (client.first_name, 'Normal'),
            (client.last_name, 'Normal'),
            (client.email, 'Normal'),
            (client.phone_no, 'Normal'),
            (client.address1, 'Normal'),
            (client.address2, 'Normal'),
            (client.user_city, 'Normal'),
            (client.user_state, 'Normal'),
            (client.user_zip_code, 'Normal'),
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

#CLIENT USERS EXCEL EXPORT ENDS

@active_user_required
def clientEmailNotification(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('clientID')
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    clientData = Client.objects.get(pk=id)
    clientActions = ClientAction.objects.all()
    SQL = '''
        SELECT 
            distinct UP.user_id
            ,1 as id
            ,UP.client_id
            ,(
                select U.display_name
                from AT_Users U
                where U.id = UP.user_id
            ) as display_name
            ,(
                select count(*)
                from AT_ClientEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.client_id = UP.client_id
                and a.action_id = 1
            ) as On_Submit
            ,(
                select count(*)
                from AT_ClientEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.client_id = UP.client_id
                and a.action_id = 2
            ) as On_Assign
            ,(
                select count(*)
                from AT_ClientEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.client_id = UP.client_id
                and a.action_id = 3
            ) as On_Next_Action
            ,(
                select count(*)
                from AT_ClientEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.client_id = UP.client_id
                and a.action_id = 4
            ) as On_Note
            ,(
                select count(*)
                from AT_ClientEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.client_id = UP.client_id
                and a.action_id = 5
            ) as On_Close
            ,(
                select count(*)
                from AT_ClientEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.client_id = UP.client_id
                and a.action_id = 6
            ) as On_Escalate
        from AT_ClientEmailNotificationUserPermissions UP
        where UP.client_id = %s
    '''
    clientUsers = ClientEmailNotificationUserPermission.objects.raw(SQL,[id])
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'clientActions': clientActions,
        'clientData': clientData,
        'clientUsers': clientUsers
    }
    return render(request, 'itrak/Client/client_Notification_permissions.html', context)

@csrf_exempt
def getModalClientEmailPermissionsByID(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        user_id = request.POST.get('user_id')
        client_actions = ClientAction.objects.all()
        client = Client.objects.get(pk=client_id)
        user = User.objects.get(pk = user_id)
        email_permit = ClientEmailNotificationUserPermission.objects.filter(client_id=client_id,user_id=user_id,email=1).values_list('action_id',flat=True)
        mobile_permit = ClientEmailNotificationUserPermission.objects.filter(client_id=client_id,user_id=user_id,mobile=1).values_list('action_id',flat=True)
        context = {
            'client': client,
            'email_permit': email_permit,
            'mobile_permit': mobile_permit,
            'client_actions': client_actions,
            'user': user
        }
        return render(request, 'itrak/Client/client_permission_modal.html', context)

def updateClientEmailMobileNotifications(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        user_id = request.POST.get('user_id')
        ClientEmailNotificationUserPermission.objects.filter(client_id=client_id,user_id=user_id).delete()
        for email in request.POST.getlist('email'):
                permit_obj = ClientEmailNotificationUserPermission(client_id=client_id,user_id=user_id, email=1, action_id=email)
                permit_obj.save()
        for mobile in request.POST.getlist('mobile'):
                permit_obj = ClientEmailNotificationUserPermission(client_id=client_id,user_id=user_id, mobile=1, action_id=mobile)
                permit_obj.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect(reverse('clientEmailNotification') + '?clientID='+str(client_id))

def deleteClientEmailMobilePermissions(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        user_id = request.POST.get('user_id')
        ClientEmailNotificationUserPermission.objects.filter(client_id=client_id,user_id=user_id).delete()        
        messages.success(request, 'Request Succeed! Record successfully deleted.')
        return redirect(reverse('clientEmailNotification') + '?clientID='+str(client_id))


#Export Client List Start#

@csrf_exempt
def export_users_by_client_xls(request):
    """
    Downloads all movies as Excel file with a worksheet for each movie category
    """

    result_data = getArrayOfallUsersByclient()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename= ClientUsersToExcel.xlsx'.format()
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
        ('Client Name', 15),
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
        title='ClientUsersToExcel',
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
    for client in result_data:
        row_num += 1
        # Define data and formats for each cell in the row
        row = [
            (client["Client Name"], 'Normal'),
            (client["User ID"], 'Normal'),
            (client["Display Name"], 'Normal'),
            (client["First Name"], 'Normal'),
            (client["Last Name"], 'Normal'),
            (client["Email"], 'Normal'),
            (client["Phone"], 'Normal'),
            (client["Address1"], 'Normal'),
            (client["Address2"], 'Normal'),
            (client["City"], 'Normal'),
            (client["State"], 'Normal'),
            (client["Zip"], 'Normal')
        ]

        if client["Client Name"] != "":
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

#Export Client List End Here#


@active_user_required
def clientUsers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/Client/client_users.html', context)

#GET ALL Clients DATA FOR EJ2 GRID
@csrf_exempt
def getAllClientsJson(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    allclients = Client.objects.raw('''
        select a.*
            ,(
                select ORG.org_name
                from AT_Organizations ORG WITH(NOLOCK)
                WHERE ORG.org_id = A.client_org_id
                AND ORG.org_is_active = 1
                AND ORG.org_is_delete = 0
            ) as org_name
        from AT_Clients a with(nolock)
        where a.cl_is_delete = 0
        and a.cl_is_active = 1
    ''')
    resultArray = []
    for client in allclients:
        resutlCurrentRecord = {}
        resutlCurrentRecord['client_id'] = client.client_id
        resutlCurrentRecord['client_cus_id'] = client.client_cus_id
        resutlCurrentRecord['client_name'] = client.client_name
        resutlCurrentRecord['org_name'] = client.org_name
        resutlCurrentRecord['client_phone'] = client.client_phone
        resutlCurrentRecord['client_fax'] = client.client_fax
        resutlCurrentRecord['client_email'] = client.client_email
        resutlCurrentRecord['client_contact_person'] = client.client_contact_person
        resutlCurrentRecord['client_address1'] = client.client_address1
        resultArray.append(resutlCurrentRecord)
    
    return HttpResponse(json.dumps(resultArray), content_type="application/json")

#GET client USERS EJ2 GRID JSON
@csrf_exempt
def getClientUsers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    clientString = request.GET.get('$filter')
    if " and " in clientString:
        searchedtext = clientString.split("',tolower(cast(username, 'Edm.String'))))",1)[0] 
        searchedtext = searchedtext.split("and (substringof('",1)[1] 
        client_id = clientString.split("client_id eq ",1)[1] 
        client_id = client_id.split(" and (s",1)[0] 
        clientUsers = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_client_id=int(client_id)).filter(Q(username__contains=searchedtext)|Q(first_name__contains=searchedtext)|Q(last_name__contains=searchedtext))
        clientUsersCount = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_client_id=int(client_id)).filter(Q(username__contains=searchedtext)|Q(first_name__contains=searchedtext)|Q(last_name__contains=searchedtext)).count()
    else: 
        client_id = clientString.split("eq ",1)[1] 
        client_id = client_id.strip()
        clientUsers = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_client_id=int(client_id)) 
        clientUsersCount = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_client_id=int(client_id)).count()
    
    resultArray = []
    for clientUser in clientUsers:
        resutlCurrentRecord = {}
        resutlCurrentRecord['username'] = clientUser.username
        resutlCurrentRecord['first_name'] = clientUser.first_name
        resutlCurrentRecord['last_name'] = clientUser.last_name
        resultArray.append(resutlCurrentRecord)
    mainArray = {}
    mainArray['results'] = resultArray
    mainArray['__count'] = clientUsersCount
    externalArray = {}
    externalArray['d'] = mainArray

    return HttpResponse(json.dumps(externalArray), content_type="application/json")

    

# Client View Start#
@active_user_required
def viewClient(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('clientID')
    try:
        try:
            client_id = signing.loads(id,salt=settings.SALT_KEY)
        except signing.BadSignature:
            return render_to_response('itrak/page-404.html')
        data = Client.objects.get(pk=client_id)
        data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
    except Client.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listClient')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Client/client_view.html', context)
# Client View End#    
    
#CLIENT ADD USER NOTIFICATION PERMISISON
@csrf_exempt
def getModalToAddUserPermissionsInClient(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        orgUsers = User.objects.filter(user_client_id = client_id, is_active = 1, is_delete = 0)
        bookedUsers = ClientEmailNotificationUserPermission.objects.filter(client_id = client_id).values_list('user_id',flat=True)
        context = {
            'orgUsers': orgUsers,
            'bookedUsers': bookedUsers,
            'client_id': client_id,
        }
        return render(request, 'itrak/Organization/client_user_permission_modal.html', context)

# Org User Save Request Start#
@active_user_required
def saveClientUserNotificationPermissions(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        user_id = request.POST.get('user_id')
        p = ClientEmailNotificationUserPermission(
            client_id=client_id,
            user_id=user_id,
        )
        p.save()
        messages.success(request, 'Request Succeed! User added.')
        return redirect(reverse('clientEmailNotification') + '?clientID='+str(client_id))
    else:
        messages.error(request, 'Request Failed! User cannot be added.Please try again.')
        return redirect(reverse('clientEmailNotification') + '?clientID='+str(client_id))
# Org User Save Request Start#

