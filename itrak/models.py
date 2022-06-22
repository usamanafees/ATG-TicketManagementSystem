from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

# Create your models here.

# Organization Model Start#
class Organization(models.Model):
    org_id = models.AutoField(primary_key=True)
    org_name = models.CharField(max_length=100)
    is_internal = models.BooleanField(default=True)
    additional_orgs = models.CharField(max_length=50)
    site_title = models.CharField(max_length=100)
    left_org_logo = models.CharField(max_length=200)
    right_org_logo = models.CharField(max_length=200)
    org_contact_person = models.CharField(max_length=100)
    org_email = models.EmailField(max_length=100)
    org_phone_no = models.CharField(max_length=100)
    org_address1 = models.TextField()
    org_address2 = models.TextField()
    org_city = models.CharField(max_length=100)
    org_state = models.CharField(max_length=100)
    org_zip_code = models.CharField(max_length=50)
    org_www_address = models.CharField(max_length=100)
    org_from_reply_email = models.EmailField(max_length=100)
    org_from_reply_address = models.TextField()
    org_note = models.CharField(max_length=100)
    org_is_active = models.BooleanField(default=True)
    org_is_delete = models.BooleanField(default=False)
    org_created_at = models.DateTimeField(auto_now_add=True)
    org_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.org_name

    def save(self, *args, **kwargs):
        if not self.org_id:
            self.org_created_at = timezone.now()
        self.org_modified_at = timezone.now()
        return super(Organization, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Organizations"


# Organization Model End#

# Client Model Start#
class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    client_cus_id = models.CharField(max_length=255)
    client_name = models.CharField(max_length=100)
    client_contact_person = models.CharField(max_length=50)
    client_org = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True)
    client_email = models.EmailField(max_length=100)
    client_phone = models.CharField(max_length=100)
    client_second_phone = models.CharField(max_length=100)
    client_fax = models.CharField(max_length=100)
    client_address1 = models.TextField()
    client_address2 = models.TextField()
    client_city = models.CharField(max_length=100)
    client_state = models.CharField(max_length=100)
    client_zip_code = models.CharField(max_length=50)
    client_country = models.CharField(max_length=100)
    cl_is_active = models.BooleanField(default=True)
    cl_is_delete = models.BooleanField(default=False)
    client_created_at = models.DateTimeField(editable=False)
    client_modified_at = models.DateTimeField()

    def __str__(self):
        return self.client_name

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_created_at = timezone.now()
        self.client_modified_at = timezone.now()
        return super(Client, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Clients"


# Client Model End#


# Department Model Start#
class Department(models.Model):
    dep_id = models.AutoField(primary_key=True)
    dep_name = models.CharField(max_length=100)
    d_is_internal = models.BooleanField(default=True)
    d_is_active = models.BooleanField(default=True)
    d_is_delete = models.BooleanField(default=False)
    d_created_at = models.DateTimeField(editable=False)
    d_modified_at = models.DateTimeField()
    user_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.dep_name

    def save(self, *args, **kwargs):
        if not self.dep_id:
            self.d_created_at = timezone.now()
        self.d_modified_at = timezone.now()
        return super(Department, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Departments"


# Department Model End#


# Group Model Start#
class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_cus_id = models.CharField(max_length=255)
    group_display_name = models.CharField(max_length=100)
    membership_type = models.IntegerField()
    group_org = models.ForeignKey(Organization, related_name='groupOrg', on_delete=models.DO_NOTHING,null=True)
    group_dep = models.ForeignKey(Department, related_name='groupDep', on_delete=models.DO_NOTHING, blank=True, null=True)
    group_email = models.EmailField(max_length=100)
    group_phone = models.CharField(max_length=100)
    group_mobile_sms_email = models.EmailField(max_length=100)
    group_suppress_all_email = models.BooleanField(default=False)
    gp_is_active = models.BooleanField(default=True)
    gp_is_delete = models.BooleanField(default=False)
    gp_created_at = models.DateTimeField(editable=False)
    gp_modified_at = models.DateTimeField()

    def __str__(self):
        return self.group_display_name

    def save(self, *args, **kwargs):
        if not self.group_id:
            self.gp_created_at = timezone.now()
        self.gp_modified_at = timezone.now()
        return super(Group, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Groups"


# Group Model End#

# Role Model Start#
class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    role_is_active = models.BooleanField(default=True)
    role_is_delete = models.BooleanField(default=False)
    role_created_at = models.DateTimeField(editable=False)
    role_modified_at = models.DateTimeField()

    def __str__(self):
        return self.role_name

    def save(self, *args, **kwargs):
        if not self.role_id:
            self.role_created_at = timezone.now()
        self.role_modified_at = timezone.now()
        return super(Role, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Roles"


# Role Model End#


# BaseUserManager Start#
class UserManger(BaseUserManager):
    def create_user(self, username, first_name, last_name, password=None, is_active=True, is_admin=False, is_superuser=False):
        if not username:
            raise ValueError("User must have an username")
        if not password:
            raise ValueError("User must have an password")
        user_obj = self.model(
            username= username
        )
        user_obj.first_name = first_name,
        user_obj.last_name = last_name,
        user_obj.set_password(password) #change your password
        user_obj.admin = is_admin
        user_obj.is_superuser = is_superuser
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_normaluser(self, username, first_name, last_name, password=None):
        user = self.create_user(
            self,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password = password,
            is_active=True,
        )

    def create_superuser(self, username, first_name, last_name, password=None, **kwargs):
        user = self.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=True,
            is_admin=True,
            is_superuser=True,
            **kwargs
        )

# BaseUserManager Ends#

# User Model Start #
class User(AbstractBaseUser, PermissionsMixin):
    user_cus_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    cnic = models.CharField(max_length=100, default="xxxxx-xxxxxxx-x")
    email = models.CharField(unique=True, max_length=100)
    username = models.CharField(unique=True, max_length=100)
    phone_no = models.CharField(max_length=100)
    mob_sms_email = models.CharField(max_length=100)
    user_org = models.ForeignKey(Organization,related_name="UserOrgId", on_delete=models.DO_NOTHING, null=True, blank=True)
    user_client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True)
    user_dep = models.ForeignKey(Department, on_delete=models.DO_NOTHING, blank=True, null=True)
    address1 = models.TextField()
    address2 = models.TextField()
    user_city = models.CharField(max_length=100)
    user_state = models.CharField(max_length=100)
    user_zip_code = models.CharField(max_length=50, null=True)
    user_country = models.CharField(max_length=100)
    user_time_zone = models.CharField(max_length=100, null=True)
    user_type = models.CharField(max_length=100)
    admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    login_permit = models.BooleanField(default=True)
    suppress_email = models.BooleanField(default=True)
    is_cloned = models.BooleanField(default=False)
    is_merged = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(editable=False)
    modified_at = models.DateTimeField()
    default_password = models.CharField(max_length=200, null=True)
    user_role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_template_user= models.BooleanField(default=False)
    user_type_slug = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    #USERNAME_Field and Password are required by default#
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManger()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(User, self).save(*args, **kwargs)

    @property
    def is_admin(self):
        self.admin

    class Meta:
        db_table = "AT_Users"

# User Model End #

# System Sections Model Start#

class Sections(models.Model):
    section_id = models.AutoField(primary_key=True)
    section_name = models.CharField(max_length=100)
    section_order = models.IntegerField(default=0,null=True)
    section_is_active = models.BooleanField(default=True)
    section_is_delete = models.BooleanField(default=False)
    section_created_at = models.DateTimeField(editable=False)
    section_modified_at = models.DateTimeField()

    def __str__(self):
        return self.section_name

    def save(self, *args, **kwargs):
        if not self.section_id:
            self.section_created_at = timezone.now()
        self.section_modified_at = timezone.now()
        return super(Sections, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Sections"

# System Sections Model End#


# System Menus Model Start#

class Menus(models.Model):
    menu_id = models.AutoField(primary_key=True)
    menu_name = models.CharField(max_length=100)
    menu_link = models.CharField(max_length=100)
    m_section = models.IntegerField(default=0)
    icon = models.CharField(max_length=200, null=True)
    menu_order = models.IntegerField(null=True)
    menu_permit_order = models.IntegerField(null=True)
    menu_permit_active = models.BooleanField(default=False)
    menu_is_active = models.BooleanField(default=True)
    menu_is_delete = models.BooleanField(default=False)
    menu_created_at = models.DateTimeField(editable=False)
    menu_modified_at = models.DateTimeField()


    def __str__(self):
        return self.menu_name

    def save(self, *args, **kwargs):
        if not self.menu_id:
            self.menu_created_at = timezone.now()
        self.menu_modified_at = timezone.now()
        return super(Menus, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Menus"

# System Menus Model End#


# System Sub Menus Model Start#

class SubMenus(models.Model):

    submenu_id = models.AutoField(primary_key=True)
    submenu_name = models.CharField(max_length=100)
    submenu_link = models.CharField(max_length=100)
    submenu_menu_id = models.IntegerField(default=0)
    submenu_order = models.IntegerField(null=True)
    submenu_permit_order = models.IntegerField(null=True)
    submenu_permit_active = models.BooleanField(default=False)
    submenu_is_active = models.BooleanField(default=True)
    submenu_is_delete = models.BooleanField(default=False)
    submenu_created_at = models.DateTimeField(editable=False)
    submenu_modified_at = models.DateTimeField()

    def __str__(self):
        return self.submenu_name

    def save(self, *args, **kwargs):
        if not self.submenu_id:
            self.submenu_created_at = timezone.now()
        self.submenu_modified_at = timezone.now()
        return super(SubMenus, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SubMenus"

# System Sub Menus Model End#


# User Menus Permissions Model Start#

class UserMenuPermissions(models.Model):

    id = models.AutoField(primary_key=True)
    # user_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name="permissionUser", on_delete=models.DO_NOTHING,null=True, blank=True)
    # menu_id = models.IntegerField(null=True)
    menu = models.ForeignKey(Menus, related_name="permissionMenu", on_delete=models.DO_NOTHING,null=True, blank=True)
    # submenu_id = models.IntegerField(null=True)
    submenu = models.ForeignKey(SubMenus, related_name="permissionSubMenu", on_delete=models.DO_NOTHING,null=True, blank=True)
    created_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(UserMenuPermissions, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserMenuPermissions"

# User Menus Permissions Model End#


# Group Menus Permissions Model Start#

class GroupMenuPermissions(models.Model):

    id = models.AutoField(primary_key=True)
    # group_id = models.CharField(max_length=100)
    group = models.ForeignKey(Group, related_name="permissionGroup", on_delete=models.DO_NOTHING,null=True, blank=True)
    # menu_id = models.IntegerField(null=True)
    menu = models.ForeignKey(Menus, related_name="permissionGroupMenu", on_delete=models.DO_NOTHING,null=True, blank=True)
    # submenu_id = models.IntegerField(null=True)
    submenu = models.ForeignKey(SubMenus, related_name="permissionGroupSubMenu", on_delete=models.DO_NOTHING,null=True, blank=True)
    created_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(GroupMenuPermissions, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_GroupMenuPermissions"

# Group Menus Permissions Model End#


# User Group Membership Start#

class UserGroupMembership(models.Model):

    membership_id = models.AutoField(primary_key=True)
    m_group = models.ForeignKey(Group, related_name="groupMembership", on_delete=models.DO_NOTHING, blank=True, null=True)
    m_user = models.ForeignKey(User, related_name="userMembership", on_delete=models.DO_NOTHING, blank=True, null=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(editable=False)
    m_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.membership_id

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(UserGroupMembership, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserGroupMembership"

# User Group Membership End#


# Client Information Record Model Start#

class ClientInformation(models.Model):
    clientinfo_id = models.AutoField(primary_key=True)
    record_locator = models.CharField(max_length=255)
    caller_name = models.CharField(max_length=100)
    caller_phone = models.CharField(max_length=50)
    caller_email = models.EmailField(max_length=100)
    passenger_name = models.CharField(max_length=100)
    clientinfo_is_active = models.BooleanField(default=True)
    clientinfo_is_delete = models.BooleanField(default=False)
    clientinfo_created_at = models.DateTimeField(editable=False)
    clientinfo_modified_at = models.DateTimeField()

    def __str__(self):
        return self.record_locator

    def save(self, *args, **kwargs):
        if not self.clientinfo_id:
            self.clientinfo_created_at = timezone.now()
        self.clientinfo_modified_at = timezone.now()
        return super(ClientInformation, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ClientInformation"


# Client Information Record Model End#


# Ticket typeRecord Model Start#

class TicketType(models.Model):
    ttype_id = models.AutoField(primary_key=True)
    ttype_name = models.CharField(max_length=100)
    t_type_display_order = models.CharField(max_length=50)
    t_type_track_tip = models.TextField()
    display_agent_only = models.BooleanField(default=True)
    parent_id = models.IntegerField(default=0, null=True)
    has_parent = models.BooleanField(default=False)
    has_child = models.BooleanField(default=False)
    ttype_is_delete = models.BooleanField(default=False)
    ttype_is_active = models.BooleanField(default=True)
    ttype_created_at = models.DateTimeField(editable=False)
    ttype_modified_at = models.DateTimeField()
    user_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.ttype_name

    def save(self, *args, **kwargs):
        if not self.ttype_id:
            self.ttype_created_at = timezone.now()
        self.ttype_modified_at = timezone.now()
        return super(TicketType, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketType"


# Ticket type Record Model End#


# Priority typeRecord Model Start#

class Priority(models.Model):
    priority_id = models.AutoField(primary_key=True)
    priority_name = models.CharField(max_length=100, null=True)
    priority_color = models.CharField(max_length=100)
    p_display_order = models.CharField(max_length=50)
    popup_message = models.TextField()
    prior_is_delete = models.BooleanField(default=False)
    prior_created_at = models.DateTimeField(editable=False)
    prior_modified_at = models.DateTimeField()
    user_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.priority_name

    def save(self, *args, **kwargs):
        if not self.priority_id:
            self.prior_created_at = timezone.now()
        self.prior_modified_at = timezone.now()
        return super(Priority, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Priority"


# Priority type Record Model End#



# Solutions Model Start#

class Solution(models.Model):
    solution_id = models.AutoField(primary_key=True)
    solution_cus_id = models.CharField(max_length=100, null=True)
    solution_text = models.CharField(max_length=100)
    sol_display_order = models.CharField(max_length=50)
    sol_is_delete = models.BooleanField(default=False)
    sol_created_at = models.DateTimeField(editable=False)
    sol_modified_at = models.DateTimeField()
    user_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.solution_text

    def save(self, *args, **kwargs):
        if not self.solution_id:
            self.sol_created_at = timezone.now()
        self.sol_modified_at = timezone.now()
        return super(Solution, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Solution"


# Solutions Model End#


# Sub Status Model Start#

class SubStatus(models.Model):
    sub_status_id = models.AutoField(primary_key=True)
    sub_status_text = models.CharField(max_length=100)
    sstatus_display_order = models.CharField(max_length=50)
    sstatus_is_delete = models.BooleanField(default=False)
    sstatus_created_at = models.DateTimeField(editable=False)
    sstatus_modified_at = models.DateTimeField()
    ss_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.sub_status_text

    def save(self, *args, **kwargs):
        if not self.sub_status_id:
            self.sstatus_created_at = timezone.now()
        self.sstatus_modified_at = timezone.now()
        return super(SubStatus, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SubStatus"


# Sub Status Model End#



# Task Model Start#

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_type = models.IntegerField(default=1)
    task_description = models.CharField(max_length=100)
    task_display_order = models.CharField(max_length=50)
    task_is_active = models.BooleanField(default=True)
    task_is_delete = models.BooleanField(default=False)
    task_created_at = models.DateTimeField(editable=False)
    task_modified_at = models.DateTimeField()
    task_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.task_description

    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_created_at = timezone.now()
        self.task_modified_at = timezone.now()
        return super(Task, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Task"


# Task Group Model End#

class TaskGroup(models.Model):
    taskgroup_id = models.AutoField(primary_key=True)
    taskgroup_description = models.CharField(max_length=100)
    taskgroup_display_order = models.CharField(max_length=50)
    taskgroup_is_active = models.BooleanField(default=True)
    taskgroup_is_delete = models.BooleanField(default=False)
    taskgroup_created_at = models.DateTimeField(editable=False)
    taskgroup_modified_at = models.DateTimeField()
    task_group_org_id = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.taskgroup_description

    def save(self, *args, **kwargs):
        if not self.taskgroup_id:
            self.taskgroup_created_at = timezone.now()
        self.taskgroup_modified_at = timezone.now()
        return super(TaskGroup, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TaskGroup"

# Task Group Model End#


# Ticekt Model End#

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    submitted_date = models.DateField(null=True)
    submitted_time = models.TimeField(null=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    ticket_status = models.IntegerField(default=0, null=True)
    ticket_sub_status = models.ForeignKey(SubStatus, related_name="ticketSubStatus", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_type = models.ForeignKey(TicketType, related_name="ticketType", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype1 = models.ForeignKey(TicketType, related_name="ticketSubType1", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype2 = models.ForeignKey(TicketType, related_name="ticketSubType2", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype3 = models.ForeignKey(TicketType, related_name="ticketSubType3", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype4 = models.ForeignKey(TicketType, related_name="ticketSubType4", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_org = models.ForeignKey(Organization, related_name="ticketOrg", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_caller = models.ForeignKey(User, related_name="ticketCaller", on_delete=models.DO_NOTHING, blank=True, null=True)
    # ticket_client = models.ForeignKey(Client, related_name="ticketClient", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_clientinformation = models.ForeignKey(ClientInformation, related_name="ticketClientInfo", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_record_locator = models.CharField(max_length=255,null=True)
    ticket_caller_name = models.CharField(max_length=100,null=True)
    ticket_caller_phone = models.CharField(max_length=50,null=True)
    ticket_caller_email = models.EmailField(max_length=100,null=True)
    ticket_passenger_name = models.CharField(max_length=100,null=True)
    subject = models.CharField(max_length=100, null=True, verbose_name='Ticket Subject')
    description = models.TextField(null=True)
    priority = models.ForeignKey(Priority, related_name="ticketPriority", on_delete=models.DO_NOTHING, blank=True, null=True)
    is_traveler_vip = models.CharField(max_length=10, null=True)
    is_payout_required  = models.CharField(max_length=10, null=True)
    agent_error_goodwill  = models.CharField(max_length=10, null=True)
    amount_saved = models.CharField(max_length=100, null=True)
    airline_ticket_no = models.CharField(max_length=100, null=True)
    agent_responsible = models.CharField(max_length=100, null=True)
    vendor_responsible = models.CharField(max_length=100, null=True)
    vresponsible_city = models.CharField(max_length=100, null=True)
    ticket_payout_amount = models.CharField(max_length=100, null=True)
    ticket_order_of_pay = models.CharField(max_length=100, null=True)
    ticket_attention = models.CharField(max_length=100, null=True)
    ticket_company = models.CharField(max_length=100, null=True)
    ticket_address = models.CharField(max_length=100, null=True)
    notes_on_check = models.CharField(max_length=100, null=True)
    check_number = models.CharField(max_length=100, null=True)
    check_approved_by = models.CharField(max_length=100, null=True)
    corr_cont_actions = models.TextField(null=True)
    ticket_root_cause = models.TextField(null=True)
    corrective_action = models.TextField(null=True)
    ticket_next_action = models.ForeignKey(User, related_name="ticketNextAssign", on_delete=models.DO_NOTHING, blank=True,null=True)
    ticket_next_action_by = models.ForeignKey(User, related_name="ticketNextAssignBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    ticket_next_action_at = models.DateTimeField(null=True)
    ticket_assign_to = models.ForeignKey(User, related_name="ticketAssignTo", on_delete=models.DO_NOTHING, blank=True,null=True)
    ticket_assign_by = models.ForeignKey(User, related_name="ticketAssignBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    ticket_assign_at = models.DateTimeField(null=True)
    total_labour_hours = models.TimeField(null=True)
    ticket_note = models.TextField(null=True)
    ticket_is_open = models.BooleanField(default=True)
    ticket_is_open_by = models.ForeignKey(User, related_name="ticketIsOpenBy", on_delete=models.DO_NOTHING,blank=True,null=True)
    ticket_is_open_at = models.DateTimeField(null=True)
    ticket_is_close = models.BooleanField(default=False)
    ticket_is_close_by = models.ForeignKey(User, related_name="ticketIsCloseBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    ticket_is_close_at = models.DateTimeField(null=True)
    ticket_is_reopen = models.BooleanField(default=False)
    ticket_is_reopen_by = models.ForeignKey(User, related_name="ticketIsReopenBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    ticket_is_reopen_at = models.DateTimeField(null=True)
    ticket_is_active = models.BooleanField(default=True)
    ticket_is_delete = models.BooleanField(default=False)
    ticket_created_by = models.ForeignKey(User, related_name="ticketCreatedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_modified_by = models.ForeignKey(User, related_name="ticketModifiedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_closed_by = models.ForeignKey(User, related_name="ticketClosedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_created_at = models.DateTimeField(editable=False)
    ticket_modified_at = models.DateTimeField()
    ticket_closed_at = models.DateTimeField(null=True)
    account = models.ForeignKey('Globalaccts', models.DO_NOTHING, blank=True, null=True)
    ticket_currency = models.TextField(null=True)
    # account = models.IntegerField(default=0)
    # account = models.ForeignKey(GlobalACCTS, related_name="account", on_delete=models.CASCADE, blank=True, null=True)
    # ticket_dep = models.ForeignKey(Department, related_name="ticketDep", on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_created_at = timezone.now()
            self.ticket_is_open_at = timezone.now()
        self.ticket_modified_at = timezone.now()
        return super(Ticket, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Tickets"

# Ticekt Model End#


# Ticket Notes Model End#

class TicketNote(models.Model):
    note_id = models.AutoField(primary_key=True)
    note_detail = models.TextField(null=True)
    note_ticket = models.ForeignKey(Ticket, related_name="ticketNote", on_delete=models.DO_NOTHING, blank=True, null=True)
    labour_hours = models.TimeField(null=True)
    tnote_laborhour_hours = models.CharField(max_length=50, null=True)
    tnote_laborhour_minutes = models.CharField(max_length=50, null=True)
    is_private = models.BooleanField(default=False)
    note_created_by = models.ForeignKey(User, related_name="noteCreatedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    note_modified_by = models.ForeignKey(User, related_name="noteModifiedBy", on_delete=models.DO_NOTHING,blank=True, null=True)
    note_created_at = models.DateTimeField(editable=False)
    note_modified_at = models.DateTimeField()
    note_is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.note_detail

    def save(self, *args, **kwargs):
        if not self.note_id:
            self.note_created_at = timezone.now()
        self.note_modified_at = timezone.now()
        return super(TicketNote, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketNote"

# Ticket Notes Model End#


# Ticket Notes Model End#

class TicketUserRoleLog(models.Model):
    urlog_id = models.AutoField(primary_key=True)
    urlog_ticket = models.ForeignKey(Ticket, related_name="ticketURLog", on_delete=models.DO_NOTHING, blank=True, null=True)
    urlog_user = models.ForeignKey(User, related_name="userURLog", on_delete=models.DO_NOTHING, blank=True, null=True)
    urlog_event = models.CharField(max_length=50, null=True)
    urlog_created_by = models.ForeignKey(User, related_name="urlogCreatedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    urlog_modified_by = models.ForeignKey(User, related_name="urlogModifiedBy", on_delete=models.DO_NOTHING,blank=True, null=True)
    urlog_created_at = models.DateTimeField(editable=False)
    urlog_modified_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.urlog_id:
            self.urlog_created_at = timezone.now()
        self.urlog_modified_at = timezone.now()
        return super(TicketUserRoleLog, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketUserRoleLog"

# Ticket Notes Model End#



# Task Group Manager Model End#

class TaskGroupManager(models.Model):
    taskgp_mgr_id = models.AutoField(primary_key=True)
    tmgrgp_task = models.ForeignKey(Task, related_name="taskgroupManager", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgrgp_group = models.ForeignKey(TaskGroup, related_name="tgroupManager", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_task_type = models.IntegerField(default=1)
    is_group = models.BooleanField(default=False)
    tmgrgp_display_order = models.CharField(max_length=50, null=True)
    tg_task_note = models.TextField(null=True)
    tg_task_due_date = models.DateField(null=True)
    tg_task_dependency = models.BooleanField(default=False)
    tg_task_depend_order = models.CharField(max_length=50, null=True)
    tg_task_assigned_to = models.ForeignKey(User, related_name="tgTaskAssign", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_ttype_group_yes = models.ForeignKey(TaskGroup, related_name="tgttypeYes", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_ttype_copen_yes = models.BooleanField(default=False)
    tg_ttype_cticket_yes = models.BooleanField(default=False)
    tg_ttype_substatus_yes = models.ForeignKey(SubStatus, related_name="tgttypeSubStatusYes", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_ttype_group_no = models.ForeignKey(TaskGroup, related_name="tgttypeNo", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_ttype_copen_no = models.BooleanField(default=False)
    tg_ttype_cticket_no = models.BooleanField(default=False)
    tg_ttype_substatus_no = models.ForeignKey(SubStatus, related_name="tgttypeSubStatusNo", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_ttype_group_na = models.ForeignKey(TaskGroup, related_name="tgttypeNA", on_delete=models.DO_NOTHING, blank=True, null=True)
    tg_ttype_copen_na = models.BooleanField(default=False)
    tg_ttype_cticket_na = models.BooleanField(default=False)
    tg_ttype_substatus_na = models.ForeignKey(SubStatus, related_name="tgttypeSubStatusNA", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgrgp_is_active = models.BooleanField(default=True)
    tmgrgp_is_delete = models.BooleanField(default=False)
    tg_task_created_by = models.ForeignKey(User, related_name="tgTaskCreateBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    tg_task_modified_by = models.ForeignKey(User, related_name="tgTaskModifiedBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    tmgrgp_created_at = models.DateTimeField(editable=False)
    tmgrgp_modified_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.taskgp_mgr_id:

            self.tmgrgp_created_at = timezone.now()
        self.tmgrgp_modified_at = timezone.now()
        return super(TaskGroupManager, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TaskGroupManager"

# Task Group Manager Model End#


# Task Manager Model End#

class TaskManager(models.Model):
    task_mgr_id = models.AutoField(primary_key=True)
    tmgr_task = models.ForeignKey(Task, related_name="taskManager", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgr_group = models.ForeignKey(TaskGroup, related_name="groupManager", on_delete=models.DO_NOTHING, blank=True, null=True)
    task_type = models.IntegerField(default=1)
    tmgr_ticket = models.ForeignKey(Ticket, related_name="ticketManager", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgr_display_order = models.CharField(max_length=50, null=True)
    task_note = models.TextField(null=True)
    task_due_date = models.DateField(null=True)
    task_dependency = models.BooleanField(default=False)
    task_depend_order = models.CharField(max_length=50, null=True)
    task_assigned_to = models.ForeignKey(User, related_name="taskAssign", on_delete=models.DO_NOTHING, blank=True, null=True)
    ttype_group_yes = models.ForeignKey(TaskGroup, related_name="ttypeYes", on_delete=models.DO_NOTHING, blank=True, null=True)
    ttype_copen_yes = models.BooleanField(default=False)
    ttype_cticket_yes = models.BooleanField(default=False)
    ttype_substatus_yes = models.ForeignKey(SubStatus, related_name="ttypeSubStatusYes", on_delete=models.DO_NOTHING, blank=True, null=True)
    ttype_group_no = models.ForeignKey(TaskGroup, related_name="ttypeNo", on_delete=models.DO_NOTHING, blank=True, null=True)
    ttype_copen_no = models.BooleanField(default=False)
    ttype_cticket_no = models.BooleanField(default=False)
    ttype_substatus_no = models.ForeignKey(SubStatus, related_name="ttypeSubStatusNo", on_delete=models.DO_NOTHING, blank=True, null=True)
    ttype_group_na = models.ForeignKey(TaskGroup, related_name="ttypeNA", on_delete=models.DO_NOTHING, blank=True, null=True)
    ttype_copen_na = models.BooleanField(default=False)
    ttype_cticket_na = models.BooleanField(default=False)
    ttype_substatus_na = models.ForeignKey(SubStatus, related_name="ttypeSubStatusNA", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgr_is_cancel = models.BooleanField(default=False)
    tmgr_is_complete = models.BooleanField(default=False)
    tmgr_completion_at = models.DateTimeField(editable=False, null=True)
    tmgr_completion_userId = models.ForeignKey(User, related_name="taskCompletionUserId", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgr_completion_userName = models.CharField(max_length=100, null=True)
    tmgr_laborhour_hours = models.CharField(max_length=50, null=True)
    tmgr_laborhour_minutes = models.CharField(max_length=50, null=True)
    tmgr_labor_note = models.TextField(null=True)
    tmgr_labor_ticketnote = models.ForeignKey(TicketNote, related_name="laborTicketNote", on_delete=models.DO_NOTHING, blank=True, null=True)
    tmgr_response_status = models.CharField(max_length=10, null=True, default=0)
    tmgr_is_active = models.BooleanField(default=True)
    tmgr_is_delete = models.BooleanField(default=False)
    task_created_by = models.ForeignKey(User, related_name="taskCreateBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    task_modified_by = models.ForeignKey(User, related_name="taskModifiedBy", on_delete=models.DO_NOTHING, blank=True,null=True)
    tmgr_created_at = models.DateTimeField(editable=False)
    tmgr_modified_at = models.DateTimeField()
    tmgr_org_id = models.IntegerField(blank=True, null=True)
    tmgr_user_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.tmgr_display_order

    def save(self, *args, **kwargs):
        if not self.task_mgr_id:
            self.tmgr_created_at = timezone.now()
        self.tmgr_modified_at = timezone.now()
        return super(TaskManager, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TaskManager"

# Task Manager Model End#


# Ticket Attachments Model End#

class TicketAttachments(models.Model):
    attach_id = models.AutoField(primary_key=True)
    attach_ticket = models.ForeignKey(Ticket, related_name="ticketAttach", on_delete=models.DO_NOTHING, blank=True, null=True)
    file_name = models.TextField(null=True)
    file_size = models.CharField(max_length=100, null=True)
    file_path = models.FileField(upload_to='attachments/')
    attach_created_by = models.ForeignKey(User, related_name="attachCreatedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    attach_modified_by = models.ForeignKey(User, related_name="attachModifiedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    attach_created_at = models.DateTimeField(editable=False)
    attach_modified_at = models.DateTimeField()
    attach_is_delete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.attach_id:
            self.attach_created_at = timezone.now()
        self.attach_modified_at = timezone.now()
        return super(TicketAttachments, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketAttachments"

# Ticket Attachments Model End#


# PanelGraph Model Start#

class PanelGraph(models.Model):
    panelGraph_id = models.AutoField(primary_key=True)
    panelGraph_text = models.CharField(max_length=255,null=False)
    panelGraph_url = models.CharField(max_length=255,null=False)
    panelGraph_created_at = models.DateTimeField(editable=False)
    panelGraph_modified_at = models.DateTimeField()

    def __str__(self):
        return self.panelGraph_text

    def save(self, *args, **kwargs):
        if not self.panelGraph_id:
            self.panelGraph_created_at = timezone.now()
        self.panelGraph_modified_at = timezone.now()
        return super(PanelGraph, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PanelGraph"
# PanelGraph Model End#


# Dashboard Settings Model End#

class DashboardSettings(models.Model):
    d_setting_id = models.AutoField(primary_key=True)
    d_user = models.ForeignKey(User, related_name="dashboardUser", on_delete=models.DO_NOTHING)
    d_panel = models.ForeignKey(PanelGraph, related_name="dashboardPanel", on_delete=models.DO_NOTHING)
    d_column_side = models.BooleanField(default=False)
    d_expanded = models.BooleanField(default=False)
    d_data_display = models.IntegerField(default=1)
    # d_parent_id = models.IntegerField(blank=True, null=True)
    d_created_at = models.DateTimeField(editable=False)
    d_modified_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.d_setting_id:
            self.d_created_at = timezone.now()
        self.d_modified_at = timezone.now()
        return super(DashboardSettings, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DashboardSettings"

# Dashboard Settings Model End#


# My Settings Model START#

class MySettings(models.Model):
    m_setting_id = models.AutoField(primary_key=True)
    m_user = models.ForeignKey(User, related_name="mSettingsUser", on_delete=models.DO_NOTHING)
    m_time_zone = models.CharField(max_length=100)
    m_default_page = models.CharField(max_length=255,null=False)
    m_ticket_screen = models.IntegerField()
    m_redirect_to = models.CharField(max_length=255,null=False)
    m_dashboard_reload = models.IntegerField(default=0)
    m_show_reload = models.BooleanField(default=False)
    m_phone = models.CharField(max_length=100,null=True)
    m_email = models.EmailField(max_length=100,null=True)
    m_mob_sms_email = models.CharField(max_length=100,null=True)
    m_address1 = models.TextField(null=True)
    m_address2 = models.TextField(null=True)
    m_user_city = models.CharField(max_length=100,null=True)
    m_user_state = models.CharField(max_length=100,null=True)
    m_user_zip_code = models.CharField(max_length=50,null=True)
    m_user_country = models.CharField(max_length=100,null=True)
    m_created_at = models.DateTimeField(editable=False)
    m_modified_at = models.DateTimeField()
    m_org_id = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.m_setting_id:
            self.m_created_at = timezone.now()
        self.m_modified_at = timezone.now()
        return super(MySettings, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_MySettings"

# My Settings Model End#


# Ticekt  Save Search End#

class TicketSavedSearch(models.Model):
    saved_search_id = models.AutoField(primary_key=True)
    ticket_status = models.IntegerField(default=0, blank=True, null=True)
    ticket_sub_status = models.ForeignKey(SubStatus, on_delete=models.DO_NOTHING, blank=True, null=True)
    priority = models.ForeignKey(Priority, on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_type = models.ForeignKey(TicketType, related_name="saveTicketType", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype1 = models.ForeignKey(TicketType, related_name="saveSubType1", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype2 = models.ForeignKey(TicketType, related_name="saveSubType2", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype3 = models.ForeignKey(TicketType, related_name="saveSubType3", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_subtype4 = models.ForeignKey(TicketType, related_name="saveSubType4", on_delete=models.DO_NOTHING, blank=True, null=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    ticket_note = models.CharField(max_length=100, null=True, blank=True)
    all_three = models.CharField(max_length=100, null=True, blank=True)
    ticket_record_locator = models.CharField(max_length=255, null=True, blank=True)
    ticket_caller_name = models.CharField(max_length=100, null=True, blank=True)
    ticket_caller_phone = models.CharField(max_length=50, null=True, blank=True)
    ticket_caller_email = models.EmailField(max_length=100, null=True, blank=True)
    ticket_passenger_name = models.CharField(max_length=100, null=True, blank=True)
    submitted_by = models.ForeignKey(User, related_name="saveSubmittedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    note_entered_by = models.ForeignKey(User, related_name="saveNoteEnteredBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    entered_by = models.ForeignKey(User, related_name="saveEnteredBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    assigned_by = models.ForeignKey(User, related_name="saveAssignBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    ticket_assigned_to = models.ForeignKey(User, related_name="saveTicketAssignTo", on_delete=models.DO_NOTHING, blank=True, null=True)
    ever_assigned = models.IntegerField(default=0, blank=True, null=True)
    next_action = models.ForeignKey(User, related_name="saveNextActionBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    ever_next_action = models.IntegerField(default=0, blank=True, null=True)
    closed_by = models.ForeignKey(User, related_name="saveClosedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    org = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True)
    # client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True)
    date_opened = models.TextField(null=True, blank=True)
    date_closed = models.TextField(null=True, blank=True)
    labour_hours_val = models.TextField(null=True, blank=True)
    labour_hours = models.TextField(null=True, blank=True)
    task_description = models.TextField(null=True, blank=True)
    task_assigned_to = models.ForeignKey(User, related_name="saveTaskAssignTo", on_delete=models.DO_NOTHING, blank=True, null=True)
    task_completion_date = models.TextField(null=True, blank=True)
    search_title = models.TextField(null=True, blank=True)
    output_view = models.TextField(null=True, blank=True)
    sort_column1 = models.CharField(max_length=100, null=True, blank=True)
    sort_order1 = models.IntegerField(default=0, blank=True, null=True)
    sort_column2 = models.CharField(max_length=100, null=True, blank=True)
    sort_order2 = models.IntegerField(default=0, blank=True, null=True)
    sort_column3 = models.CharField(max_length=100, null=True, blank=True)
    sort_order3 = models.IntegerField(default=0, blank=True, null=True)
    total_time_open_val = models.TextField(null=True, blank=True)
    total_time_open = models.TextField(null=True, blank=True)
    adj_time_open_val = models.TextField(null=True, blank=True)
    adj_time_open = models.TextField(null=True, blank=True)
    show_criteria = models.IntegerField(default=0, blank=True, null=True)
    is_share = models.BooleanField(default=False)
    save_created_at = models.DateTimeField(editable=False)
    save_modified_at = models.DateTimeField()
    save_created_by = models.ForeignKey(User, related_name="saveCreatedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    save_modified_by = models.ForeignKey(User, related_name="saveModifiedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    account_id = models.IntegerField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.saved_search_id:
            self.save_created_at = timezone.now()
        self.save_modified_at = timezone.now()
        return super(TicketSavedSearch, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketSavedSearches"

# Ticekt Save Search Model End# 


# Tickets Roles Model End#

class TicketsRoles(models.Model):
    t_role_id = models.AutoField(primary_key=True)
    t_role_slug = models.CharField(max_length=100,null=True,blank=True)
    t_name = models.CharField(max_length=100)
    t_is_deleted = models.BooleanField(default=False)
    t_is_default = models.BooleanField(default=False)
    t_created_by = models.ForeignKey(User, related_name="tcreatorUser", on_delete=models.DO_NOTHING, null=True, blank=True)
    t_modified_by = models.ForeignKey(User, related_name="tmodifierUser", on_delete=models.DO_NOTHING, null=True, blank=True)
    t_created_at = models.DateTimeField(editable=False)
    t_modified_at = models.DateTimeField()

    def __str__(self):
        return self.t_name

    def save(self, *args, **kwargs):
        if not self.t_role_id:
            self.t_created_at = timezone.now()
        self.t_modified_at = timezone.now()
        return super(TicketsRoles, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketsRoles"

# Tickets Roles Model End#



# Tickets Actions Model End#

class TicketsActions(models.Model):
    t_action_id = models.AutoField(primary_key=True)
    t_action_slug = models.CharField(max_length=100,null=True,blank=True)
    t_action_name = models.CharField(max_length=100)
    t_action_is_deleted = models.BooleanField(default=False)
    t_action_created_by = models.ForeignKey(User, related_name="tActionCreatorUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    t_action_modified_by = models.ForeignKey(User, related_name="tActionModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    t_action_created_at = models.DateTimeField(editable=False)
    t_action_modified_at = models.DateTimeField()

    def __str__(self):
        return self.t_action_name

    def save(self, *args, **kwargs):
        if not self.t_action_id:
            self.t_action_created_at = timezone.now()
        self.t_action_modified_at = timezone.now()
        return super(TicketsActions, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketsActions"

# Tickets Actions Model End#


# Tickets Email Notification Permissions Model End#

class TicketsEmailNotificationPermissions(models.Model):
    t_email_permit_id = models.AutoField(primary_key=True)
    t_email_role = models.ForeignKey(TicketsRoles, related_name="tRoleEmail", on_delete=models.DO_NOTHING)
    t_email_action = models.ForeignKey(TicketsActions, related_name="tActionEmail", on_delete=models.DO_NOTHING)
    t_email_is_deleted = models.BooleanField(default=False)
    t_email_created_by = models.ForeignKey(User, related_name="tEmailCreatorUser", on_delete=models.DO_NOTHING)
    t_email_modified_by = models.ForeignKey(User, related_name="tEmailModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    t_email_created_at = models.DateTimeField(editable=False)
    t_email_modified_at = models.DateTimeField()
    t_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.t_email_role.t_name + self.t_email_action.t_action_name

    def save(self, *args, **kwargs):
        if not self.t_email_permit_id:
            self.t_email_created_at = timezone.now()
        self.t_email_modified_at = timezone.now()
        return super(TicketsEmailNotificationPermissions, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketsEmailNotificationPermissions"

# Tickets Email Notification Permissions Model End#


# Report Setting Data Type Start#

class ReportSettingDataType(models.Model):
    rpt_data_type_id = models.AutoField(primary_key=True)
    rpt_data_type_name = models.CharField(max_length=100)
    data_type_is_delete = models.BooleanField(default=False)
    data_type_created_at = models.DateTimeField(editable=False)
    data_type_modified_at = models.DateTimeField()

    def __str__(self):
        return self.rpt_data_type_name

    def save(self, *args, **kwargs):
        if not self.rpt_data_type_id:
            self.data_type_created_at = timezone.now()
        self.data_type_modified_at = timezone.now()
        return super(ReportSettingDataType, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ReportSettingDataTypes"

# Report Setting Data Type End#


# Data Sets For Query Builder Model End#

class DataSetsPair(models.Model):
    ds_pair_id = models.AutoField(primary_key=True)
    ds_pair_name = models.CharField(max_length=100)
    ds_is_deleted = models.BooleanField(default=False)
    ds_created_at = models.DateTimeField(editable=False)
    ds_modified_at = models.DateTimeField()

    def __str__(self):
        return self.ds_pair_name

    def save(self, *args, **kwargs):
        if not self.ds_report_writer_id:
            self.ds_created_at = timezone.now()
        self.ds_modified_at = timezone.now()
        return super(DataSetsPair, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DataSetsPair"

# Data Sets For Query Builder Model End#


# Data Sets For Query Builder Model End#

class DataSetsPairFields(models.Model):
    d_field_id = models.AutoField(primary_key=True)
    df_name = models.CharField(max_length=100)
    df_actual_column_name = models.CharField(max_length=100)
    df_actual_table_name = models.CharField(max_length=100)
    df_primary_table_name = models.CharField(max_length=100, null=True)
    df_pair = models.ForeignKey(DataSetsPair, related_name="dsfieldPair", on_delete=models.DO_NOTHING, null=True,blank=True)
    df_condition_type = models.CharField(max_length=100)
    df_rpt_data_type = models.ForeignKey(ReportSettingDataType, related_name="dfReportDataType", on_delete=models.DO_NOTHING,null=True,blank=True)
    df_order = models.IntegerField(null=True)
    df_is_deleted = models.BooleanField(default=False)
    df_created_at = models.DateTimeField(editable=False)
    df_modified_at = models.DateTimeField()

    def __str__(self):
        return self.df_name

    def save(self, *args, **kwargs):
        if not self.d_field_id:
            self.df_created_at = timezone.now()
        self.df_modified_at = timezone.now()
        return super(DataSetsPairFields, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DataSetsPairFields"

# Data Sets For Query Builder Model End#


# Data Sets For Query Builder Model End#

class DataSetsFieldsConditions(models.Model):
    d_condition_id = models.AutoField(primary_key=True)
    dc_name = models.CharField(max_length=100)
    dc_type = models.CharField(max_length=100)
    dc_express = models.CharField(max_length=100, default='iexact')
    dc_type_name = models.CharField(max_length=100)
    dc_is_deleted = models.BooleanField(default=False)
    dc_created_at = models.DateTimeField(editable=False)
    dc_modified_at = models.DateTimeField()

    def __str__(self):
        return self.dc_name

    def save(self, *args, **kwargs):
        if not self.d_condition_id:
            self.dc_created_at = timezone.now()
        self.dc_modified_at = timezone.now()
        return super(DataSetsFieldsConditions, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DataSetsFieldsConditions"

# Data Sets For Query Builder Model End#


#Query Builder Saved Queries Start#

class SavedQBQuries(models.Model):
    qb_query_id = models.AutoField(primary_key=True)
    qb_query_name = models.CharField(max_length=100)
    qb_query_description = models.TextField(null=True)
    qb_query_pair = models.ForeignKey(DataSetsPair, related_name="qbDataSetsPair", on_delete=models.DO_NOTHING, null=True, blank=True)
    qb_filter_expressions = models.TextField(null=True)
    qb_filter_expression_array = models.TextField(null=True)
    qb_expression_content_array = models.TextField(null=True)
    qb_filter_statement = models.TextField(null=True)
    qb_selected_fields = models.TextField(null=True)
    qb_unselected_fields = models.TextField(null=True)
    qb_query_create_report = models.BooleanField(default=False)
    qb_query_is_share = models.BooleanField(default=False)
    qb_query_is_delete = models.BooleanField(default=False)
    qb_created_by = models.ForeignKey(User, related_name="qbCreatorUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    qb_modified_by = models.ForeignKey(User, related_name="qbModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    qb_created_at = models.DateTimeField(editable=False)
    qb_modified_at = models.DateTimeField()

    def __str__(self):
        return self.qb_query_name

    def save(self, *args, **kwargs):
        if not self.qb_query_id:
            self.qb_created_at = timezone.now()
        self.qb_modified_at = timezone.now()
        return super(SavedQBQuries, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SavedQBQuries"

# Query Builder Saved Queries End#


# Query Builder Saved Queries Start#
class SavedQBQuriesShareWith(models.Model):
    qb_share_with_id = models.AutoField(primary_key=True)
    qb_query = models.ForeignKey(SavedQBQuries, related_name="qbQueryID", on_delete=models.DO_NOTHING, null=True, blank=True)
    qb_query_share_with = models.ForeignKey(User, related_name="qbShareWith", on_delete=models.DO_NOTHING, null=True, blank=True)
    qb_created_at = models.DateTimeField(editable=False)
    qb_modified_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.qb_share_with_id:
            self.qb_created_at = timezone.now()
        self.qb_modified_at = timezone.now()
        return super(SavedQBQuriesShareWith, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SavedQBQuriesShareWith"

# Query Builder Saved Queries End#


# Report Setting Data Type Format Start#

class ReportSettingFormat(models.Model):
    rpt_format_id = models.AutoField(primary_key=True)
    rpt_format_name = models.CharField(max_length=100)
    rpt_format_value = models.CharField(max_length=100, null=True, blank=True)
    format_data_type = models.ForeignKey(ReportSettingDataType, related_name="formatDataType", on_delete=models.DO_NOTHING,null=True,blank=True)
    format_is_delete = models.BooleanField(default=False)
    format_created_at = models.DateTimeField(editable=False)
    format_modified_at = models.DateTimeField()

    def __str__(self):
        return self.rpt_format_name

    def save(self, *args, **kwargs):
        if not self.rpt_format_id:
            self.format_created_at = timezone.now()
        self.format_modified_at = timezone.now()
        return super(ReportSettingFormat, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ReportSettingFormats"

# Report Setting Data Type End#


# Report Setting Data Type Format Start#

class ReportSettingJustification(models.Model):
    rpt_justify_id = models.AutoField(primary_key=True)
    rpt_justify_name = models.CharField(max_length=100)
    justify_is_delete = models.BooleanField(default=False)
    justify_created_at = models.DateTimeField(editable=False)
    justify_modified_at = models.DateTimeField()

    def __str__(self):
        return self.rpt_justify_name

    def save(self, *args, **kwargs):
        if not self.rpt_justify_id:
            self.justify_created_at = timezone.now()
        self.justify_modified_at = timezone.now()
        return super(ReportSettingJustification, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ReportSettingJustifications"

# Report Setting Data Type End#


# Save Report Settings Start#

class SaveReportSetting(models.Model):
    rpt_setting_id = models.AutoField(primary_key=True)
    rpt_setting_dataType = models.ForeignKey(ReportSettingDataType, related_name="rptSettingDataType", on_delete=models.DO_NOTHING,null=True,blank=True)
    rpt_setting_width = models.IntegerField(default=0, null=True)
    max_records_return = models.IntegerField(default=0, null=True)
    max_records_print = models.IntegerField(default=0, null=True)
    max_records_display = models.IntegerField(default=0, null=True)
    rpt_setting_is_delete = models.BooleanField(default=False)
    rpt_setting_format = models.ForeignKey(ReportSettingFormat, related_name="rptSettingFormat", on_delete=models.DO_NOTHING,null=True,blank=True)
    rpt_setting_justification = models.ForeignKey(ReportSettingJustification, related_name="rptSettinJustification", on_delete=models.DO_NOTHING,null=True,blank=True)
    rpt_setting_created_at = models.DateTimeField(editable=False)
    rpt_setting_created_by = models.ForeignKey(User, related_name="rptSettingCreatedBy", on_delete=models.DO_NOTHING,null=True,blank=True)
    rpt_org_id = models.IntegerField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.rpt_setting_id:
            self.rpt_setting_created_at = timezone.now()
        return super(SaveReportSetting, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SaveReportSetting"

# Save Report Settings End#


# User Sent Email Start#

class UserSentEmails(models.Model):
    use_id = models.AutoField(primary_key=True)
    use_subject = models.CharField(max_length=100, blank=True, null=True)
    use_message = models.CharField(max_length=100, blank=True, null=True)
    use_sent_to = models.ForeignKey(User, related_name="useSentTo", on_delete=models.DO_NOTHING,null=True,blank=True)
    use_created_at = models.DateTimeField(editable=False)
    use_created_by = models.ForeignKey(User, related_name="useCreatedBy", on_delete=models.DO_NOTHING,null=True,blank=True)
    use_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.use_message

    def save(self, *args, **kwargs):
        if not self.use_id:
            self.use_created_at = timezone.now()
        return super(UserSentEmails, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserSentEmails"

# User Sent Email End#


#Report Builder Saved Queries Start#

class SavedRBReports(models.Model):
    rb_report_id = models.AutoField(primary_key=True)
    rb_report_name = models.CharField(max_length=100)
    rb_report_title = models.CharField(max_length=200, null=True)
    rb_report_description = models.TextField(null=True)
    rb_report_query = models.ForeignKey(SavedQBQuries, related_name="rbQuerySetsQuery", on_delete=models.DO_NOTHING, null=True, blank=True)
    rb_selected_query_fields_array = models.TextField(null=True)
    rb_unselected_query_fields_array = models.TextField(null=True)
    rb_selected_group_fields_array = models.TextField(null=True)
    rb_unselected_group_fields_array = models.TextField(null=True)
    rb_selected_order_fields_array = models.TextField(null=True)
    rb_selected_group_sorting = models.TextField(null=True)
    rb_selected_sort_expressions = models.TextField(null=True)
    rb_selected_fields_formating = models.TextField(null=True)
    rb_selected_format_fields_array = models.TextField(null=True)
    rb_report_create_report = models.BooleanField(default=False)
    rb_report_is_share = models.BooleanField(default=False)
    rb_report_is_delete = models.BooleanField(default=False)
    rb_created_by = models.ForeignKey(User, related_name="rbCreatorUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    rb_modified_by = models.ForeignKey(User, related_name="rbModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    rb_created_at = models.DateTimeField(editable=False)
    rb_modified_at = models.DateTimeField()

    def __str__(self):
        return self.rb_report_name

    def save(self, *args, **kwargs):
        if not self.rb_report_id:
            self.rb_created_at = timezone.now()
        self.rb_modified_at = timezone.now()
        return super(SavedRBReports, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SavedRBReports"

# Report Builder Saved Queries End#


class SavedRBReportsShareWith(models.Model):
    rb_share_with_id = models.AutoField(primary_key=True)
    rb_report = models.ForeignKey(SavedRBReports, related_name="rbReportID", on_delete=models.DO_NOTHING, null=True, blank=True)
    rb_report_share_with = models.ForeignKey(User, related_name="rbShareWith", on_delete=models.DO_NOTHING, null=True, blank=True)
    rb_created_at = models.DateTimeField(editable=False)
    rb_modified_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.rb_share_with_id:
            self.rb_created_at = timezone.now()
        self.rb_modified_at = timezone.now()
        return super(SavedRBReportsShareWith, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SavedRBReportsShareWith"

# Query Builder Saved Queries End#

# Scheduled Report Model Start#
class ScheduledReport(models.Model):
    sch_rpt_id = models.AutoField(primary_key=True)
    sch_rpt_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    rep_type = models.IntegerField(default=0, null=True)
    rep_name = models.CharField(max_length=100)
    out_type = models.IntegerField(default=0, null=True)
    schedule = models.IntegerField(default=0, null=True)
    end_sch_rpt_date = models.DateTimeField(null=True)
    notify_error = models.ForeignKey(User, related_name="schRptNotifyUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    comment = models.TextField()
    sch_rpt_is_delete = models.BooleanField(default=False)
    sch_rpt_created_by = models.ForeignKey(User, related_name="schRptCreatorUser", on_delete=models.DO_NOTHING)
    sch_rpt_modified_by = models.ForeignKey(User, related_name="schRptModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    sch_rpt_created_at = models.DateTimeField(editable=False)
    sch_rpt_modified_at = models.DateTimeField()
    sch_rpt_org_id = models.IntegerField(blank=True, null=True)
    sch_rpt_report_writer = models.ForeignKey('Savedrbreports', models.DO_NOTHING, blank=True, null=True)
    sch_rpt_saved_search = models.ForeignKey('Ticketsavedsearch', models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.sch_rpt_name

    def save(self, *args, **kwargs):
        if not self.sch_rpt_id:
            self.sch_rpt_created_at = timezone.now()
        self.sch_rpt_modified_at = timezone.now()
        return super(ScheduledReport, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ScheduledReports"


# Scheduled Report Model End#


# Orginaztion Contract Model Start#
class OrginaztionContract(models.Model):
    org_contract_id = models.AutoField(primary_key=True)
    org_contract_name = models.CharField(max_length=100)
    org_contract_begin_date = models.DateTimeField()
    org_contract_end_date = models.DateTimeField()
    oc_org = models.ForeignKey(Organization, related_name="orgContractOrganiztion", on_delete=models.DO_NOTHING)
    org_contract_hours_purchased = models.IntegerField(default=0, null=True)
    org_contract_is_batch = models.BooleanField(default=False)
    org_contract_is_delete = models.BooleanField(default=False)
    org_contract_created_by = models.ForeignKey(User, related_name="orgContractCreatedUser", on_delete=models.DO_NOTHING)
    org_contract_modified_by = models.ForeignKey(User, related_name="orgContractModifiedUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    org_contract_created_at = models.DateTimeField(editable=False)
    org_contract_modified_at = models.DateTimeField()

    def __str__(self):
        return self.org_contract_name

    def save(self, *args, **kwargs):
        if not self.org_contract_id:
            self.org_contract_created_at = timezone.now()
        self.org_contract_modified_at = timezone.now()
        return super(OrginaztionContract, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_OrginaztionContracts"
# Orginaztion Contract Model End#


# Schedule Report Recipient Start#
class ScheduleReportResp(models.Model):
    sr_resp_id = models.AutoField(primary_key=True)
    sch_rep_id = models.ForeignKey(ScheduledReport, related_name="schRpt", on_delete=models.DO_NOTHING,null=True,blank=True)
    sr_resp_recipt_user = models.ForeignKey(User, related_name="schRptRespUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    sr_resp_created_at = models.DateTimeField(editable=False)
    sr_resp_modified_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.sr_resp_id:
            self.sr_resp_created_at = timezone.now()
        self.sr_resp_modified_at = timezone.now()
        return super(ScheduleReportResp, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ScheduleReportResp"


#Schedule Report Recipient


#Schedule Report Span Start#
class ScheduleReportSpan(models.Model):
    sch_rep_span_id = models.AutoField(primary_key=True)
    sch_rep_span_name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        return super(ScheduleReportSpan, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ScheduleReportSpan"

#Schedule Report Span end#


#SChedule Report Entery with Filters i.e weekly,monthly
class ScheduleReportSchedulebyFilters(models.Model):
    sch_rep_sch_filter_id = models.AutoField(primary_key=True)
    sch_rep_id = models.ForeignKey(ScheduledReport, related_name="SchRpt", on_delete=models.DO_NOTHING,null=True,blank=True)
    sch_rep_span_id = models.ForeignKey(ScheduleReportSpan, related_name="schRptspan", on_delete=models.DO_NOTHING,null=True,blank=True)
    week_days=models.TextField(null=True)
    is_MonthDay_Specific = models.IntegerField(null=True)
    days= models.CharField(max_length=100)
    everyMonth = models.IntegerField(null=True)
    the_first= models.IntegerField(null=True)
    single_WeakDay = models.IntegerField( null=True)
    quartely_Beginning_Date = models.DateTimeField(null=True)
    biannually_start_date = models.DateTimeField(null=True)
    biannually_end_date = models.DateTimeField(null=True)
    annually_date = models.DateTimeField(null=True)
    onetime_date = models.DateTimeField(null=True)
    sch_rep_sch_filter_created_at = models.DateTimeField(editable=False)
    sch_rep_sch_filter_modified_at = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.sch_rep_sch_filter_id:
            self.sch_rep_sch_filter_created_at = timezone.now()
        self.sch_rep_sch_filter_modified_at = timezone.now()
        return super(ScheduleReportSchedulebyFilters, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ScheduleReportSchedulebyFilter"

#SChedule Report Entery with Filters i.e weekly,monthly


# HoursOfOperation Model Start#
class HoursOfOperation(models.Model):
    sys_id = models.AutoField(primary_key=True)
    open_tickets_only = models.CharField(max_length=100, default='Open')
    # open_and_closed_tickets = models.CharField(max_length=100)
    work_day = models.CharField(max_length=100, default='ON')
    start_hour = models.CharField(max_length=50, default="12")
    start_minutes = models.CharField(max_length=50, default="00")
    start_AM_PM = models.CharField(max_length=50, default="AM")
    end_hour = models.CharField(max_length=50, default="11")
    end_minutes = models.CharField(max_length=50, default="30")
    end_AM_PM = models.CharField(max_length=50, default="PM")
    monday = models.CharField(max_length=50, null=True)
    tuesday = models.CharField(max_length=50, null=True)
    wednesday = models.CharField(max_length=50, null=True)
    thursday = models.CharField(max_length=50, null=True)
    friday = models.CharField(max_length=50, null=True)
    saturday = models.CharField(max_length=50, null=True)
    sunday = models.CharField(max_length=50, null=True)
    sys_is_active = models.BooleanField(default=True)
    sys_is_delete = models.BooleanField(default=False)
    sys_created_at = models.DateTimeField(auto_now_add=True)
    sys_modified_at = models.DateTimeField(auto_now=True)
    operation_org_id = models.IntegerField(blank=True, null=True)
    operation_user_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.work_day

    def save(self, *args, **kwargs):
        if not self.sys_id:
            self.sys_created_at = timezone.now()
        self.sys_modified_at = timezone.now()
        return super(HoursOfOperation, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_HoursOfOperation"

# HoursOfOperation Model End#


# Dates Closed Model Start#
class DatesClosed(models.Model):
    date_id = models.AutoField(primary_key=True)
    date_closed = models.CharField(max_length=100)
    comment = models.CharField(max_length=100)
    date_is_active = models.BooleanField(default=True)
    date_is_delete = models.BooleanField(default=False)
    date_created_at = models.DateTimeField(auto_now_add=True)
    date_modified_at = models.DateTimeField(auto_now=True)
    date_org_id = models.IntegerField(blank=True, null=True)
    date_user_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.date_closed

    def save(self, *args, **kwargs):
        if not self.date_id:
            self.date_created_at = timezone.now()
        self.date_modified_at = timezone.now()
        return super(DatesClosed, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DatesClosed"

# Dates Closed Model End#


# Site Appearance Model Start#
class SiteAppearance(models.Model):
    site_id = models.AutoField(primary_key=True)
    site_title = models.CharField(max_length=255)
    home_screen = models.TextField(null=True)
    home_agent = models.TextField(null=True)
    login_screen = models.TextField(null=True)
    upload_favicon = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    upload_left_logo = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    left_logo_url = models.CharField(max_length=255, null=True)
    upload_right_logo = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    right_logo_url = models.CharField(max_length=255, null=True)
    site_is_active = models.BooleanField(default=True)
    site_is_delete = models.BooleanField(default=False)
    site_created_at = models.DateTimeField(auto_now_add=True)
    site_modified_at = models.DateTimeField(auto_now=True)
    site_org_id = models.IntegerField(blank=True, null=True)
    site_user_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        if not self.site_id:
            self.site_created_at = timezone.now()
        self.site_modified_at = timezone.now()
        return super(SiteAppearance, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SiteAppearance"

# Site Appearance Model End#


# Email Settings Model Start#
class EmailSettings(models.Model):
    email_id = models.AutoField(primary_key=True)
    email_server = models.CharField(max_length=255)
    tls_encription = models.CharField(max_length=50)
    port = models.CharField(max_length=50)
    user_auth = models.CharField(max_length=50)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    email_sender_address = models.CharField(max_length=255)
    email_sender_name = models.CharField(max_length=255)
    outgoing_email = models.CharField(max_length=50)
    return_email_address = models.CharField(max_length=255)
    reply_separation_text = models.CharField(max_length=255)
    use_html_format = models.CharField(max_length=50)
    email_to_initiator = models.CharField(max_length=50)
    email_on_substatus_change = models.CharField(max_length=50)
    suppression_of_email_notifications = models.CharField(max_length=50)
    allow_for_agents = models.CharField(max_length=50)
    sorting_order = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    email_org_id = models.IntegerField(blank=True, null=True)
    email_user_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.email_server

    def save(self, *args, **kwargs):
        if not self.email_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(EmailSettings, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_EmailSettings"

# Email Settings Model End#


# Emails Model Start#
class Emails(models.Model):
    email_id = models.AutoField(primary_key=True)
    send_date = models.DateTimeField(auto_now_add=True)
    to_user_id = models.CharField(max_length=255)
    to_email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField(default="Email Body")
    mailed_date = models.DateTimeField(auto_now_add=True)
    rc = models.CharField(max_length=50)
    ticket = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    org_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        if not self.email_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(Emails, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Emails"

# Emails Model End#


# # PermissionSection Model Start#

class PermissionSection(models.Model):
    perm_sect_id = models.AutoField(primary_key=True)
    permission = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.permission

    def save(self, *args, **kwargs):
        if not self.perm_sect_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(PermissionSection, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PermissionSections"

# PermissionSection Model End#


# PermissionAction Model Start#

class PermissionAction(models.Model):
    perm_act_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    
    # perm_sect_id = models.IntegerField(null=True)
    perm_act_slug = models.CharField(max_length=255,blank=True,default='')    
    perm_sect = models.ForeignKey(PermissionSection, on_delete=models.DO_NOTHING, related_name='permission_action', blank=True, null=True) 
    permit_agent = models.BooleanField(default=False)
    permit_end_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if not self.perm_act_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(PermissionAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PermissionActions"

# PermissionAction Model End#


# PermissionSubAction Model Start#

class PermissionSubAction(models.Model):
    sub_act_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    perm_sub_act_slug = models.CharField(max_length=255,blank=True,default='')  
    perm_act = models.ForeignKey(PermissionAction, on_delete=models.DO_NOTHING, related_name='permission_sub_action', blank=True, null=True)
    permit_agent = models.BooleanField(default=False)
    permit_end_user = models.BooleanField(default=False)    
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        if not self.sub_act_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(PermissionSubAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PermissionSubActions"

# PermissionSubAction Model End#


# UserActionPermission Model Start#

class UserActionPermission(models.Model):
    user_act_per_id = models.AutoField(primary_key=True)   
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    perm_act = models.ForeignKey(PermissionAction, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user_act_per_id

    def save(self, *args, **kwargs):
        if not self.user_act_per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(UserActionPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserActionPermissions"

# UserActionPermission Model End#


#Business Rules Start#
class BusinessRules(models.Model):
    br_id = models.AutoField(primary_key=True)
    br_org_name: models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=True, null=True) = models.CharField(max_length=100)
    br_dep_name = models.CharField(max_length=100, default="Null")
    br_client_name = models.CharField(max_length=100)
    br_ticket_type = models.ForeignKey(TicketType, related_name="br_ticketType", on_delete=models.DO_NOTHING, blank=True,null=True)
    br_ticket_subtype1 = models.ForeignKey(TicketType, related_name="br_ticketSubType1", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_ticket_subtype2 = models.ForeignKey(TicketType, related_name="br_ticketSubType2", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_ticket_subtype3 = models.ForeignKey(TicketType, related_name="br_ticketSubType3", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_ticket_subtype4 = models.ForeignKey(TicketType, related_name="br_ticketSubType4", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_org = models.ForeignKey(Organization, related_name="br_Organization", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_dep = models.ForeignKey(Department, related_name="br_Department", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_client = models.ForeignKey(Client, related_name="br_Client", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_priority = models.ForeignKey(Priority, related_name="br_Priority", on_delete=models.DO_NOTHING,blank=True, null=True)
    br_priority_name = models.CharField(max_length=100, null=True)
    start_hour = models.CharField(max_length=50, default="00")
    start_minutes = models.CharField(max_length=50, default="00")
    start_AM_PM = models.CharField(max_length=50, default="AM")
    end_hour = models.CharField(max_length=50, default="00")
    end_minutes = models.CharField(max_length=50, default="00")
    end_AM_PM = models.CharField(max_length=50, default="PM")
    monday = models.CharField(max_length=50, null=True)
    tuesday = models.CharField(max_length=50, null=True)
    wednesday = models.CharField(max_length=50, null=True)
    thursday = models.CharField(max_length=50, null=True)
    friday = models.CharField(max_length=50, null=True)
    saturday = models.CharField(max_length=50, null=True)
    sunday = models.CharField(max_length=50, null=True)
    start_24_hours = models.CharField(max_length=50, default="00:00")
    end_24_hours = models.CharField(max_length=50, default="00:00")
    br_ticket_assign_to = models.ForeignKey(User, related_name="br_ticketAssignTo", on_delete=models.DO_NOTHING, blank=True, null=True)
    br_ticket_assign_to_name = models.CharField(max_length=100, default="Null")
    br_is_active = models.BooleanField(default=True)
    br_is_delete = models.BooleanField(default=False)
    br_created_at = models.DateTimeField(auto_now_add=True,null=True)
    br_modified_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.br_id)

    def save(self, *args, **kwargs):
        if not self.br_id:
            self.br_created_at = timezone.now()
        self.br_modified_at = timezone.now()
        return super(BusinessRules, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_BusinessRules"

# Business Rules End#


#Business Rules Precedence Start#
class PrecedenceBusinessRule(models.Model):
    pbr_id = models.AutoField(primary_key=True)
    pbr_class= models.IntegerField(default="9")
    pbr_dep= models.IntegerField(default="1")
    pbr_client= models.IntegerField(default="2")
    pbr_tickettype= models.IntegerField(default="3")
    pbr_org= models.IntegerField(default="4")
    pbr_priority= models.IntegerField(default="5")
    pbr_submit_betw= models.IntegerField(default="7")
    pbr_submit_on= models.IntegerField(default="8")
    pbr_is_active = models.BooleanField(default=True)
    pbr_is_delete = models.BooleanField(default=False)
    pbr_created_at = models.DateTimeField(auto_now_add=True, null=True)
    pbr_modified_at = models.DateTimeField(auto_now_add=True, null=True)
    user_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.pbr_id)

    def save(self, *args, **kwargs):
        if not self.pbr_id:
            self.pbr_created_at = timezone.now()
        self.pbr_modified_at = timezone.now()
        return super(PrecedenceBusinessRule, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PrecedenceBusinessRules"


#Business Rules Precedence End#


# UserSubActionPermissions Model Start#

class UserSubActionPermission(models.Model):
    user_sub_act_per_id = models.AutoField(primary_key=True)   
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    sub_act = models.ForeignKey(PermissionSubAction, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)   

    def save(self, *args, **kwargs):
        if not self.user_sub_act_per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(UserSubActionPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserSubActionPermissions"

# UserSubActionPermissions Model End#


# ClientEmailNotificationPermission Model Start#
class ClientEmailNotificationPermission(models.Model):
    notif_per_id = models.AutoField(primary_key=True)   
    client = models.ForeignKey(Client,related_name='client_email_notification_children', on_delete=models.DO_NOTHING, blank=True, null=True)        
    t_action = models.ForeignKey(TicketsActions, on_delete=models.DO_NOTHING, blank=True, null=True)        
    email = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return str(self.notif_per_id)

    def save(self, *args, **kwargs):
        if not self.notif_per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(ClientEmailNotificationPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ClientEmailNotificationPermissions"

# ClientEmailNotificationPermission Model End#


# GroupActionPermission Model Start#

class GroupActionPermission(models.Model):
    group_act_per_id = models.AutoField(primary_key=True)   
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, blank=True, null=True)
    perm_act = models.ForeignKey(PermissionAction, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group_act_per_id

    def save(self, *args, **kwargs):
        if not self.group_act_per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(GroupActionPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_GroupActionPermissions"

# GroupActionPermission Model End#


# GroupSubActionPermission Model Start#

class GroupSubActionPermission(models.Model):
    group_sub_act_per_id = models.AutoField(primary_key=True)   
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, blank=True, null=True)
    sub_act = models.ForeignKey(PermissionAction, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)   

    def save(self, *args, **kwargs):
        if not self.group_sub_act_per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(GroupSubActionPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_GroupSubActionPermissions"

# GroupSubActionPermission Model End#


#Ticket Event Start#
class TicketEvent(models.Model):
    te_id = models.AutoField(primary_key=True)
    te_name = models.CharField(max_length=100, null=True)
    te_is_active = models.BooleanField(default=True)
    te_is_delete = models.BooleanField(default=False)
    te_created_at = models.DateTimeField(auto_now_add=True, null=True)
    te_modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.te_name

    def save(self, *args, **kwargs):
        if not self.te_id:
            self.te_created_at = timezone.now()
        self.te_modified_at = timezone.now()
        return super(TicketEvent, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TicketEvents"

#Ticket Event End#


#SubstatusBusinessRule Start#
class SubstatusBusinessRule(models.Model):
    sbr_id = models.AutoField(primary_key=True)
    sbr_ticketevent = models.ForeignKey(TicketEvent, related_name="sbr_ticketevent", on_delete=models.DO_NOTHING, blank=True,null=True)
    sbr_when_substatus_equal = models.ForeignKey(SubStatus, related_name="sbr_when_substatus_equal", on_delete=models.DO_NOTHING, blank=True,null=True)
    sbr_when_substatus_to = models.ForeignKey(SubStatus, related_name="sbr_substatus_to", on_delete=models.DO_NOTHING, blank=True,null=True)
    sbr_ticketevent_name = models.CharField(max_length=100, null=True)
    sbr_when_substatus_equal_name = models.CharField(max_length=100, null=True)
    sbr_when_substatus_to_name = models.CharField(max_length=100, null=True)
    sbr_process_order= models.IntegerField(default="1")
    sbr_is_active = models.BooleanField(default=True)
    sbr_is_delete = models.BooleanField(default=False)
    sbr_created_at = models.DateTimeField(auto_now_add=True, null=True)
    sbr_modified_at = models.DateTimeField(auto_now_add=True, null=True)
    sbr_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.sbr_id

    def save(self, *args, **kwargs):
        if not self.sbr_id:
            self.sbr_created_at = timezone.now()
        self.sbr_modified_at = timezone.now()
        return super(SubstatusBusinessRule, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_SubstatusBusinessRules"

#SubstatusBusinessRule End#


#Pause Clock Business Rules Start#
class PauseClockBusinessRule(models.Model):
    pcbr_id = models.AutoField(primary_key=True)
    pcbr_substatus_equal = models.ForeignKey(SubStatus, related_name="pcbr_substatus_equal", on_delete=models.DO_NOTHING, blank=True,null=True)
    pcbr_substatus_equal_name = models.CharField(max_length=100, null=True)
    pcbr_is_active = models.BooleanField(default=True)
    pcbr_is_delete = models.BooleanField(default=False)
    pcbr_created_at = models.DateTimeField(auto_now_add=True, null=True)
    pcbr_modified_at = models.DateTimeField(auto_now_add=True, null=True)
    pcbr_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.pcbr_id

    def save(self, *args, **kwargs):
        if not self.pcbr_id:
            self.pcbr_created_at = timezone.now()
        self.pcbr_modified_at = timezone.now()
        return super(PauseClockBusinessRule, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PauseClockBusinessRules"

#Pause Clock Business Rules End#



#Task Group Restrict To Start#
class TaskGroupRestrict(models.Model):
    tgr_id = models.AutoField(primary_key=True)
    tgr_task_group = models.ForeignKey(TaskGroup, related_name="tgr_task_group", on_delete=models.DO_NOTHING, blank=True,null=True)
    tgr_group = models.ForeignKey(Group, related_name="tgr_group", on_delete=models.DO_NOTHING, blank=True,null=True)
    tgr_org = models.ForeignKey(Organization, related_name='tgr_org', on_delete=models.DO_NOTHING, blank=True,null=True)
    tgr_type_is_group = models.BooleanField(default=False)
    tgr_type_is_org = models.BooleanField(default=False)
    tgr_group_or_org_name = models.CharField(max_length=100, null=True)
    #tgr_org_name = models.CharField(max_length=100, null=True)
    tgr_is_active = models.BooleanField(default=True)
    tgr_is_delete = models.BooleanField(default=False)
    tgr_created_at = models.DateTimeField(auto_now_add=True, null=True)
    tgr_modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.tgr_id

    def save(self, *args, **kwargs):
        if not self.tgr_id:
            self.tgr_created_at = timezone.now()
        self.tgr_modified_at = timezone.now()
        return super(TaskGroupRestrict, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TaskGroupRestricts"

#Task Group Restrict To End#



# Tasks Actions Model End#

class TasksAction(models.Model):
    task_action_id = models.AutoField(primary_key=True)
    task_action_slug = models.CharField(max_length=100)
    task_action_name = models.CharField(max_length=100)
    task_action_is_deleted = models.BooleanField(default=False)
    task_action_created_by = models.ForeignKey(User, related_name="taskActionCreatorUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    task_action_modified_by = models.ForeignKey(User, related_name="taskActionModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    task_action_created_at = models.DateTimeField(editable=False)
    task_action_modified_at = models.DateTimeField()

    def __str__(self):
        return self.task_action_name

    def save(self, *args, **kwargs):
        if not self.task_action_id:
            self.task_action_created_at = timezone.now()
        self.task_action_modified_at = timezone.now()
        return super(TasksAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TasksActions"

# Tasks Actions Model End#


# Tasks Roles Model End#

class TasksRole(models.Model):
    task_role_id = models.AutoField(primary_key=True)
    task_role_slug = models.CharField(max_length=100)
    task_name = models.CharField(max_length=100)
    task_is_deleted = models.BooleanField(default=False)
    task_is_default = models.BooleanField(default=False)
    task_created_by = models.ForeignKey(User, related_name="taskcreatorUser", on_delete=models.DO_NOTHING, null=True, blank=True)
    task_modified_by = models.ForeignKey(User, related_name="taskmodifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    task_created_at = models.DateTimeField(editable=False)
    task_modified_at = models.DateTimeField()

    def __str__(self):
        return self.task_name

    def save(self, *args, **kwargs):
        if not self.task_role_id:
            self.task_created_at = timezone.now()
        self.task_modified_at = timezone.now()
        return super(TasksRole, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TasksRoles"

# Tasks Roles Model End#


# Task Email Notification Permissions Model End#

class TasksEmailNotificationPermission(models.Model):
    t_email_permit_id = models.AutoField(primary_key=True)
    t_email_role = models.ForeignKey(TasksRole, related_name="taskRoleEmail", on_delete=models.DO_NOTHING)
    t_email_action = models.ForeignKey(TasksAction, related_name="taskActionEmail", on_delete=models.DO_NOTHING)
    t_email_is_deleted = models.BooleanField(default=False)
    t_email_created_by = models.ForeignKey(User, related_name="taskEmailCreatorUser", on_delete=models.DO_NOTHING)
    t_email_modified_by = models.ForeignKey(User, related_name="taskEmailModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    t_email_created_at = models.DateTimeField(editable=False)
    t_email_modified_at = models.DateTimeField()
    t_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.t_email_role.t_name + self.t_email_action.t_action_name

    def save(self, *args, **kwargs):
        if not self.t_email_permit_id:
            self.t_email_created_at = timezone.now()
        self.t_email_modified_at = timezone.now()
        return super(TasksEmailNotificationPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TasksEmailNotificationPermissions"

# Task Email Notification Permissions Model End#

# DepartmentEmailNotificationPermission Model Start#
class DepartmentEmailNotificationPermission(models.Model):
    notif_per_id = models.AutoField(primary_key=True)   
    dep = models.ForeignKey(Department,related_name='department_email_notification_children', on_delete=models.DO_NOTHING, blank=True, null=True)        
    t_action = models.ForeignKey(TicketsActions, on_delete=models.DO_NOTHING, blank=True, null=True)        
    email = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return str(self.notif_per_id)

    def save(self, *args, **kwargs):
        if not self.notif_per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(DepartmentEmailNotificationPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DepartmentEmailNotificationPermissions"

# DepartmentEmailNotificationPermission Model End#


# MailBox Model Start#
class MailBox(models.Model):
    mail_box_id = models.AutoField(primary_key=True)
    active = models.CharField(max_length=255)    
    server_type = models.CharField(max_length=255)    
    enable_auto_discover = models.CharField(max_length=255)    
    mail_server = models.CharField(max_length=255)    
    use_TLS = models.CharField(max_length=255)    
    TLS_port = models.CharField(max_length=255,default="")    
    domain = models.CharField(max_length=255)    
    version = models.CharField(max_length=255)    
    EWS_server_url = models.CharField(max_length=255)    
    account_id = models.CharField(max_length=255)    
    password = models.CharField(max_length=255)    
    return_address = models.CharField(max_length=255,default="")    
    from_name = models.CharField(max_length=255,default="")    
    delete_message_processing = models.CharField(max_length=255)    
    assign_to = models.IntegerField(null=True)    
    quick_pick = models.CharField(max_length=255)    
    default_quick_pick = models.CharField(max_length=255,default="")    
    assign_ticket_type = models.CharField(max_length=255)    
    default_ticket_type = models.IntegerField(null=True)  
    submitting_user = models.CharField(max_length=255)    
    caller_id1 = models.IntegerField(null=True)   
    caller_id2 = models.IntegerField(null=True)   
    submit_user_organization = models.IntegerField(null=True)   
    submit_user_client = models.IntegerField(null=True)   
    additional_option1 = models.CharField(max_length=255,default="")    
    additional_option2 = models.CharField(max_length=255,default="")    
    additional_option3 = models.CharField(max_length=255)    
    enable_cc_list = models.CharField(max_length=255,default="")    
    cc_user = models.CharField(max_length=255)    
    add_user_template = models.IntegerField(null=True) 
    cc_user_organization = models.IntegerField(null=True) 
    cc_user_client = models.IntegerField(null=True)  
    cc_user_checkbox1 = models.CharField(max_length=255,default="")    
    cc_user_checkbox2 = models.CharField(max_length=255,default="")    
    reopen_tickets = models.CharField(max_length=255,default="")    
    notify_on_error = models.CharField(max_length=255,default="")    
    max_size = models.CharField(max_length=255,default="")    
    refuse_count = models.CharField(max_length=255,default="5")    
    within_count = models.CharField(max_length=255,default="5")
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    mail_box_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.mail_box_id)

    def save(self, *args, **kwargs):
        if not self.mail_box_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(MailBox, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_MailBoxs"

# MailBox Model End#


# HoursOfOperation Model Start#
class HistoryHoursOfOperation(models.Model):
    hhop_id = models.AutoField(primary_key=True)
    hhop_type = models.CharField(max_length=100, null=True)
    hhop_previous_value = models.CharField(max_length=100, null=True)
    hhop_current_value = models.CharField(max_length=100, null=True)
    hhop_modified_by = models.CharField(max_length=100, default='admin')
    hhop_recalculation = models.CharField(max_length=100, default='Open')
    hhop_is_active = models.BooleanField(default=True)
    hhop_is_delete = models.BooleanField(default=False)
    hhop_created_at = models.DateTimeField(auto_now_add=True)
    hhop_modified_at = models.DateTimeField(auto_now=True)
    hhop_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.hhop_id

    def save(self, *args, **kwargs):
        if not self.hhop_id:
            self.hhop_created_at = timezone.now()
        self.hhop_modified_at = timezone.now()
        return super(HistoryHoursOfOperation, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_HistoryHoursOfOperations"

# HoursOfOperation Model End#


# User Attachments Model Start#
class UserAttachment(models.Model):
    ua_id = models.AutoField(primary_key=True)
    ua_user = models.ForeignKey(User, related_name="ua_userAttachment", on_delete=models.DO_NOTHING, blank=True, null=True)
    ua_file_name = models.TextField(null=True)
    ua_file_size = models.CharField(max_length=100, null=True)
    ua_file_path = models.FileField(upload_to='attachments/',null=True)
    # upload_user_file_1 = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    # upload_user_file_2 = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    # upload_user_file_3 = models.FileField(upload_to='documents/%Y/%m/%d',null=True)
    ua_is_active = models.BooleanField(default=True)
    ua_is_delete = models.BooleanField(default=False)
    ua_created_at = models.DateTimeField(auto_now_add=True)
    ua_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ua_id

    def save(self, *args, **kwargs):
        if not self.ua_id:
            self.ua_created_at = timezone.now()
        self.ua_modified_at = timezone.now()
        return super(UserAttachment, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserAttachments"
        
        

# User Attachments Model End#

#Email Custom Messages Event Start#
class CustomMessagesEvent(models.Model):
    cme_id = models.AutoField(primary_key=True)
    cme_name = models.CharField(max_length=100, null=True)
    cme_subject_slug = models.TextField(null=True)
    cme_message_slug = models.TextField(null=True)
    cme_is_active = models.BooleanField(default=True)
    cme_is_delete = models.BooleanField(default=False)
    cme_created_at = models.DateTimeField(auto_now_add=True, null=True)
    cme_modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.cme_name

    def save(self, *args, **kwargs):
        if not self.cme_id:
            self.cme_created_at = timezone.now()
        self.cme_modified_at = timezone.now()
        return super(CustomMessagesEvent, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_CustomMessagesEvents"

#Email Custom Messages Event End#

#Email Custom Messages Tokens Start#
class CustomMessagesToken(models.Model):
    cmt_id = models.AutoField(primary_key=True)
    cmt_name = models.CharField(max_length=100, null=True)
    cmt_slug = models.CharField(max_length=100, null=True)
    cmt_is_subject = models.BooleanField(default=True)
    cmt_is_active = models.BooleanField(default=True)
    cmt_is_delete = models.BooleanField(default=False)
    cmt_created_at = models.DateTimeField(auto_now_add=True, null=True)
    cmt_modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.cmt_name

    def save(self, *args, **kwargs):
        if not self.cmt_id:
            self.cmt_created_at = timezone.now()
        self.cmt_modified_at = timezone.now()
        return super(CustomMessagesToken, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_CustomMessagesTokens"

#Email Custom Messages Tokens End#


#Email Custom Messages Start#
class CustomMessage(models.Model):
    cm_id = models.AutoField(primary_key=True)
    cm_event = models.ForeignKey(CustomMessagesEvent, related_name="cm_CustomMessagesEvent", on_delete=models.DO_NOTHING, blank=True, null=True)
    cm_event_name = models.CharField(max_length=100, null=True)
    cm_subject = models.TextField(null=True)
    cm_message = models.TextField(null=True)
    cm_is_subject = models.BooleanField(default=True)
    cm_is_active = models.BooleanField(default=True)
    cm_is_delete = models.BooleanField(default=False)
    cm_created_at = models.DateTimeField(auto_now_add=True, null=True)
    cm_modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.cm_id

    def save(self, *args, **kwargs):
        if not self.cm_id:
            self.cm_created_at = timezone.now()
        self.cm_modified_at = timezone.now()
        return super(CustomMessage, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_CustomMessages"

#Email Custom Messages End#


# Exclude Text Model Start#
class ExcludeText(models.Model):
    etext_id = models.AutoField(primary_key=True)
    etext_name = models.TextField()
    etext_is_delete = models.BooleanField(default=False)
    etext_created_at = models.DateTimeField(editable=False)
    etext_modified_at = models.DateTimeField()
    etext_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.etext_id)

    def save(self, *args, **kwargs):
        if not self.etext_id:
            self.etext_created_at = timezone.now()
        self.etext_modified_at = timezone.now()
        return super(ExcludeText, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ExcludeTexts"


# Exclude Text Model End#

class Keyword(models.Model):
    keywords_id = models.AutoField(primary_key=True)
    keywords_name = models.CharField(max_length=255,default="") 
    keywords_search_in = models.IntegerField()
    keywords_search_for = models.IntegerField()
    keywords_is_delete = models.BooleanField(default=False)
    keywords_created_at = models.DateTimeField(editable=False)
    keywords_modified_at = models.DateTimeField()
    keywords_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.keywords_id)

    def save(self, *args, **kwargs):
        if not self.keywords_id:
            self.keywords_created_at = timezone.now()
        self.keywords_modified_at = timezone.now()
        return super(Keyword, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Keywords"


class FieldToken(models.Model):
    ft_id = models.AutoField(primary_key=True)
    ft_field_name = models.CharField(max_length=255,default="") 
    ft_token_identifier = models.CharField(max_length=255,default="") 
    ft_is_active = models.BooleanField(default=False)
    ft_is_deletable = models.BooleanField(default=False)
    ft_is_delete = models.BooleanField(default=False)
    ft_created_at = models.DateTimeField(editable=False)
    ft_modified_at = models.DateTimeField()
    ft_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.ft_id)

    def save(self, *args, **kwargs):
        if not self.ft_id:
            self.ft_created_at = timezone.now()
        self.ft_modified_at = timezone.now()
        return super(FieldToken, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_FieldTokens"


class CommandToken(models.Model):
    ct_id = models.AutoField(primary_key=True)
    ct_command_name = models.CharField(max_length=255,default="") 
    ct_token_identifier = models.CharField(max_length=255,default="") 
    ct_is_active = models.BooleanField(default=False)
    ct_is_delete = models.BooleanField(default=False)
    ct_created_at = models.DateTimeField(editable=False)
    ct_modified_at = models.DateTimeField()

    def __str__(self):
        return str(self.ct_id)

    def save(self, *args, **kwargs):
        if not self.ct_id:
            self.ct_created_at = timezone.now()
        self.ct_modified_at = timezone.now()
        return super(CommandToken, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_CommandTokens"


class BlockedAttachment(models.Model):
    ba_id = models.AutoField(primary_key=True)
    ba_upload_attachment = models.FileField(upload_to='blockedattachments/')
    ba_file_size = models.CharField(max_length=100, null=True)
    ba_file_name = models.CharField(max_length=100, null=True)
    # ba_attach_created_by = models.ForeignKey(User, related_name="blockedAttachCreatedBy", on_delete=models.DO_NOTHING, blank=True, null=True)
    ba_attach_created_by_id = models.IntegerField()
    ba_is_delete = models.BooleanField(default=False)
    ba_created_at = models.DateTimeField(editable=False)
    ba_modified_at = models.DateTimeField()
    ba_org_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.ba_id)

    def save(self, *args, **kwargs):
        if not self.ba_id:
            self.ba_created_at = timezone.now()
        self.ba_modified_at = timezone.now()
        return super(BlockedAttachment, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_BlockedAttachments"


class MailBoxEmailViewLog(models.Model):
    evl_id = models.AutoField(primary_key=True)
    evl_mail_box = models.ForeignKey(MailBox, related_name="emailBoxID", on_delete=models.DO_NOTHING, blank=True, null=True)
    evl_ticket = models.ForeignKey(Ticket, related_name="ticketMailBoxRelation", on_delete=models.DO_NOTHING, blank=True, null=True)
    evl_to = models.CharField(max_length=500, null=True)
    evl_from = models.CharField(max_length=500, null=True)
    evl_cc = models.CharField(max_length=500, null=True)
    evl_subject = models.CharField(max_length=500, null=True)
    evl_bcc = models.CharField(max_length=500, null=True)
    evl_body = models.TextField()
    evl_received_date = models.DateTimeField(editable=False)
    evl_processed_date = models.DateTimeField(editable=False)
    evl_status = models.IntegerField(default=0)
    evl_status_message = models.TextField(null=True)
    evl_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.evl_id)

    def save(self, *args, **kwargs):
        if not self.evl_id:
            self.evl_processed_date = timezone.now()
        return super(MailBoxEmailViewLog, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_MailBoxEmailViewLogs"

#UserTemplate Model Start#
class UserTemplate(models.Model):
    user_temp_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=255)    
    username = models.CharField(max_length=255)    
    first_name = models.CharField(max_length=255)    
    last_name = models.CharField(max_length=255)    
    display_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    template_org_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.user_temp_id)

    def save(self, *args, **kwargs):
        if not self.user_temp_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(UserTemplate, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserTemplates"

# UserTemplate Model End#

# UserTemplateActionPermission Model Start#
class UserTemplateActionPermission(models.Model):
    per_id = models.AutoField(primary_key=True)   
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    perm_act = models.ForeignKey(PermissionAction, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.per_id

    def save(self, *args, **kwargs):
        if not self.per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(UserTemplateActionPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserTemplateActionPermissions"

# UserTemplateActionPermission Model End#

# UserTemplateSubActionPermission Model Start#
class UserTemplateSubActionPermission(models.Model):
    per_id = models.AutoField(primary_key=True)   
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    sub_act = models.ForeignKey(PermissionSubAction, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)   

    def save(self, *args, **kwargs):
        if not self.per_id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super(UserTemplateSubActionPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserTemplateSubActionPermissions"

# UserTemplateSubActionPermission Model End#

# UserTemplateMenuPermission Model Start#
class UserTemplateMenuPermission(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="tempPermissionUser", on_delete=models.DO_NOTHING,null=True, blank=True)
    menu = models.ForeignKey(Menus, related_name="tempPermissionMenu", on_delete=models.DO_NOTHING,null=True, blank=True)
    submenu = models.ForeignKey(SubMenus, related_name="tempPermissionSubMenu", on_delete=models.DO_NOTHING,null=True, blank=True)
    created_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(UserTemplateMenuPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserTemplateMenuPermissions"
# UserTemplateMenuPermission Model End#

# INCOMING EMAIL ATTACHEMENTS Model Start#
class IncomingEmailAttachement(models.Model):

    attach_id = models.AutoField(primary_key=True)
    email = models.ForeignKey(MailBoxEmailViewLog, related_name="evlRelation", on_delete=models.DO_NOTHING,null=True, blank=True)
    attach_name = models.CharField(max_length=255)    
    created_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(IncomingEmailAttachement, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_IncomingEmailAttachements"
# INCOMING EMAIL ATTACHEMENTS  Model End#

# Organization Actions Model End#
class OrganizationAction(models.Model):
    org_action_id = models.AutoField(primary_key=True)
    org_action_slug = models.CharField(max_length=100,null=True,blank=True)
    org_action_name = models.CharField(max_length=100)
    org_action_is_deleted = models.BooleanField(default=False)
    org_action_created_by = models.ForeignKey(User, related_name="orgActionCreatorUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    org_action_modified_by = models.ForeignKey(User, related_name="OrgActionModifierUser", on_delete=models.DO_NOTHING,null=True,blank=True)
    org_action_created_at = models.DateTimeField(editable=False)
    org_action_modified_at = models.DateTimeField()

    def __str__(self):
        return self.org_action_name

    def save(self, *args, **kwargs):
        if not self.org_action_id:
            self.org_action_created_at = timezone.now()
        self.org_action_modified_at = timezone.now()
        return super(OrganizationAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_OrganizationActions"
# Tickets Actions Model End#

#ORGANIZATION EMAIL NOTIFICATION USERS MODEL START#
class OrganizationEmailNotificationUserPermission(models.Model):
    id = models.AutoField(primary_key=True)   
    user = models.ForeignKey(User,related_name='user_organizationEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    org = models.ForeignKey(Organization,related_name='org_organizationEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    action = models.ForeignKey(OrganizationAction, related_name='action_organizationEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    email = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super(OrganizationEmailNotificationUserPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_OrganizationEmailNotificationUserPermissions"
#ORGANIZATION EMAIL NOTIFICATION USERS MODEL END#

# Client Actions Model End#
class ClientAction(models.Model):
    cli_action_id = models.AutoField(primary_key=True)
    cli_action_slug = models.CharField(max_length=100,null=True,blank=True)
    cli_action_name = models.CharField(max_length=100)
    cli_action_is_deleted = models.BooleanField(default=False)
    cli_action_created_by = models.ForeignKey(User, related_name="createClientAction", on_delete=models.DO_NOTHING,null=True,blank=True)
    cli_action_modified_by = models.ForeignKey(User, related_name="modifiedClientAction", on_delete=models.DO_NOTHING,null=True,blank=True)
    cli_action_created_at = models.DateTimeField(editable=False)
    cli_action_modified_at = models.DateTimeField()

    def _str_(self):
        return self.cli_action_name

    def save(self, *args, **kwargs):
        if not self.cli_action_id:
            self.cli_action_created_at = timezone.now()
            self.cli_action_modified_at = timezone.now()
        return super(ClientAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ClientActions"
# Client Actions Model End#

#Client EMAIL NOTIFICATION USERS MODEL START#
class ClientEmailNotificationUserPermission(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,related_name='user_ClientEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    client = models.ForeignKey(Client,related_name='cli_ClientEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    action = models.ForeignKey(OrganizationAction, related_name='action_ClientEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    email = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def _str_(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super(ClientEmailNotificationUserPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_ClientEmailNotificationUserPermissions"
#Client EMAIL NOTIFICATION USERS MODEL END#

# Department Actions Model End#
class DepartmentAction(models.Model):
    dep_action_id = models.AutoField(primary_key=True)
    dep_action_slug = models.CharField(max_length=100,null=True,blank=True)
    dep_action_name = models.CharField(max_length=100)
    dep_action_is_deleted = models.BooleanField(default=False)
    dep_action_created_by = models.ForeignKey(User, related_name="createDepartmentAction", on_delete=models.DO_NOTHING,null=True,blank=True)
    dep_action_modified_by = models.ForeignKey(User, related_name="modifiedDepartmentAction", on_delete=models.DO_NOTHING,null=True,blank=True)
    dep_action_created_at = models.DateTimeField(editable=False)
    dep_action_modified_at = models.DateTimeField()

    def _str_(self):
        return self.dep_action_name

    def save(self, *args, **kwargs):
        if not self.dep_action_id:
            self.dep_action_created_at = timezone.now()
            self.dep_action_modified_at = timezone.now()
        return super(DepartmentAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DepartmentActions"
# Department Actions Model End#

# DEPARTMENT EMAIL NOTIFICATION USERS MODEL START#
class DepartmentEmailNotificationUserPermission(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,related_name='user_DepartmentEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    dep = models.ForeignKey(Department,related_name='cli_DepartmentEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    action = models.ForeignKey(OrganizationAction, related_name='action_DepartmentEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    email = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def _str_(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super(DepartmentEmailNotificationUserPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_DepartmentEmailNotificationUserPermissions"
# DEPARTMENT EMAIL NOTIFICATION USERS MODEL END#

#Task Restrict To Start#
class TaskRestrict(models.Model):
    tr_id = models.AutoField(primary_key=True)
    tr_task = models.ForeignKey(Task, related_name="tr_task", on_delete=models.DO_NOTHING, blank=True,null=True)
    tr_group = models.ForeignKey(Group, related_name="tr_group", on_delete=models.DO_NOTHING, blank=True,null=True)
    tr_org = models.ForeignKey(Organization, related_name='tr_org', on_delete=models.DO_NOTHING, blank=True,null=True)
    tr_type_is_group = models.BooleanField(default=False)
    tr_type_is_org = models.BooleanField(default=False)
    tr_group_or_org_name = models.CharField(max_length=100, null=True)
    tr_is_active = models.BooleanField(default=True)
    tr_is_delete = models.BooleanField(default=False)
    tr_created_at = models.DateTimeField(auto_now_add=True, null=True)
    tr_modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.tr_id

    def save(self, *args, **kwargs):
        if not self.tr_id:
            self.tr_created_at = timezone.now()
        self.tr_modified_at = timezone.now()
        return super(TaskRestrict, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_TaskRestricts"

#Task Restrict To End#

# Email Log Model Start#
class EmailLog(models.Model):
    email_id = models.AutoField(primary_key=True)
    to = models.CharField(max_length=255, blank=True,null=True)
    cc = models.CharField(max_length=255, blank=True,null=True)
    bcc = models.CharField(max_length=255, blank=True,null=True)
    subject = models.CharField(max_length=255, blank=True,null=True)
    body = models.TextField(default="Email Body")
    event_name = models.CharField(max_length=255, blank=True,null=True)
    action_item = models.CharField(max_length=255, blank=True,null=True)
    auto_date = models.DateTimeField(auto_now_add=True)
    log_org_id = models.IntegerField(blank=True, null=True)
    log_user_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.email_id

    def save(self, *args, **kwargs):
        if not self.email_id:
            self.auto_date = timezone.now()
        return super(EmailLog, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_EmailLogs"
# Email Log Model End#

# Priority Actions Model End#
class PriorityAction(models.Model):
    pri_action_id = models.AutoField(primary_key=True)
    pri_action_slug = models.CharField(max_length=100,null=True,blank=True)
    pri_action_name = models.CharField(max_length=100)
    pri_action_is_deleted = models.BooleanField(default=False)
    pri_action_created_by = models.ForeignKey(User, related_name="createdByPriorityAction", on_delete=models.DO_NOTHING,null=True,blank=True)
    pri_action_modified_by = models.ForeignKey(User, related_name="modifiedByPriorityAction", on_delete=models.DO_NOTHING,null=True,blank=True)
    pri_action_created_at = models.DateTimeField(editable=False)
    pri_action_modified_at = models.DateTimeField()

    def __str__(self):
        return self.pri_action_name

    def save(self, *args, **kwargs):
        if not self.pri_action_id:
            self.pri_action_created_at = timezone.now()
        self.pri_action_modified_at = timezone.now()
        return super(PriorityAction, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PriorityActions"
#Priority Actions Model End#

#Priority EMAIL NOTIFICATION USERS MODEL START#
class PriorityEmailNotificationUserPermission(models.Model):
    id = models.AutoField(primary_key=True)   
    user = models.ForeignKey(User,related_name='user_priorityEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    priority = models.ForeignKey(Priority,related_name='org_priorityEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    action = models.ForeignKey(PriorityAction, related_name='action_priorityEmailNotificationUserPermission', on_delete=models.DO_NOTHING, blank=True, null=True)
    email = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super(PriorityEmailNotificationUserPermission, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_PriorityEmailNotificationUserPermissions"
#Priority EMAIL NOTIFICATION USERS MODEL END#

#User Account Relation MODEL START#
class UserAccountRelation(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True,blank=True)
    account_id = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(editable=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(UserAccountRelation, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_UserAccountRelation"
#User Account Relation MODEL END#


#Account Relation MODEL START#
class GlobalACCTS(models.Model):
    id = models.AutoField(primary_key=True)
    AIAN_DK = models.CharField(max_length=100,null=True,blank=True)
    acc_number = models.CharField(max_length=100,null=True,blank=True)
    acc_name = models.CharField(max_length=100,null=True,blank=True)
    agency = models.CharField(max_length=100,null=True,blank=True)
    login_id = models.CharField(max_length=100,null=True,blank=True)
    agency_email = models.CharField(max_length=100,null=True,blank=True)
    status = models.BooleanField(default=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    client = models.CharField(max_length=100,null=True,blank=True)
    company = models.CharField(max_length=100,null=True,blank=True)
    currency = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    created_by_id = models.IntegerField()
    updated_by_id = models.IntegerField()
    note = models.TextField()
    uploaded = models.BooleanField(default=True)
    uploaded_date = models.DateTimeField(editable=False)
    exported = models.BooleanField(default=True)
    exported_date = models.DateTimeField(editable=False)
    updated_accts = models.DateTimeField(editable=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        return super(GlobalACCTS, self).save(*args, **kwargs)

    class Meta:
        db_table = "GlobalACCTS"
#Account MODEL END#

# Ticket Currency Model starts here
class Currency(models.Model):
    country = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=25, blank=True, null=True)
    symbol = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AT_Currency'
# Ticket Currency Model ends here

# Ticket Agent Sines Model starts here
class Agentsines(models.Model):
    id = models.AutoField(primary_key=True)
    agent_name = models.CharField(max_length=100, blank=True, null=True)
    agent_sine = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AT_AgentSines'
# Ticket Agent Sines Model ends here

# Iorad Model Start#
class Iorad(models.Model):
    iorad_id = models.AutoField(primary_key=True)
    iorad_title = models.CharField(max_length=255)
    iorad_link = models.CharField(max_length=255)
    iorad_is_delete = models.BooleanField(default=False)
    iorad_created_at = models.DateTimeField(editable=False)
    iorad_modified_at = models.DateTimeField()

    def __str__(self):
        return str(self.iorad_id)

    def save(self, *args, **kwargs):
        if not self.iorad_id:
            self.iorad_created_at = timezone.now()
        self.iorad_modified_at = timezone.now()
        return super(Iorad, self).save(*args, **kwargs)

    class Meta:
        db_table = "AT_Iorad"
# Iorad Model End #

# Submit Ticket Configuration begins
class AtTicketFields(models.Model):
    field_id = models.AutoField(primary_key=True)
    field_name = models.CharField(max_length=80, blank=True, null=True)
    created_by = models.CharField(max_length=80, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AT_ticket_fields'

#end Submit Ticket Configuration ends

# AtTicketFieldsOrganization begins

class AtTicketFieldsOrganization(models.Model):
    tf_co_id = models.AutoField(primary_key=True)
    org = models.ForeignKey('Organization', models.DO_NOTHING, blank=True, null=True)
    field = models.ForeignKey('AtTicketFields', models.DO_NOTHING, blank=True, null=True)
    created_by = models.CharField(max_length=80, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    show_field = models.BooleanField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AT_ticket_fields_organization'

# AtTicketFieldsOrganization ends
