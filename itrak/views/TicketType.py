from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from itrak.models import Organization, Client, Group, Department, User, UserManger, UserMenuPermissions, UserGroupMembership, ClientInformation, TicketType
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


# Ticket Type Add Request Start#

@active_user_required
def addTicketType(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/TicketType/tickettype_add.html', context)

# Ticket Type Save Request Start#

@active_user_required
def saveTicketType(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'ticket_type' in request.POST and request.POST['ticket_type']:
            ticket_type = request.POST.get('ticket_type')
        if 'display_order' in request.POST:
            display_order = request.POST.get('display_order')
        if 'display_agent_only' in request.POST:
            display_agent_only = 'True'
        else:
            display_agent_only = 'False'
        if 'parent_id' in request.POST and request.POST['parent_id']:
            parent_id = request.POST.get('parent_id')
        else:
            parent_id = 0
        org_id = request.user.user_org_id
        obj = TicketType(ttype_name=ticket_type, t_type_display_order=display_order, display_agent_only=display_agent_only, parent_id = parent_id, user_org_id=org_id)
        obj.save()

        messages.success(request, 'Request Succeed! Ticket Type added.')
        return redirect('addTicketType')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Ticket Type cannot be added.Please try again.')
        return redirect('addTicketType')
# Ticket Type Save Request Start#


# Ticket Type List Request Start#

@active_user_required
def listTicketTypes(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    parent_id = request.GET.get('parent_id')
    level = request.GET.get('level')
    load_sidebar = get_sidebar(request)

    context = {
        'parent_id': parent_id,
        'level': level,
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/TicketType/tickettype_list.html', context)

# Ticket Type List Request End#


# Ticket Type Edit Request Start#

@active_user_required
def editTicketType(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('ticketTypeID')
    
    try:
        ttype_id = signing.loads(id)
        data = TicketType.objects.get(pk=ttype_id)
    except TicketType.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listTicketType')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/TicketType/tickettype_edit.html', context)

# Ticket Type Edit Request End#


#Ticket Type Update Request Start
@active_user_required
def updateTicketType(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('ttype_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = TicketType.objects.get(pk=id)
        except TicketType.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect("/Admin_TicketTypeList?parent_id=0&level=0")
        else:
            if 'ticket_type' in request.POST:
                obj.ttype_name = request.POST.get('ticket_type')
            if 'display_order' in request.POST:
                obj.t_type_display_order = request.POST.get('display_order')
            if 'parent_id' in request.POST:
                obj.parent_id = request.POST.get('parent_id')
            else:
                obj.parent_id = 0

            if 'is_active' in request.POST:
                obj.ttype_is_active = 1
            else:
                obj.ttype_is_active = 0
            obj.save()

        # return HttpReshtponse('Success')
        messages.success(request, 'Request Succeed! Ticket Type updated.')
        return redirect('/portal/atg-extra/Admin_TicketTypeList?parent_id=0&level=0')
    else:
        messages.error(request, 'Request Failed! Ticket Type cannot be updated.Please try again.')
        return redirect('/portal/atg-extra/Admin_TicketTypeList?parent_id=0&level=0')

# Ticket Type Update Request End#


# Ticket Type Delete Request Start#

@active_user_required
def deleteTicketType(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('ticketTypeID')
    try:
        obj = TicketType.objects.get(pk=id)
    except TicketType.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('/portal/atg-extra/Admin_TicketTypeList?parent_id=0&level=0')
    else:
        obj.ttype_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Ticket Type deleted.')
        return redirect('/portal/atg-extra/Admin_TicketTypeList?parent_id=0&level=0')
# Ticket Type Delete Request End#


# Ajax Function to Get Parent ID Start#

@csrf_exempt
def getParentIDValue(request):
    if request.is_ajax() and request.method == 'POST':
        ttype_id = request.POST.get('type_id')
        data = TicketType.objects.get(pk=ttype_id)
        parentID = []
        parentID.append(str(data.parent_id))  
        return HttpResponse(json.dumps(parentID), content_type="application/json")
    else:
        return HttpResponse('fail')


# Ajax Function to Get Parent ID End#


# Ticket Type load Ajax Data Start#
@csrf_exempt
def TicketTypeJsonData(request):
    if request.is_ajax() and request.method == 'POST':
        global_user = isGlobalUser(request)
        if request.user.user_type_slug != global_user:
            org_id = request.user.user_org_id
            dataZeroLevel = TicketType.objects.filter(ttype_is_delete=0).filter(ttype_is_active=1).filter(user_org_id=org_id)
        else:
            dataZeroLevel = TicketType.objects.filter(ttype_is_delete=0).filter(ttype_is_active=1)
        mainArray = []
        for dataZeroLevel in dataZeroLevel:
        #
            levelZeroSubChildAssociative = {'id':dataZeroLevel.ttype_id , 'name': dataZeroLevel.ttype_name}
            if dataZeroLevel.parent_id == 0:
                levelOneSubChild = []
                dataFirstLevel = getTicketTypeRecordsByParentID(dataZeroLevel.ttype_id)
                if dataFirstLevel:
                    for dataFirstLevel in dataFirstLevel:
                    #
                        levelOneSubChildAssociative = {'id':dataFirstLevel.ttype_id , 'name': dataFirstLevel.ttype_name}
                        dataSecondLevel = getTicketTypeRecordsByParentID(dataFirstLevel.ttype_id)
                        if dataSecondLevel:
                            levelTwoSubChild = []
                            for dataSecondLevel in dataSecondLevel:
                            #
                                levelTwoSubChildAssociative = {'id':dataSecondLevel.ttype_id , 'name': dataSecondLevel.ttype_name}
                                dataThirdLevel = getTicketTypeRecordsByParentID(dataSecondLevel.ttype_id)
                                if dataThirdLevel:
                                    levelThreeSubChild = []
                                    for dataThirdLevel in dataThirdLevel:
                                    #
                                        levelThreeSubChildAssociative = {'id':dataThirdLevel.ttype_id , 'name': dataThirdLevel.ttype_name}
                                        dataFourthLevel = getTicketTypeRecordsByParentID(dataThirdLevel.ttype_id)
                                        if dataFourthLevel:
                                            levelFourSubChild = []
                                            for dataFourthLevel in dataFourthLevel:
                                            #
                                                levelFourSubChild.append({'id':dataFourthLevel.ttype_id , 'name': dataFourthLevel.ttype_name})
                                            #
                                            levelThreeSubChildAssociative['subChild'] = levelFourSubChild
                                            levelThreeSubChildAssociative['expanded'] = 'false'
                                        levelThreeSubChild.append(levelThreeSubChildAssociative)
                                    #
                                    levelTwoSubChildAssociative['subChild'] = levelThreeSubChild
                                    levelTwoSubChildAssociative['expanded'] = 'false'
                                levelTwoSubChild.append(levelTwoSubChildAssociative)
                            #
                            levelOneSubChildAssociative['subChild'] = levelTwoSubChild
                            levelOneSubChildAssociative['expanded'] = 'false'
                        levelOneSubChild.append(levelOneSubChildAssociative)
                    #
                levelZeroSubChildAssociative['subChild'] = levelOneSubChild
                levelZeroSubChildAssociative['expanded'] = 'false'
                mainArray.append(levelZeroSubChildAssociative)  
        #   
        return HttpResponse(json.dumps(mainArray), content_type="application/json")
    else:
        return HttpResponse('fail')
# Ticket Type load Ajax Data End#



#Datatable Code Start Here#
class TicketTypeListJson(BaseDatatableView):
    # The model we're going to show
    model = TicketType

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
    @csrf_exempt
    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        parent_id = self.request.GET.get('parent_id')
        org_id = self.request.user.user_org_id
        user_id = self.request.user.id
        global_user = isGlobalUser(self.request)
        # if self.request.user.user_type_slug != global_user:
        if parent_id == '0':
            return TicketType.objects.filter(ttype_is_delete = 0).filter(parent_id=0).filter(user_org_id=org_id)
        else:
            return TicketType.objects.filter(ttype_is_delete = 0, parent_id = parent_id).filter(user_org_id=org_id)
        # else:
        #     if parent_id == '0':
        #         return TicketType.objects.filter(ttype_is_delete = 0).filter(parent_id=0)
        #     else:
        #         return TicketType.objects.filter(ttype_is_delete = 0, parent_id = parent_id)
        
    @csrf_exempt
    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.ttype_id)
        level = self.request.GET.get('level')
        level = int(level) + 1
        noOfChilds = TicketType.objects.filter( parent_id= row.ttype_id).count()
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_TicketTypeEdit?ticketTypeID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_TicketTypeDel?ticketTypeID=' + str(row.ttype_id) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'isActive':
            if row.ttype_is_active == 1:
                return 'Active'
            else:
                return 'In Active'
        elif column == 'childlevel':
            if noOfChilds > 0:
                return '<a href="Admin_TicketTypeList?parent_id=' + str(row.ttype_id) + '&level='+str(level)+'">Level '+str(level)+'</a>'
            else:
                return ''
        else:
            return super(TicketTypeListJson, self).render_column(row, column)
    @csrf_exempt
    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = user_org.org_name
            qs = qs.filter(Q(ttype_name__icontains=search))
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
def validateUnique(request):
    if request.is_ajax() and request.method == 'POST':
        record_locator = request.POST.get('record_locator')
        # probably you want to add a regex check if the username value is valid here
        if record_locator:
            is_exist = ClientInformation.objects.filter(record_locator=record_locator).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')

#Validate Username for Uniqueness End#

@csrf_exempt
def export_tickettypes_xls(request):
    """
    Downloads all Ticket Type List as Excel file with a worksheet for each 
    """
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        xlsType = request.POST.get('xlsType')
    ticket_queryset = ticketTypeExportXLS()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-TicketTypesExport.xlsx'.format(
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
        ('TicketTypeID', 7),
        ('Ticket Type', 20),
        ('TicketSubtypeID', 10),
        ('TicketSubtype', 20),
        ('TicketSubtype2ID', 10),
        ('TicketSubtype2', 20),
        ('TicketSubtype3ID', 10),
        ('TicketSubtype3', 20),
        ('TicketSubtype4ID', 10),
        ('TicketSubtype4', 20),
        ('Active', 20),
    ]

    # Create a worksheet/tab with the title of the category
    worksheet = workbook.create_sheet(
        title='TicketTypesExport',
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
    for ticket in ticket_queryset:
        row_num += 1

        # Define data and formats for each cell in the row
        row = [
            (ticket["levelZeroIssueTypeID"], 'Normal'),
            (ticket["levelZeroIssueTypeName"], 'Normal'),
            (ticket["levelOneIssueTypeID"], 'Normal'),
            (ticket["levelOneIssueTypeName"], 'Normal'),
            (ticket["levelTwoIssueTypeID"], 'Normal'),
            (ticket["levelTwoIssueTypeName"], 'Normal'),
            (ticket["levelThreeIssueTypeID"], 'Normal'),
            (ticket["levelThreeIssueTypeName"], 'Normal'),
            (ticket["levelFourIssueTypeID"], 'Normal'),
            (ticket["levelFourIssueTypeName"], 'Normal'),
            (ticket["is_active"], 'Normal')
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

#unassignedTickets tickets to XLSX End#





