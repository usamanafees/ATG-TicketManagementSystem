from django.shortcuts import render, redirect, get_object_or_404, render_to_response, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import *
from django.contrib.sessions.models import Session
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from django.apps import apps
from itrak.views.encryption_util import *
from django.core.signing import Signer
import base64
from urllib.parse import urlencode
from django.core import signing
from datetime import date as dtDate
from dateutil.relativedelta import relativedelta
from django.utils.crypto import get_random_string
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


# Organization Add Request Start#

@active_user_required
def addOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'timezones': pytz.common_timezones,
    }
    return render(request, 'itrak/Organization/org_add.html', context)

# Organization Add Request End#


# Organization Save Request Start#

@active_user_required
def saveOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'orgname' in request.POST and request.POST['orgname']:
            orgname = request.POST.get('orgname')
        if 'is_internal' in request.POST and request.POST['is_internal']:
            is_internal = 'True'
        else:
            is_internal = 'False'
        if 'site_title' in request.POST:
            site_title = request.POST.get('site_title')
        if 'contact_person' in request.POST:
            contact_person= request.POST.get('contact_person')
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
        if 'email' in request.POST:
            email = request.POST.get('email')
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
        if 'www_address' in request.POST:
            www_address = request.POST.get('www_address')
        if 'from_reply_name' in request.POST:
            from_reply_name = request.POST.get('from_reply_name')
        if 'from_reply_email' in request.POST:
            from_reply_email = request.POST.get('from_reply_email')
        if 'note' in request.POST:
            note = request.POST.get('note')

        p = Organization(org_name=orgname, is_internal=is_internal, site_title=site_title, org_contact_person=contact_person, org_email=email, org_phone_no=phone, org_address1=address1, org_address2=address2, org_city=city, org_state=state, org_zip_code=zip, org_www_address=www_address, org_from_reply_email=from_reply_email, org_from_reply_address=from_reply_name, org_note=note)
        p.save()

        # organizational superadmin information
        if 'user_first_name' in request.POST and request.POST['user_first_name']:
            user_first_name = request.POST.get('user_first_name')
        if 'user_last_name' in request.POST and request.POST['user_last_name']:
            user_last_name = request.POST.get('user_last_name')
        if 'user_display_name' in request.POST:
            user_display_name = request.POST.get('user_display_name')
        if 'user_login_permit' in request.POST:
            user_login_permit = 'True'
        else:
            user_login_permit = 'False'
        if 'user_email' in request.POST:
            user_username = request.POST.get('user_email')
        if 'user_time_zone' in request.POST and request.POST['user_time_zone']:
            user_time_zone = request.POST.get('user_time_zone')
        else: 
            user_time_zone = 'NULL'
        obj = User(user_type='0', admin=True, is_active=True, username=user_username, first_name=user_first_name, last_name=user_last_name, display_name=user_display_name, login_permit=user_login_permit, phone_no='', email=user_username, mob_sms_email='', suppress_email=False, user_dep_id='', user_org_id=p.org_id, address1='', address2='', user_city='', user_state='', user_zip_code='', user_country='', user_time_zone=user_time_zone)
        obj.default_password = randomString = get_random_string(length=8)
        obj.set_password(randomString)
        obj.save()
        m = MySettings(m_user_id=obj.id, m_time_zone=user_time_zone, m_default_page='home', m_ticket_screen=0,m_redirect_to='home',
                       m_dashboard_reload=0, m_show_reload='False', m_phone=None, m_email=None,m_mob_sms_email=None, m_address1=None,
                       m_address2=None, m_user_city=None,m_user_state=None, m_user_zip_code=None, m_user_country=None, m_org_id=p.org_id)
        m.save()

        #EMAIL SENT on USER ADD Start#

        subject = 'Login Credentials'
        to = []
        to.append(obj.email)
        support_url = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/'
        obj1 = UserSentEmails(
                use_subject = subject,
                use_sent_to_id = obj.id,
                use_created_by_id = obj.id,
                use_org_id = p.org_id
            )
        obj1.save()
        insert_id = signing.dumps(UserSentEmails.objects.latest('pk').use_id, salt=settings.SALT_KEY)
        dynamic = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/resetPassword?userID=' + obj.username + '&password=' + randomString + '&msgID=' + str(insert_id) + ''

        params = {'company_name': 'ATG Extra', 'firstname': obj.first_name, 'lastname': obj.last_name,
                  'default_password': randomString, 'action_url': dynamic,
                  'support_url': support_url}  # Paramters for change in Template Context

        message = render_to_string('itrak/Email/Email-Template/signup_mail.html', params)

        send_email(to=to, subject=subject, message=message)
        # EMAIL SENT on USER ADD End#

        #Add User Menu Permision in DB Start#
        print(p.org_id)
        # menu_ids = request.POST.getlist('menus')
        # submenu_ids = request.POST.getlist('submenus')

        # for id in submenu_ids:
        #     permit_obj = UserMenuPermissions(user_id= obj.id, submenu_id = id)
        #     permit_obj.save()

        # for id in menu_ids:
        #     permit_obj = UserMenuPermissions(user_id= obj.id, menu_id = id)
        #     permit_obj.save()
        # #Add User Menu Permision in DB End#

        # #Adding Permission Actions to UserActionPermission table        
        # permission_actions = request.POST.getlist('permission_action')
        # permission_sub_actions = request.POST.getlist(' ')
        # user = User.objects.get(pk=obj.id)
       
        # for permission_action in permission_actions:
        #     # return HttpResponse(permission_action)
        #     permission_action_obj = PermissionAction.objects.get(perm_act_id=permission_action)
        #     user_act_obj = UserActionPermission(user_id=user.id, perm_act_id=permission_action_obj.perm_act_id, user_org_id=org_id)
        #     user_act_obj.save() 
        # for permission_sub_action in permission_sub_actions:
        #     per_sub_action_obj = PermissionSubAction.objects.get(sub_act_id=permission_sub_action)
        #     user_act_obj = UserSubActionPermission(user_id=user.id, sub_act_id=per_sub_action_obj.sub_act_id)
        #     user_act_obj.save()
        #END Adding Permission Actions to UserActionPermission table 
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Organization added.')
        return redirect('listOrg')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Organization cannot be added.Please try again.')
        return redirect('listOrg')
# Organization Save Request Start#


# Organization List Request Start#

@active_user_required
def listOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/Organization/org_list.html', context)

# Organization List Request End#


# Organization Edit Request Start#

@active_user_required
def editOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('orgID')
    try:
        org_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Organization.objects.get(pk=org_id)
    except Organization.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listOrg')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data
        }
        return render(request, 'itrak/Organization/org_edit.html', context)

# Organization Edit Request End#

#Organization Update Request Start
@active_user_required
def updateOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('org_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Organization.objects.get(pk=id)
        except Organization.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect("/Admin_OrganizationList")
        else:
            if 'orgname' in request.POST and request.POST['orgname']:
                obj.org_name = request.POST.get('orgname')
            if 'is_internal' in request.POST and request.POST['is_internal']:
                obj.is_internal = 'True'
            else:
                obj.is_internal = 'False'
            if 'site_title' in request.POST:
                obj.site_title = request.POST.get('site_title')
            if 'contact_person' in request.POST:
                obj.org_contact_person = request.POST.get('contact_person')
            if 'address1' in request.POST:
                obj.org_address1 = request.POST.get('address1')
            if 'address2' in request.POST:
                obj.org_address2 = request.POST.get('address2')
            if 'city' in request.POST:
                obj.org_city = request.POST.get('city')
            if 'state' in request.POST:
                obj.org_state = request.POST.get('state')
            if 'zip' in request.POST:
                obj.org_zip_code = request.POST.get('zip')
            if 'email' in request.POST:
                obj.org_email = request.POST.get('email')
            if 'phone' in request.POST:
                obj.org_phone_no = request.POST.get('phone')
            if 'www_address' in request.POST:
                obj.org_www_address = request.POST.get('www_address')
            if 'from_reply_name' in request.POST:
                obj.org_from_reply_address = request.POST.get('from_reply_name')
            if 'from_reply_email' in request.POST:
                obj.org_from_reply_email = request.POST.get('from_reply_email')
            if 'note' in request.POST:
                obj.org_note = request.POST.get('note')

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Organization updated.')
            return redirect('listOrg')
    else:
        messages.error(request, 'Request Failed! Organization cannot be updated.Please try again.')
        return redirect('listOrg')

# Organization Update Request End#


# Organization Delete Request Start#

@active_user_required
def deleteOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    org_id = request.GET.get('orgID')
    try:
        id = signing.loads(org_id,salt=settings.SALT_KEY)
        obj = Organization.objects.get(pk=id)
    except Organization.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listOrg')
    else:
        #Deleting Task Group Restrict To TaskGroupRestricts table            
        org = Organization.objects.get(pk=id)
        TaskGroupRestrict.objects.filter(tgr_org_id=org.org_id).delete()           
        #END Deleting Task Group Restrict To TaskGroupRestricts table 

        #Deleting Task Restrict To TaskGroupRestricts table            
        org = Organization.objects.get(pk=id)
        TaskRestrict.objects.filter(tr_org_id=org.org_id).delete()           
        #END Deleting Task  Restrict To TaskGroupRestricts table 
        # user_status = User.objects.filter(user_org_id=org)
        # print(user_status)
        # for status in user_status:
        #     print('in users')
        #     status.is_active = 0
        #     status.save()
        obj.org_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Organization deleted.')
        # return redirect("/Admin_OrganizationList")
        return redirect('listOrg')

# Organization Delete Request End#


# Organization Enable Request Start#

@active_user_required
def enableOrganization(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    org_id = request.GET.get('orgID')
    try:
        id = signing.loads(org_id,salt=settings.SALT_KEY)
        obj = Organization.objects.get(pk=id)
    except Organization.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listOrg')
    else:
        #Deleting Task Group Restrict To TaskGroupRestricts table            
        # org = Organization.objects.get(pk=id)
        # TaskGroupRestrict.objects.filter(tgr_org_id=org.org_id).delete()           
        # #END Deleting Task Group Restrict To TaskGroupRestricts table 

        # #Deleting Task Restrict To TaskGroupRestricts table            
        # org = Organization.objects.get(pk=id)
        # TaskRestrict.objects.filter(tr_org_id=org.org_id).delete()           
        #END Deleting Task  Restrict To TaskGroupRestricts table 
        # org = Organization.objects.get(pk=id)
        # user_status = User.objects.filter(user_org_id=org)
        # print(user_status)
        # for status in user_status:
        #     print('in users')
        #     status.is_active = 1
            # status.save()
        obj.org_is_delete = 0
        obj.save()
        messages.success(request, 'Request Success! Organization Enabled.')
        # return redirect("/Admin_OrganizationList")
        return redirect('listOrg')

# Organization Enable Request End#



#Datatable Code Start Here#
class OrgListJson(BaseDatatableView):
    # The model we're going to show
    model = Organization

    # define the columns that will be returned
    # columns = ['action', 'org_id', 'org_name', 'is_internal', 'display']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'org_id', 'org_name', 'is_internal']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        # rid = base64.urlsafe_b64encode(bytes(str(row.org_id), 'ascii'))
        # signer = Signer(salt='extra')
        # original = signer.sign(rid)
        # value = signer.unsign(original)
        # new = base64.b64decode(value).decode('ascii')
        # # return HttpResponse(original)
        # print(type(new))
        rid = signing.dumps(row.org_id,salt=settings.SALT_KEY)
        print(rid)
        id = signing.loads(rid,salt=settings.SALT_KEY)
        org_status = Organization.objects.filter(org_id=id).values_list('org_is_delete', flat=True)
        print(org_status)
        if column == 'action':
            # escape HTML for security reasons
            # return escape('{0}'.format(row.site_title))
            for org in org_status:
                if org == True:
                    print('True')
                    return '<a href="Admin_OrganizationEdit?orgID=' + str(rid) + '" title="Edit Organization"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_OrganizationEnable?orgID=' + str(rid) + '" data-toggle="modal" title="Enable Organization" data-target="#confirm-enable"><i class="fa fa-recycle" style="color:green"></i></a>'
                else:
                    return '<a href="Admin_OrganizationEdit?orgID=' + str(rid) + '" title="Edit Organization"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_OrganizationDel?orgID=' + str(rid) + '" data-toggle="modal" title="Delete Organization" data-target="#confirm-delete"><i class="fa fa-trash-o" style="color:red"></a>'
                    
                    print('False')
            # return '<a href="Admin_OrganizationEdit?orgID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_OrganizationDel?orgID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
            # return '<a href="{% url 'editOrganization' %}">Edit</a> | <a href="deleteOrg/' + str(row.org_id) + '">Delete</a>'
        elif column == 'org_id':
            # return '<a href="#modalOrgView" onclick="GetOrgView(event,' + str(row.org_id) + ');">'+str(row.org_id)
            return '<a href="Home_ViewOrganization?orgID=' + str(rid) + '">'+str(row.org_id)+'</a>' 
        elif column == 'display':
            return '<a href="#modalOrgUsers" class="bg-info text-white" onclick="GetUsersList(event,'+str(row.org_id)+');"> View Users </a> | <a href="#modalOrgTickets" class="bg-warning text-white" onclick="GetTicketsList(event,'+str(row.org_id)+');"> View Tickets </a>'
        elif column == 'is_internal':
            if row.is_internal == True:
                return escape('{0}'.format('Yes'))
            else:
                return escape('{0}'.format('No'))
        else:
            return super(OrgListJson, self).render_column(row, column)

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        if self.request.user.user_type_slug != isGlobalUser(self.request):
            return render(self.request, 'itrak\page-404.html')
        return Organization.objects.all().exclude(org_id=self.request.user.user_org_id)
        # return Organization.objects.filter(org_is_active=0, org_is_delete=1)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(org_id__icontains=search) | Q(org_name__icontains=search))
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


#Esxport Organization List Start#


def export_organizations_xls(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    """
    Downloads all movies as Excel file with a worksheet for each movie category
    """

    # category_queryset = Ticket.objects.all()
    organization_queryset = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-OrganizationList.xlsx'.format(
        date=datetime.now().strftime('%m-%d-%Y'),
    )
    workbook = Workbook()

    # Delete the default worksheet
    workbook.remove(workbook.active)

    # Define some styles and formatting that will be later used for cells
    header_font = Font(size=9, name='Segoe UI', bold=True, color='FFFFFF')
    centered_alignment = Alignment(horizontal='left')
    border_bottom = Border(
        bottom=Side(border_style='medium', color='21316f'),
    )
    wrapped_alignment = Alignment(
        vertical='top',
        wrap_text=True
    )
    columns = [
        ('ID', 15),
        ('Organization Name',17),
        ('Contact Person', 15),
        ('Email', 20),
        ('Phone', 15),
        ('Addr1', 23),
        ('Addr2', 20),
        ('City', 23),
        ('State', 30),
        ('Zip', 30),
        ('URL', 20),
        ('Internal Only', 20),
        ('Note', 15),
    ]
    # Create a worksheet/tab with the title of the category
    worksheet = workbook.create_sheet(
        title='OrganizationListEcxel',
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
    for organization in organization_queryset:
        row_num += 1
        # Define data and formats for each cell in the row
        row = [
            (organization.org_id, 'Normal'),
            (organization.org_name, 'Normal'),
            (organization.org_contact_person, 'Normal'),
            (organization.org_email, 'Normal'),
            (organization.org_phone_no, 'Normal'),
            (organization.org_address1, 'Normal'),
            (organization.org_address2, 'Normal'),
            (organization.org_city, 'Normal'),
            (organization.org_state, 'Normal'),
            (organization.org_zip_code, 'Normal'),
            (organization.org_www_address, 'Normal'),
            ('Yes' if organization.is_internal == 1 else 'No', 'Normal'),
            (organization.org_note, 'Normal'),
        ]

        row_fill = PatternFill(
            start_color='FFFFFF',
            end_color='FFFFFF',
            fill_type='solid',
        )

        cell_border = Border(
            bottom=Side(border_style='medium', color='21316f'),
            right=Side(border_style='medium', color='21316f'),
            left=Side(border_style='medium', color='21316f'),
            top=Side(border_style='medium', color='21316f'),
        )

        row_font = Font(size=8, name='Segoe UI', bold=False, color='000000')
        # Assign values, styles, and formatting for each cell in the row
        for col_num, (cell_value, cell_format) in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.style = cell_format
            # if cell_format == 'Currency':
            # cell.number_format = '#,##0.00 €'
            # if col_num == 8:
            # cell.number_format = '[h]:mm;@'
            cell.alignment = wrapped_alignment
            cell.fill = row_fill
            cell.font = row_font
            cell.border = cell_border

    # freeze the first row
    worksheet.freeze_panes = worksheet['A2']

    # set tab color
    worksheet.sheet_properties.tabColor = 'FFFFFF'

    workbook.save(response)

    return response

#Export Organization List End Here#

# Orginaztion Contract Save Start#
@active_user_required
def SaveOrgContract(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
            return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'org_id' in request.POST:
              org_id = request.POST.get('org_id')
        if 'contract_name' in request.POST:
              contract_name = request.POST.get('contract_name')
        if 'contract_begin_date' in request.POST:
              contract_begin_date = datetime.strptime(request.POST.get('contract_begin_date'), '%m-%d-%Y').strftime('%Y-%m-%d')
        if 'contract_end_date' in request.POST:
              contract_end_date = datetime.strptime(request.POST.get('contract_end_date'), '%m-%d-%Y').strftime('%Y-%m-%d')
        if 'contract_hours_purchased' in request.POST:
              contract_hours_purchased = request.POST.get('contract_hours_purchased')
        obj = OrginaztionContract(
                oc_org_id= org_id,
                org_contract_name=contract_name,
                org_contract_begin_date=contract_begin_date,
                org_contract_end_date=contract_end_date,
                org_contract_hours_purchased=contract_hours_purchased,
                org_contract_created_by_id=request.user.id
            )
        obj.save()

        response_data = [{'response' : 'success'}]
        return JsonResponse(response_data, safe=False)
# Orginaztion Contract Save End#
# Orginaztion Batch Contract Save Start#
@active_user_required
def SaveOrgBatchContract(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'org_id' in request.POST:
            org_id = request.POST.get('org_id')
        if 'batch_contract_name' in request.POST:
            batch_contract_name = request.POST.get('batch_contract_name')
        if 'bacth_genrate_number' in request.POST:
            bacth_genrate_number = request.POST.get('bacth_genrate_number')
        if 'batch_contract_no' in request.POST:
            batch_contract_no = request.POST.get('batch_contract_no') 
        if 'batch_dates_MY' in request.POST:
            batch_dates_MY = request.POST.get('batch_dates_MY')                    
        if 'batch_date_start' in request.POST:
            batch_date_start = (request.POST.get('batch_date_start'))
            start_date = batch_date_start.split('-')
            years = int(start_date[2])
            months = int(start_date[0])
            days = int(start_date[1])

        if 'batch_hours_purchased' in request.POST:
            batch_hours_purchased = request.POST.get('batch_hours_purchased')
        
                
        counter = 0
        batch_date_start = dtDate(years,months,days)
        if batch_dates_MY == '0':
            batch_end_date = batch_date_start + relativedelta(months=int(batch_contract_no))
        else:
            batch_end_date = batch_date_start + relativedelta(years=int(batch_contract_no))

        for genrate_number in range(0,int(bacth_genrate_number)):
            counter = counter+1
            obj = OrginaztionContract(
                oc_org_id= org_id,
                org_contract_name=batch_contract_name + str(counter) ,
                org_contract_begin_date=batch_date_start,
                org_contract_end_date=batch_end_date,
                org_contract_hours_purchased=batch_hours_purchased,
                org_contract_is_batch = 1,
                org_contract_created_by_id=request.user.id
            )
            obj.save()
            end_date = str(batch_end_date).split('-')
            years = int(end_date[0])
            months = int(end_date[1])
            days = int(end_date[2])+1
            batch_date_start = dtDate(years,months,days)
        if batch_dates_MY == '0':
            batch_end_date = batch_date_start + relativedelta(months=int(batch_contract_no))
        else:
            batch_end_date = batch_date_start + relativedelta(years=int(batch_contract_no))

        response_data = [{'response': 'success'}]
        
        return JsonResponse(response_data, safe=False)        
                
# Orginaztion Batch Contract Save End#

#Delete Service Contract By Organization id Start#
def deleteServiceContractByOrgId(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    response_data1 = {}
    if request.method == 'POST':
        org_contract_id =  request.POST.get('org_contract_id')
        org_id =  request.POST.get('org_id')
        if org_contract_id:
            serviceContact = OrginaztionContract.objects.get(org_contract_id=org_contract_id)
            serviceContact.org_contract_is_delete = 1
            serviceContact.save()
            response_data1['response'] = 'Success'
        else:
            response_data1['response'] = 'No Record Found'
        response_data = list(OrginaztionContract.objects.values().filter(oc_org_id=org_id).filter(org_contract_is_delete=0))
        return JsonResponse(response_data, safe=False)

#Update Service Contract By Org-Contract ID Start#
def UpdateerviceContractByOrgContractId(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    response_data1 = {}
    if request.method == 'POST':
        org_id =  request.POST.get('org_id')
        org_contract_id =  request.POST.get('org_contract_id')
        org_contract_name = request.POST.get('org_contract_name')
        org_contract_begin_date =datetime.strptime(request.POST.get('org_contract_begin_date'), '%m-%d-%Y').strftime('%Y-%m-%d')
        org_contract_end_date = datetime.strptime(request.POST.get('org_contract_end_date'), '%m-%d-%Y').strftime('%Y-%m-%d')
        org_contract_hour_purchased = request.POST.get('org_contract_hour_purchased')
        if org_contract_id:
            serviceContract = OrginaztionContract.objects.get(org_contract_id=org_contract_id)
            serviceContract.org_contract_name = org_contract_name
            serviceContract.org_contract_begin_date =org_contract_begin_date
            serviceContract.org_contract_end_date = org_contract_end_date
            serviceContract.org_contract_hours_purchased =org_contract_hour_purchased
            serviceContract.org_contract_modified_by_id = request.user.id
            serviceContract.save()
            response_data1['response'] = 'Success'
        else:
            response_data1['response'] = 'No Record Found'
        response_data = list(OrginaztionContract.objects.values().filter(oc_org_id=org_id).filter(org_contract_is_delete=0))
        return JsonResponse(response_data, safe=False)

#Update Service Contract By Org-Contract ID End#  

#ORGANIZATION USERS EXCEL EXPORT

@csrf_exempt
def export_organization_users_xls(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.POST.get('org_id')
    org_queryset = User.objects.filter(is_delete=0).filter(user_org_id=org_id)
    getOrgByOrgID = Organization.objects.get(pk=org_id)
    org_name = getOrgByOrgID.org_name
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-OrganizationUsersToExcel.xlsx'.format(
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
        ('Org ID #', 7),
        ('User ID ', 7),
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
        title='OrganizationUsersToExcel',
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
    for org in org_queryset:
        row_num += 1

        # Define data and formats for each cell in the row
        row = [
            (org_name, 'Normal'),
            (org.username, 'Normal'),
            (org.last_name+','+org.first_name, 'Normal'),
            (org.first_name, 'Normal'),
            (org.last_name, 'Normal'),
            (org.email, 'Normal'),
            (org.phone_no, 'Normal'),
            (org.address1, 'Normal'),
            (org.address2, 'Normal'),
            (org.user_city, 'Normal'),
            (org.user_state, 'Normal'),
            (org.user_zip_code, 'Normal'),
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
def orgEmailNotification(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('orgID')
    load_sidebar = get_sidebar(request)
    panel_types = getPanelsForDashboardSettings(request)
    organizationActions = OrganizationAction.objects.all()
    organizationData = Organization.objects.get(pk=id)
    SQL = '''
        SELECT 
            distinct UP.user_id
            ,1 as id
            ,UP.org_id
            ,(
                select U.display_name
                from AT_Users U
                where U.id = UP.user_id
            ) as display_name
            ,(
                select count(*)
                from AT_OrganizationEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.org_id = UP.org_id
                and a.action_id = 1
            ) as On_Submit
            ,(
                select count(*)
                from AT_OrganizationEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.org_id = UP.org_id
                and a.action_id = 2
            ) as On_Assign
            ,(
                select count(*)
                from AT_OrganizationEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.org_id = UP.org_id
                and a.action_id = 3
            ) as On_Next_Action
            ,(
                select count(*)
                from AT_OrganizationEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.org_id = UP.org_id
                and a.action_id = 4
            ) as On_Note
            ,(
                select count(*)
                from AT_OrganizationEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.org_id = UP.org_id
                and a.action_id = 5
            ) as On_Close
            ,(
                select count(*)
                from AT_OrganizationEmailNotificationUserPermissions a
                where a.user_id = UP.user_id
                and a.org_id = UP.org_id
                and a.action_id = 6
            ) as On_Escalate
        from AT_OrganizationEmailNotificationUserPermissions UP
        where UP.org_id = %s
    '''
    organizationUsers = OrganizationEmailNotificationUserPermission.objects.raw(SQL,[id])
    context = {
        'sidebar': load_sidebar,
        'panelTypes': panel_types,
        'organizationActions': organizationActions,
        'organizationData': organizationData,
        'organizationUsers': organizationUsers,
    }
    return render(request, 'itrak/Organization/org_email_Notification_permissions.html', context)

@csrf_exempt
def getModalOrgEmailPermissionsByID(request):
    if request.method == 'POST':
        organization_actions = OrganizationAction.objects.all()
        org_id = request.POST.get('org_id')
        user_id = request.POST.get('user_id')
        organization = Organization.objects.get(pk = org_id)
        user = User.objects.get(pk = user_id)
        email_permit = OrganizationEmailNotificationUserPermission.objects.filter(org_id = org_id, user_id = user_id, email=1).values_list('action_id',flat=True)
        mobile_permit = OrganizationEmailNotificationUserPermission.objects.filter(org_id = org_id, user_id = user_id, mobile=1).values_list('action_id',flat=True)
        # return HttpResponse(email_permit)
        context = {
            'organization': organization,
            'email_permit': email_permit,
            'mobile_permit': mobile_permit,
            'organization_actions': organization_actions,
            'user': user,
        }
        return render(request, 'itrak/Organization/org_permission_modal.html', context)

def updateOrgEmailMobileNotifications(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.POST.get('org_id')
        user_id = request.POST.get('user_id')
        # return HttpResponse(user_id)
        OrganizationEmailNotificationUserPermission.objects.filter(org_id=org_id, user_id=user_id).delete()
        
        for email in request.POST.getlist('email'):
                permit_obj = OrganizationEmailNotificationUserPermission(org_id=org_id, user_id=user_id, email=1, action_id=email)
                permit_obj.save()
        # for mobile in request.POST.getlist('mobile'):
        #         permit_obj = OrganizationEmailNotificationUserPermission(org_id=org_id, user_id=user_id, mobile=1, action_id=mobile)
        #         permit_obj.save()
        messages.success(request, 'Request Succeed! Record successfully updated.')
        return redirect(reverse('orgEmailNotification') + '?orgID='+str(org_id))

def deleteOrgEmailMobilePermissions(request):
    if request.method == 'POST':
        org_id = request.POST.get('org_id')
        user_id = request.POST.get('user_id')
        OrganizationEmailNotificationUserPermission.objects.filter(org_id = org_id, user_id = user_id).delete()        
        messages.success(request, 'Request Succeed! Record successfully deleted.')
        return redirect(reverse('orgEmailNotification') + '?orgID='+str(org_id))


#Esxport Organization List Start#

@csrf_exempt
def export_users_by_organization_xls(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    """
    Downloads all movies as Excel file with a worksheet for each movie category
    """

    result_data = getArrayOfallUsersByOrganization()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=OrganizationUsersToExcel.xlsx'.format()
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
        ('Organization Name', 15),
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
        title='OrganizationUsersToExcel',
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
    for organization in result_data:
        row_num += 1
        # Define data and formats for each cell in the row
        row = [
            (organization["Organization Name"], 'Normal'),
            (organization["User ID"], 'Normal'),
            (organization["Display Name"], 'Normal'),
            (organization["First Name"], 'Normal'),
            (organization["Last Name"], 'Normal'),
            (organization["Email"], 'Normal'),
            (organization["Phone"], 'Normal'),
            (organization["Address1"], 'Normal'),
            (organization["Address2"], 'Normal'),
            (organization["City"], 'Normal'),
            (organization["State"], 'Normal'),
            (organization["Zip"], 'Normal')
        ]

        if organization["Organization Name"] != "":
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

#Export Organization List End Here#

#GET ORGANIZATION USERS EJ2 GRID JSON
@csrf_exempt
def getOrgUsers(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    orgString = request.GET.get('$filter')
    if " and " in orgString:
        searchedtext = orgString.split("',tolower(cast(username, 'Edm.String'))))",1)[0] 
        searchedtext = searchedtext.split("and (substringof('",1)[1] 
        org_id = orgString.split("org_id eq ",1)[1] 
        org_id = org_id.split(" and (s",1)[0] 
        orgUsers = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_org_id=int(org_id)).filter(Q(username__contains=searchedtext)|Q(first_name__contains=searchedtext)|Q(last_name__contains=searchedtext))
        orgUsersCount = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_org_id=int(org_id)).filter(Q(username__contains=searchedtext)|Q(first_name__contains=searchedtext)|Q(last_name__contains=searchedtext)).count()
        # return HttpResponse(org_id)
    else: 
        getOrgID = orgString.split("eq ",1)[1] 
        spacesFreeOrgID = getOrgID.strip()
        orgUsers = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_org_id=int(spacesFreeOrgID)) 
        orgUsersCount = User.objects.filter(is_active=1).filter(is_delete=0).filter(user_org_id=int(spacesFreeOrgID)).count()
    
    resultArray = []
    for orgUser in orgUsers:
        rid = signing.dumps(orgUser.id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['username'] = '<a href="Home_ViewUser?UserID=' + str(rid) + '">'+str(orgUser.username)+'</a>'
        resutlCurrentRecord['first_name'] = orgUser.first_name
        resutlCurrentRecord['last_name'] = orgUser.last_name
        resultArray.append(resutlCurrentRecord)
    mainArray = {}
    mainArray['results'] = resultArray
    mainArray['__count'] = orgUsersCount
    externalArray = {}
    externalArray['d'] = mainArray

    return HttpResponse(json.dumps(externalArray), content_type="application/json")

#GET ALL ORGANIZATIONS DATA FOR EJ2 GRID
@csrf_exempt
def getAllOrgJson(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    allOrgs = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
    resultArray = []
    for allOrg in allOrgs:
        rid = signing.dumps(allOrg.org_id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['org_id'] = allOrg.org_id
        resutlCurrentRecord['org_link'] = '<a href="Home_ViewOrganization?orgID=' + str(rid) + '">'+str(allOrg.org_id)+'</a>'
        resutlCurrentRecord['org_name'] = allOrg.org_name
        if allOrg.is_internal == 1:
            resutlCurrentRecord['is_internal'] = "yes"
        else:
            resutlCurrentRecord['is_internal'] = "no"
        resutlCurrentRecord['phone_number'] = allOrg.org_phone_no
        resutlCurrentRecord['view_tickets'] = '<a href="#modalOrgTickets" onclick="GetTicketsList(event,'+str(allOrg.org_id)+');"> View Tickets </a>'
        resultArray.append(resutlCurrentRecord)
    
    return HttpResponse(json.dumps(resultArray), content_type="application/json")

@active_user_required
def organizatoinUsers(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/Organization/organization_users.html', context)

    
# Organization View Start#
@active_user_required
def viewOrg(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('orgID')
    try:
        org_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Organization.objects.get(pk=org_id)
        
    except Organization.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listUser')
    else:
        load_sidebar = get_sidebar(request)
        
        context = {
            'sidebar': load_sidebar,
            'data':data,      
        }
    return render(request, 'itrak/Organization/org_view.html', context)

# Organization View End#    

#ORGANIZATION ADD USER NOTIFICATION PERMISISON
@csrf_exempt
def getModalToAddUserPermissionsInOrg(request):
    if request.method == 'POST':
        org_id = request.POST.get('org_id')
        orgUsers = User.objects.filter(user_org_id = org_id, is_active = 1, is_delete = 0)
        bookedUsers = OrganizationEmailNotificationUserPermission.objects.filter(org_id = org_id).values_list('user_id',flat=True)
        context = {
            'orgUsers': orgUsers,
            'bookedUsers': bookedUsers,
            'org_id': org_id,
        }
        return render(request, 'itrak/Organization/org_user_permission_modal.html', context)

# Org User Save Request Start#
@active_user_required
def saveOrgUserNotificationPermissions(request):
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.POST.get('org_id')
        user_id = request.POST.get('user_id')
        p = OrganizationEmailNotificationUserPermission(
            org_id=org_id,
            user_id=user_id,
        )
        p.save()
        messages.success(request, 'Request Succeed! User added.')
        return redirect(reverse('orgEmailNotification') + '?orgID='+str(org_id))
    else:
        messages.error(request, 'Request Failed! User cannot be added.Please try again.')
        return redirect(reverse('orgEmailNotification') + '?orgID='+str(org_id))
# Org User Save Request Start#
