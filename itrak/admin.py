from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import *

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class MyUserAdmin(UserAdmin):
    form = UserChangeForm

    list_display = ('username', 'first_name', 'last_name', 'is_admin')
    list_filter = ('first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (('first_name', 'last_name'))}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


# Register your models here.
admin.site.register(Organization)
admin.site.register(Client)
admin.site.register(Department)
admin.site.register(Group)
admin.site.register(Role)
admin.site.register(User, MyUserAdmin)
admin.site.register(Menus)
admin.site.register(SubMenus)
admin.site.register(Sections)
admin.site.register(TicketType)
admin.site.register(DataSetsPairFields)
admin.site.register(DataSetsFieldsConditions)
admin.site.register(ReportSettingDataType)
admin.site.register(ReportSettingFormat)
admin.site.register(ReportSettingJustification)
admin.site.register(DataSetsPair)
admin.site.register(PermissionSection)
admin.site.register(PermissionAction)
admin.site.register(PermissionSubAction)




admin.site.register(UserActionPermission)
admin.site.register(UserSubActionPermission)
admin.site.register(ClientEmailNotificationPermission)
admin.site.register(MailBox)
admin.site.register(TicketEvent)
admin.site.register(CustomMessagesEvent)
admin.site.register(CustomMessagesToken)
admin.site.register(OrganizationAction)
admin.site.register(ClientAction)
admin.site.register(DepartmentAction)
admin.site.register(TicketsRoles)
admin.site.register(TicketsActions)
admin.site.register(TasksAction)
admin.site.register(TasksRole)
admin.site.register(PriorityAction)




