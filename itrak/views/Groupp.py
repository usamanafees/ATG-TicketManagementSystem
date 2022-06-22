from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Organization, Client, Group, Department, GroupMenuPermissions
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from django.core import signing




# Create your views here.

#Custom Decorator Start#

user_login_required = user_passes_test(lambda user: user.is_active, login_url='/') #Here user_passes_test decorator designates the user is active.

def active_user_required(view_func):
    decorated_view_func = login_required(user_login_required(view_func))
    return decorated_view_func
from functools import wraps
# def active_user_required(view_func):
#     @wraps(view_func)
#     def wrapped(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('/')
#         else:
#             if request.user.user_org.org_is_delete==False:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return redirect('signout')
#     decorated_view_func = login_required(user_login_required(view_func))
#     return wraps(decorated_view_func)(wrapped)
#Custom Decorator End#saveGroup


# Client Add Request Start#

@active_user_required
def addGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    user_id = request.user.id
    org_id = request.user.user_org_id
    if user_id != 3108:
        organizations = org_id
        departments = Department.objects.filter(d_is_delete=0).filter(d_is_active=1).filter(user_org_id=org_id)
    else:
        organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
        departments = Department.objects.filter(d_is_delete=0)
    load_sidebar = get_sidebar(request)
    permissions = PermissionSection.objects.filter(is_active = 1).all() 
    disabled_actions=[1,2,3,4,5,6,7,11,40]
    disabled_sub_action=[1,2]
    context = {
        'sidebar': load_sidebar,
        'organizations': organizations,
        'departments': departments,
        'permissions': permissions,
        'disabled_actions': disabled_actions,
        'disabled_sub_action': disabled_sub_action,
        'user_id':user_id,
        'org_id':org_id

    }

    return render(request, 'itrak/Group/group_add.html', context)

# Client Add Request End#


# Group Save Request Start#

@active_user_required
def saveGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'membership_type' in request.POST and request.POST['membership_type']:
            membership_type = request.POST.get('membership_type')
        if 'group_cus_id' in request.POST:
            group_cus_id = request.POST.get('group_cus_id')
            
        if 'display_name' in request.POST and request.POST['display_name']:
            display_name = request.POST.get('display_name')
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
        if 'email' in request.POST:
            email = request.POST.get('email')
        if 'mob_sms_email' in request.POST:
            mob_sms_email = request.POST.get('mob_sms_email')
        if 'suppress_all_emails' in request.POST and request.POST['suppress_all_emails']:
            suppress_all_emails = 'True'
        else:
            suppress_all_emails = 'False'
        if 'org_id' in request.POST and request.POST['org_id']:
            org_id = request.POST.get('org_id')
        if 'dep_id' in request.POST:
            dep_id = request.POST.get('dep_id')

        obj = Group(membership_type=membership_type, group_cus_id=group_cus_id, group_display_name=display_name, group_phone=phone, group_email=email, group_mobile_sms_email=mob_sms_email, group_suppress_all_email=suppress_all_emails, group_dep_id=dep_id, group_org_id=org_id)
        obj.save()
        # return HttpResponse('Success')
        # Add Group Menu Permision in DB Start#

        menu_ids = request.POST.getlist('menus')
        submenu_ids = request.POST.getlist('submenus')

        for id in submenu_ids:
            permit_obj = GroupMenuPermissions(group_id=obj.group_id, submenu_id=id)
            permit_obj.save()

        for id in menu_ids:
            permit_obj = GroupMenuPermissions(group_id=obj.group_id, menu_id=id)
            permit_obj.save()
        
        #Adding Permission Actions to GroupActionPermission table        
        permission_actions = request.POST.getlist('permission_action')
        permission_sub_actions = request.POST.getlist('permission_sub_action')
        group = Group.objects.get(pk=obj.group_id)
        for permission_action in permission_actions:
            permission_action_obj = PermissionAction.objects.get(perm_act_id=permission_action)
            print(permission_action_obj)
            group_act_obj = GroupActionPermission(group_id=group.group_id, perm_act_id=permission_action_obj.perm_act_id)
            group_act_obj.save()

        for permission_sub_action in permission_sub_actions:
            per_sub_action_obj = PermissionSubAction.objects.get(sub_act_id=permission_sub_action)
            group_act_obj = GroupSubActionPermission(group_id=group.group_id, sub_act_id=per_sub_action_obj.sub_act_id)
            group_act_obj.save()
        #Adding Permission Actions to GroupActionPermission table   

        # Add Group Menu Permision in DB End#
        messages.success(request, 'Request Succeed! Group added.')
        return redirect('listGroup')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Group cannot be added.Please try again.')
        return redirect('listGroup')
# Group Save Request Start#


# Group List Request Start#

@active_user_required
def listGroups(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    obj = Group.objects.select_related('group_org')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/Group/group_list.html', context)

# Group List Request End#


# Group Edit Request Start#

@active_user_required
def editGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    id = request.GET.get('GrpID')
    try:
        group_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Group.objects.get(pk=group_id)
        data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
        data.departments = Department.objects.filter(d_is_delete=0)
        permissions = PermissionSection.objects.filter(is_active = 1).all()  
        any_users = User.objects.filter(is_delete=0).filter(is_active=1).filter(user_type__in = [1, 0]) 
        agents_users = User.objects.filter(is_delete=0).filter(is_active=1).filter(user_type=0)
        data.allowed_users = list(data.groupMembership.filter(is_delete=0).values_list('m_user_id', flat=True))
        print(permissions)
    except Group.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listGroup')
    else:
        load_sidebar = get_sidebar(request)
        menus_allowed = list(get_group_menus_permit(request, group_id))
        submenus_allowed = list(get_group_submenus_permit(request, group_id))
        actions_list = group_action_permissions(request, data)
        sub_actions_list = group_sub_action_permissions(request, data)
        disabled_actions= group_permissions_not_allowed(request)
        disabled_sub_action= group_sub_permissions_not_allowed(request)
        # print(disabled_actions)
        # print(disabled_sub_action)
        context = {
            'sidebar': load_sidebar,
            'menus_allowed': menus_allowed,
            'submenus_allowed': submenus_allowed,
            'data': data,
            'permissions': permissions,
            'actions_list': actions_list,
            'sub_actions_list': sub_actions_list,
            'disabled_actions': disabled_actions,
            'disabled_sub_action': disabled_sub_action,
            'any_users':any_users,
            'agents_users':agents_users,
        }
        return render(request, 'itrak/Group/group_edit.html', context)

# Group Edit Request End#

#Group Update Request Start
@active_user_required
def updateGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('group_id')
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = Group.objects.get(pk=id)
        except Group.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listGroup')
        else:
            if 'membership_type' in request.POST and request.POST['membership_type']:
                obj.membership_type = request.POST.get('membership_type')
            if 'display_name' in request.POST and request.POST['display_name']:
                obj.group_display_name = request.POST.get('display_name')
            if 'phone' in request.POST:
                obj.group_phone = request.POST.get('phone')
            if 'email' in request.POST:
                obj.group_email = request.POST.get('email')
            if 'mob_sms_email' in request.POST:
                obj.group_mob_sms_email = request.POST.get('mob_sms_email')
            if 'suppress_all_emails' in request.POST:
                obj.suppress_all_emails = 'True'
            else:
                obj.suppress_all_emails = 'False'
            if 'is_active' in request.POST:
                obj.gp_is_active = 'True'
            else:
                obj.gp_is_active = 'False'
            if 'org_id' in request.POST and request.POST['org_id']:
                obj.group_org_id = request.POST.get('org_id')
            if 'dep_id' in request.POST:
                obj.group_dep_id = request.POST.get('dep_id')

            obj.save()
            # return HttpResponse('Success')

            # Add Group Menu Permision in DB Start#

            GroupMenuPermissions.objects.filter(group_id=id).delete()
            menu_ids = request.POST.getlist('menus')
            submenu_ids = request.POST.getlist('submenus')

            for submenuid in submenu_ids:
                permit_obj = GroupMenuPermissions(group_id=id, submenu_id=submenuid)
                permit_obj.save()

            for menuid in menu_ids:
                permit_obj = GroupMenuPermissions(group_id=id, menu_id=menuid)
                permit_obj.save()
            # Add Group Menu Permision in DB End#

            # User Group Membership Start#

            UserGroupMembership.objects.filter(m_group_id=id).delete()
            user_membership = request.POST.getlist('user_membership')
            if user_membership:
                if 'multiselect-all' in user_membership:
                    user_membership.remove('multiselect-all')
            for user_id in user_membership:
                membership_obj = UserGroupMembership(m_user_id=user_id, m_group_id=id)
                membership_obj.save()

            # User Group Membership End#    

            #Adding Permission Actions to GroupActionPermission table            
            permission_actions = request.POST.getlist('permission_action')
            permission_sub_actions = request.POST.getlist('permission_sub_action')
            group = Group.objects.get(pk=id)
            GroupActionPermission.objects.filter(group_id=group.group_id).delete()
            GroupSubActionPermission.objects.filter(group_id=group.group_id).delete()
            for permission_action in permission_actions:
                permission_action_obj = PermissionAction.objects.get(perm_act_id=permission_action)
                group_act_obj = GroupActionPermission(group_id=group.group_id, perm_act_id=permission_action_obj.perm_act_id)
                group_act_obj.save()
            for permission_sub_action in permission_sub_actions:
                per_sub_action_obj = PermissionSubAction.objects.get(sub_act_id=permission_sub_action)
                group_act_obj = GroupSubActionPermission(group_id=group.group_id, sub_act_id=per_sub_action_obj.sub_act_id)
                group_act_obj.save()            
            #END Adding Permission Actions to GroupActionPermission table 

            messages.success(request, 'Request Succeed! Group updated.')
            return redirect('listGroup')
    else:
        messages.error(request, 'Request Failed! Group cannot be updated.Please try again.')
        return redirect('listGroup')

# Group Update Request End#


# Group Delete Request Start#

@active_user_required
def deleteGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # Instead of having an error on your server,
    # your user will get a 404 meaning that he tries to access a non existing resource.
    # data = get_object_or_404(Organization , pk = id)
    group_id = request.GET.get('GrpID')
    try:
        id = signing.loads(group_id,salt=settings.SALT_KEY)
        obj = Group.objects.get(pk=id)
    except Group.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listGroup')
    else:
        #Deleting Permission Actions to GroupActionPermission table            
        group = Group.objects.get(pk=id)
        GroupActionPermission.objects.filter(group_id=group.group_id).delete()
        GroupSubActionPermission.objects.filter(group_id=group.group_id).delete()            
        #END Deleting Permission Actions to GroupActionPermission table 

        #Deleting Task Group Restrict To TaskGroupRestricts table            
        group = Group.objects.get(pk=id)
        TaskGroupRestrict.objects.filter(tgr_group_id=group.group_id).delete()           
        #END Deleting Task Group Restrict To TaskGroupRestricts table 

        #Deleting Task Restrict To TaskGroupRestricts table            
        group = Group.objects.get(pk=id)
        TaskRestrict.objects.filter(tr_group_id=group.group_id).delete()           
        #END Deleting Task  Restrict To TaskGroupRestricts table 

        obj.gp_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Group deleted.')
        return redirect('listGroup')

# Group Delete Request End#


# Group Add Request Start#

@active_user_required
def exportGroup(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    return render(request, 'Organization/org_add.html')

# Group Add Request End#


#Datatable Code Start Here#
class GroupListJson(BaseDatatableView):
    # The model we're going to show
    model = Group

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
        is_active = self.request.GET.get('is_active')
        user_id = self.request.user.id
        org_id = self.request.user.user_org_id
        global_user = isGlobalUser(self.request)
        # if self.request.user.user_type_slug != global_user:
        if(is_active == '1'):
            return Group.objects.filter(gp_is_delete=0, gp_is_active = 1).filter(group_org_id=org_id)
        else:
            return Group.objects.filter(gp_is_delete=0).filter(group_org_id=org_id)
        # else:
        #     if(is_active == '1'):
        #         return Group.objects.filter(gp_is_delete=0, gp_is_active = 1)
        #     else:
        #         return Group.objects.filter(gp_is_delete=0)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.group_id,salt=settings.SALT_KEY)
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_GroupEdit?GrpID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_GroupDel?GrpID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'group_cus_id': 
            return '<a href="Home_ViewGroup?GrpID=' + str(rid) + '">'+str(row.group_cus_id)+'</a>'
        elif column == 'membership_type':
            if row.membership_type == 0:
                return 'Agent Only'
            else:
                return 'Any'
        elif column == 'gp_is_active':
            if row.gp_is_active == 1:
                return 'Y'
            else:
                return 'N'
        elif column == 'group_org_id':
            if row.group_org_id == 0:
               return ''
            else:
                # obj = Organization.objects.filter(org_id=row.client_org_id).values('org_name')
                org_name = Organization.objects.only('org_name').get(pk=row.group_org_id).org_name
                return org_name
        else:
            return super(GroupListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            # org = group_org.org_name
            qs = qs.filter(Q(group_cus_id__icontains=search) | Q(group_display_name__icontains=search)| Q(group_org__org_name__icontains=search))
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

#SHOW MEMERS
@active_user_required
def groupMembers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/Group/group_members.html', context)

#GET ALL  DATA FOR EJ2 GRID
@csrf_exempt
def getAllGroupsJson(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    global_user = isGlobalUser(request)
    if request.user.user_type_slug != global_user:
        allGroups = Group.objects.raw('''
            select a.*
                ,(
                    select ORG.org_name
                    from AT_Organizations ORG WITH(NOLOCK)
                    WHERE ORG.org_id = a.group_org_id
                    AND ORG.org_is_active = 1
                    AND ORG.org_is_delete = 0
                ) as org_name
            from AT_Groups a with(nolock)
            where a.gp_is_delete = 0
            and a.gp_is_active = 1 and group_org_id = '''+str(request.user.user_org_id)+ '''
        ''')
    else:
        allGroups = Group.objects.raw('''
            select a.*
                ,(
                    select ORG.org_name
                    from AT_Organizations ORG WITH(NOLOCK)
                    WHERE ORG.org_id = a.group_org_id
                    AND ORG.org_is_active = 1
                    AND ORG.org_is_delete = 0
                ) as org_name
            from AT_Groups a with(nolock)
            where a.gp_is_delete = 0
            and a.gp_is_active = 1
        ''')
    resultArray = []
    for group in allGroups:
        rid = signing.dumps(group.group_id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['group_id'] = group.group_id
        resutlCurrentRecord['group_cus_id_link'] = '<a href="Home_ViewGroup?GrpID=' + str(rid) + '">'+str(group.group_cus_id)+'</a>'
        resutlCurrentRecord['group_cus_id'] = group.group_cus_id
        if group.membership_type == 0:
            resutlCurrentRecord['group_type'] = "Agents Only"
        else:
            resutlCurrentRecord['group_type'] = "Any"
        resutlCurrentRecord['group_display_name'] = group.group_display_name
        resutlCurrentRecord['org_name'] = group.org_name
        resultArray.append(resutlCurrentRecord)
    
    return HttpResponse(json.dumps(resultArray), content_type="application/json")

#GET client USERS EJ2 GRID JSON
@csrf_exempt
def getGroupMembers(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    groupString = request.GET.get('$filter')
    if " and " in groupString:
        searchedtext = groupString.split("',tolower(cast(username, 'Edm.String'))))",1)[0] 
        searchedtext = searchedtext.split("and (substringof('",1)[1] 
        searchedtext = '%'+searchedtext+'%'
        group_id = groupString.split("group_id eq ",1)[1] 
        group_id = group_id.split(" and (s",1)[0] 
        groupMembers = UserGroupMembership.objects.raw('''
            SELECT *
                ,(
                    SELECT U.username
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.is_delete = 0
                    AND U.is_active = 1
                ) AS username
                ,(
                    SELECT U.first_name
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.is_delete = 0
                    AND U.is_active = 1
                ) AS first_name
                ,(
                    SELECT U.last_name
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.is_delete = 0
                    AND U.is_active = 1
                ) AS last_name
            FROM AT_UserGroupMembership UGM
            WHERE UGM.m_group_id = %s
            AND(
                (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.username like %s
                    AND U.is_delete = 0
                    AND U.is_active = 1
                )>0
                OR
                (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.first_name like %s
                    AND U.is_delete = 0
                    AND U.is_active = 1
                )>0
                OR
                (
                    SELECT COUNT(*)
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.last_name like %s
                    AND U.is_delete = 0
                    AND U.is_active = 1
                )>0
            )
        ''',[group_id,searchedtext,searchedtext,searchedtext])
        groupMembersCount = len(list(groupMembers))
    else: 
        group_id = groupString.split("eq ",1)[1] 
        group_id = group_id.strip()
        # groups = UserGroupMembership.objects.prefetch_related().filter(m_group_id=group_id)
        query  = '''
            SELECT *
                ,(
                    SELECT U.username
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.is_delete = 0
                    AND U.is_active = 1
                ) AS username
                ,(
                    SELECT U.first_name
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.is_delete = 0
                    AND U.is_active = 1
                ) AS first_name
                ,(
                    SELECT U.last_name
                    FROM AT_Users U
                    WHERE U.id = UGM.m_user_id
                    AND U.is_delete = 0
                    AND U.is_active = 1
                ) AS last_name
            FROM AT_UserGroupMembership UGM
            WHERE UGM.m_group_id = '''+group_id+'''
            AND (
                SELECT COUNT(*)
                FROM AT_Users U
                WHERE U.ID = m_user_id
                AND U.is_delete = 0
                AND U.is_active = 1
            )>0
        '''
        groupMembers = UserGroupMembership.objects.raw(query)
        groupMembersCount = len(list(groupMembers))

    resultArray = []
    for groupMember in groupMembers:
        rid = signing.dumps(groupMember.m_user_id,salt=settings.SALT_KEY)
        resutlCurrentRecord = {}
        resutlCurrentRecord['username'] = '<a href="Home_ViewUser?UserID=' + str(rid) + '">'+str(groupMember.username)+'</a>'
        resutlCurrentRecord['first_name'] = groupMember.first_name
        resutlCurrentRecord['last_name'] = groupMember.last_name
        resultArray.append(resutlCurrentRecord)
    mainArray = {}
    mainArray['results'] = resultArray
    mainArray['__count'] = groupMembersCount
    externalArray = {}
    externalArray['d'] = mainArray

    return HttpResponse(json.dumps(externalArray), content_type="application/json")

#EXPORT Group USERS
@csrf_exempt
def export_users_by_group_xls(request):

    result_data = getArrayOfallUsersByGroup()
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename= GroupMembersToExcel.xlsx'.format()
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
        ('Group Name', 15),
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
        title='GroupMembersToExcel',
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
            (client["Group Name"], 'Normal'),
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

        if client["Group Name"] != "":
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

#Export Group List End Here#

# Get allUsersByGroup starts
def getArrayOfallUsersByGroup():
    getAll = Group.objects.filter(gp_is_active=1,gp_is_delete=0)
    mainArray = []
    for getAll in getAll:
        groupData = {}
        groupData['Group Name'] = getAll.group_display_name
        groupData['User ID'] = ''
        groupData['Display Name'] = ''
        groupData['First Name'] = ''
        groupData['Last Name'] = ''
        groupData['Email'] = ''
        groupData['Phone'] = ''
        groupData['Address1'] = ''
        groupData['Address2'] = ''
        groupData['City'] = ''
        groupData['State'] = ''
        groupData['Zip'] = ''
        
        mainArray.append(groupData)
        getAllUsers = User.objects.raw('''
        SELECT U.*
        from AT_Users U
        INNER JOIN AT_UserGroupMembership UGM ON UGM.m_user_id = U.id
        WHERE UGM.m_group_id = %s
        AND U.is_active = 1
        AND U.is_delete = 0
        ''',[getAll.group_id])
        
        for getAllUsers in getAllUsers:
            usersData = {}
            usersData['Group Name'] = ''
            usersData['User ID'] = getAllUsers.username
            usersData['Display Name'] = getAllUsers.last_name+', '+getAllUsers.first_name
            usersData['First Name'] = getAllUsers.first_name
            usersData['Last Name'] = getAllUsers.last_name
            usersData['Email'] = getAllUsers.email
            usersData['Phone'] = getAllUsers.phone_no
            usersData['Address1'] = getAllUsers.address1
            usersData['Address2'] = getAllUsers.address2
            usersData['City'] = getAllUsers.user_city
            usersData['State'] = getAllUsers.user_state
            usersData['Zip'] = getAllUsers.user_zip_code
            mainArray.append(usersData)
    return mainArray
# Get allUsersByOrganization ends

# Group View Start#
@active_user_required
def viewGroup(request):
    id = request.GET.get('GrpID')
    try:
        group_id = signing.loads(id,salt=settings.SALT_KEY)
        data = Group.objects.get(pk=group_id)
        data.organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
        data.departments = Department.objects.filter(d_is_delete=0)
        permissions = PermissionSection.objects.filter(is_active = 1).all() 
        print(permissions)
    except Group.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listGroup')
    else:
        load_sidebar = get_sidebar(request)
        menus_allowed = list(get_group_menus_permit(request, group_id))
        submenus_allowed = list(get_group_submenus_permit(request, group_id))
        actions_list = group_action_permissions(request, data)
        sub_actions_list = group_sub_action_permissions(request, data)
        disabled_actions= group_permissions_not_allowed(request)
        disabled_sub_action= group_sub_permissions_not_allowed(request)
        # print(disabled_actions)
        # print(disabled_sub_action)
        context = {
            'sidebar': load_sidebar,
            'menus_allowed': menus_allowed,
            'submenus_allowed': submenus_allowed,
            'data': data,
            'permissions': permissions,
            'actions_list': actions_list,
            'sub_actions_list': sub_actions_list,
            'disabled_actions': disabled_actions,
            'disabled_sub_action': disabled_sub_action,
        }
    return render(request, 'itrak/Group/group_view.html', context)

# Group View End#