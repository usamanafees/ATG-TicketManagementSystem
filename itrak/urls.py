# pages/urls.py
from django.conf.urls import url
from django.urls import path
from itrak import views
from .views import  OrgListJson, ClientListJson, DepartmentListJson, GroupListJson, UserListJson, ClientInfoListJson, TicketTypeListJson, PriorityListJson, SolutionListJson, SubStatusListJson, TaskListJson, TaskGroupListJson, MyTicketListJson, ScheduleRptListJson, EmailsListJson, BusinessRulesListJson,MailBoxListJson,ExcludeTextJSON,KeywordsJSON, BlockedAttachmentsJSON, MailBoxEmailViewLogJSON, HoursOfOperationListJson, UserSummaryListJson
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404


base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'
























urlpatterns = [

    # Auth URLs Start
    url(r'^$', views.auth_login, name='login'),
    url(r'signin', views.signin, name='signin'),
    url(r'^signout/$', views.signout, name='signout'),
    url(r'^home', views.home, name='home'),
    url(r'^accounts/', views.auth_login, name='login'),
    url(r'^resetPassword/', views.resetPassword, name='resetPassword'),
    url(r'^updatePassword/', views.updatePassword, name='updatePassword'),
    url(r'^validatePassword/$', views.validatePassword, name='validatePassword'),
    url(r'^forgetPassword/$', views.forgetPassword, name='forgetPassword'),
    url(r'^forgotPasswordEmail/$', views.forgotPasswordEmail, name='forgotPasswordEmail'),

    # Auth URLs End


    # Organization URLs Start
    url(r'Admin_OrganizationAdd', views.addOrganization, name='addOrg'),
    url(r'Admin_OrganizationSave', views.saveOrganization, name='saveOrg'),
    url(r'Admin_OrganizationList', views.listOrganization, name='listOrg'),
    # path('Admin_OrganizationEdit/(?P<id>{})'.format(base64_pattern), views.editOrganization, name='editOrg'),
    path(r'Admin_OrganizationEdit', views.editOrganization, name='editOrg'),
    path('Admin_OrganizationUpdate', views.updateOrganization, name='updateOrg'),
    path(r'Admin_OrganizationDel', views.deleteOrganization, name='deleteOrg'),
    path(r'Admin_OrganizationEnable', views.enableOrganization, name='deleteOrg'),
    url(r'Admin_OrganizationExport', views.exportOrganization, name='exportOrg'),
    url(r'^OrgListDatatable/data/$', login_required(OrgListJson.as_view()), name='org_list_json'),
    url(r'^validateAddUnique/$', views.validateAddUnique, name='validateAddUnique'),
    url(r'^validateEditUnique/$', views.validateEditUnique, name='validateEditUnique'),
    url(r'^export_organizations_xls/$', views.export_organizations_xls, name='export_organizations_xls'),
    url(r'^getModalOrgUsersById/$', views.getModalOrgUsersById, name='getModalOrgUsersById'),
    url(r'^getModalOrgViewById/$', views.getModalOrgViewById, name='getModalOrgViewById'),
    url(r'^getModalOrgTicketsById/$', views.getModalOrgTicketsById, name='getModalOrgTicketsById'),
    url(r'Admin_OrgContractAdd', views.SaveOrgContract, name='SaveOrgContract'),
    url(r'Admin_OrgBatchContractAdd', views.SaveOrgBatchContract, name='SaveOrgBatchContract'),
    url(r'getserviceContractByOrgId', views.getserviceContractByOrgId, name='getserviceContractByOrgId'),
    url(r'getserviceContractByOrgViewId', views.getserviceContractByOrgViewId, name='getserviceContractByOrgViewId'),
    url(r'deleteServiceContractByOrgId', views.deleteServiceContractByOrgId, name='deleteServiceContractByOrgId'),
    url(r'getserviceContractByOrgContractId', views.getserviceContractByOrgContractId, name='getserviceContractByOrgContractId'),
    url(r'UpdateerviceContractByOrgContractId', views.UpdateerviceContractByOrgContractId, name='UpdateerviceContractByOrgContractId'),
    url(r'getscheduleReportRecpBySchId', views.getscheduleReportRecpBySchId, name='getscheduleReportRecpBySchId'),
    url(r'export_organization_users_xls', views.export_organization_users_xls, name='export_organization_users_xls'),
    path(r'Admin_OrgEmailNotification', views.orgEmailNotification, name='orgEmailNotification'),
    path(r'getModalOrgEmailPermissionsByID', views.getModalOrgEmailPermissionsByID, name='getModalOrgEmailPermissionsByID'),
    url(r'Admin_updateOrgEmailMobileNotifications', views.updateOrgEmailMobileNotifications, name='updateOrgEmailMobileNotifications'),
    url(r'deleteOrgEmailMobilePermissions', views.deleteOrgEmailMobilePermissions, name='deleteOrgEmailMobilePermissions'),
    url(r'^export_users_by_organization_xls/$', views.export_users_by_organization_xls, name='export_users_by_organization_xls'),
    url(r'Admin_GetAllOrgJson', views.getAllOrgJson, name='getAllOrgJson'),
    url(r'Admin_GetOrgUsers', views.getOrgUsers, name='getOrgUsers'),
    url(r'Admin_GetAllOrgJson', views.getAllOrgJson, name='getAllOrgJson'),
    url(r'Admin_OrganizatoinWithUsers', views.organizatoinUsers, name='organizatoinUsers'),
    url('Home_ViewOrganization', views.viewOrg, name='viewOrg'),
    path(r'getModalToAddUserPermissionsInOrg', views.getModalToAddUserPermissionsInOrg, name='getModalToAddUserPermissionsInOrg'),
    url(r'Admin_SaveOrgUserNotificationPermissions', views.saveOrgUserNotificationPermissions, name='saveOrgUserNotificationPermissions'),
    # Organization URLs End


    # Client URLs Start
    url(r'Admin_ClientAdd', views.addClient, name='addClient'),
    url(r'Admin_ClientSave', views.saveClient, name='saveClient'),
    url(r'Admin_ClientList', views.listClients, name='listClient'),
    path(r'Admin_ClientEdit', views.editClient, name='editClient'),
    path('Admin_ClientUpdate', views.updateClient, name='updateClient'),
    path(r'Admin_ClientDel', views.deleteClient, name='deleteClient'),
    url(r'Admin_ClientExport', views.exportOrganization, name='exportOrg'),
    url(r'^ClientListdatatable/data/$', login_required(ClientListJson.as_view()), name='client_list_json'),
    path(r'Admin_clientEmailNotification', views.clientEmailNotification, name='clientEmailNotification'),
    path(r'getModalClientEmailPermissionsByID', views.getModalClientEmailPermissionsByID, name='getModalClientEmailPermissionsByID'),
    url(r'updateClientEmailMobileNotifications', views.updateClientEmailMobileNotifications, name='updateClientEmailMobileNotifications'),
    url(r'deleteClientEmailMobilePermissions', views.deleteClientEmailMobilePermissions, name='deleteClientEmailMobilePermissions'),
    url(r'^export_users_by_client_xls/$', views.export_users_by_client_xls, name='export_users_by_client_xls'),
    url(r'Admin_ClientUsers', views.clientUsers, name='clientUsers'),
    url(r'Admin_GetAllClientsJson', views.getAllClientsJson, name='getAllClientsJson'),
    url(r'Admin_GetClientUsers', views.getClientUsers, name='getClientUsers'),
    url('Home_ViewClient', views.viewClient, name='viewClient'),
    path(r'getModalToAddUserPermissionsInClient', views.getModalToAddUserPermissionsInClient, name='getModalToAddUserPermissionsInClient'),
    url(r'Admin_SaveClientUserNotificationPermissions', views.saveClientUserNotificationPermissions, name='saveClientUserNotificationPermissions'),
    url(r'^accountListJsonData/$', views.accountListJsonData, name='accountListJsonData'), 
    url(r'^selectedAccountListJsonData/$', views.selectedAccountListJsonData, name='selectedAccountListJsonData'), 
    url(r'^sendUserType/$', views.sendUserType, name='sendUserType'), 
    # Client URLs End


    # Department URLs Start
    url(r'Admin_DeptAdd', views.addDepartment, name='addDepartment'),
    url(r'Admin_DeptSave', views.saveDepartment, name='saveDepartment'),
    url(r'Admin_DeptList', views.listDepartments, name='listDepartment'),
    path('Admin_DeptEdit', views.editDepartment, name='editDepartment'),
    path('Admin_DeptUpdate', views.updateDepartment, name='updateDepartment'),
    path(r'Admin_DeptDel', views.deleteDepartment, name='deleteDepartment'),
    url(r'Admin_DeptExport', views.exportDepartment, name='exportDepartment'),
    url(r'^DeptListDatatable/data/$', login_required(DepartmentListJson.as_view()), name='department_list_json'),
    url(r'^getModalDepUsersById/$', views.getModalDepUsersById, name='getModalDepUsersById'),    
    url(r'export_dep_users_xls', views.export_dep_users_xls, name='export_dep_users_xls'),
    path(r'Admin_depEmailNotification', views.depEmailNotification, name='depEmailNotification'),
    path(r'getModalDepEmailPermissionsByID', views.getModalDepEmailPermissionsByID, name='getModalDepEmailPermissionsByID'),
    url(r'updateDepEmailMobileNotifications', views.updateDepEmailMobileNotifications, name='updateDepEmailMobileNotifications'),
    url(r'deleteDepEmailMobilePermissions', views.deleteDepEmailMobilePermissions, name='deleteDepEmailMobilePermissions'),
    url(r'^export_users_by_department_xls/$', views.export_users_by_department_xls, name='export_users_by_department_xls'),
    url(r'Admin_departmentUsers', views.departmentUsers, name='departmentUsers'),
    url(r'Admin_GetAllDepartmentsJson', views.getAllDepartmentsJson, name='getAllDepartmentsJson'),
    url(r'Admin_GetDepUsers', views.getDepUsers, name='getDepUsers'),
    url('Home_ViewDepartment', views.viewDepartment, name='viewDepartment'),
    path(r'getModalToAddUserPermissionsInDepartment', views.getModalToAddUserPermissionsInDepartment, name='getModalToAddUserPermissionsInDepartment'),
    url(r'Admin_SaveDepartmentUserNotificationPermissions', views.saveDepartmentUserNotificationPermissions, name='saveDepartmentUserNotificationPermissions'),
    # Department URLs End


    # Group URLs Start
    url(r'Admin_GroupAdd', views.addGroup, name='addGroup'),
    url(r'Admin_GroupSave', views.saveGroup, name='saveGroup'),
    url(r'Admin_GroupList', views.listGroups, name='listGroup'),
    path('Admin_GroupEdit', views.editGroup, name='editGroup'),
    path('Admin_GroupUpdate', views.updateGroup, name='updateGroup'),
    path(r'Admin_GroupDel', views.deleteGroup, name='deleteGroup'),
    url(r'Admin_GroupExport', views.exportGroup, name='exportGroup'),
    url(r'^GroupListDatatable/data/$', login_required(GroupListJson.as_view()), name='group_list_json'),
    url(r'Admin_GroupMembers', views.groupMembers, name='groupMembers'),
    url(r'Admin_GetAllGroupsJson', views.getAllGroupsJson, name='getAllGroupsJson'),
    url(r'Admin_GetGroupMembers', views.getGroupMembers, name='getGroupMembers'),
    url(r'^export_users_by_group_xls/$', views.export_users_by_group_xls, name='export_users_by_group_xls'),
    url('Home_ViewGroup', views.viewGroup, name='viewGroup'),
    # Group URLs End


    # User URLs Start
    url(r'Admin_UserAdd', views.addUser, name='addUser'),
    url(r'Admin_UserSave', views.saveUser, name='saveUser'),
    url(r'Admin_UserList', views.listUsers, name='listUser'),
    path('Admin_UserEdit', views.editUser, name='editUser'),
    path('Admin_UserUpdate', views.updateUser, name='updateUser'),
    path(r'Admin_UserDel', views.deleteUser, name='deleteUser'),
    url(r'Admin_UserExport', views.exportUser, name='exportUser'),
    url(r'^UserListDatatable/data/$', login_required(UserListJson.as_view()), name='user_list_json'),
    url(r'^validateUnique/$', views.validate, name='validate'),
    url(r'Admin_CloneUser', views.cloneUser, name='cloneUser'),
    url(r'^userLookUp', views.userLookUp, name='userLookUp'),
    url(r'^cloneUser', views.cloneUserform, name='cloneUserform'),
    url(r'Admin_SearchUser', views.searchUser, name='searchUser'),
    url(r'Home_UsersSearchList', views.userSearchResults, name='userSearchResults'),
    url(r'Admin_UserChangeUserID', views.userIDmaintenance, name='userIDmaintenance'),
    url(r'Admin_UserMerge', views.UserMerge, name='UserMerge'),
    url(r'DuplicateUserMerge', views.DuplicateUserMerge, name='DuplicateUserMerge'),
    url(r'Admin_UserChangeID', views.UserChangeID, name='UserChangeID'),
    url(r'userChangeIDupdate', views.userChangeIDupdate, name='userChangeIDupdate'),
    url(r'Admin_UserSummary', views.userSummary, name='userSummary'),
    url(r'getSummaryList', views.getSummaryList, name='getSummaryList'),
    url(r'Admin_SaveUserFiles', views.saveUserFiles, name='saveUserFiles'),
    path(r'Admin_UserAttachments', views.userAttachments, name='userAttachments'),
    url(r'Admin_SaveUserAttachmentFiles', views.saveUserAttachmentFiles, name='saveUserAttachmentFiles'),
    url(r'Home_DeleteUserAttach', views.deleteUserAttach, name='deleteUserAttach'),
    url('changeUsersPassword', views.changeUsersPassword, name='changeUsersPassword'),
    url('UserPasswordChange', views.userPasswordChange, name='userPasswordChange'),
    url('Home_ViewUser', views.viewUser, name='viewUser'),
    path('Admin_UpdateViewGroupMembershipUser', views.updateViewGroupMembershipUser, name='updateViewGroupMembershipUser'),
    path(r'Admin_UserEmailNotification', views.userEmailNotification, name='userEmailNotification'),
    url(r'^UserSummaryListDatatable/data/$', login_required(UserSummaryListJson.as_view()), name='user_summary_list_json'),
    
    url(r'^showGroupsnWhichGivesPermisison/$', views.showGroupsnWhichGivesPermisison, name='showGroupsnWhichGivesPermisison'), 
    
    

    # User URLs End


    # Client Information URLs Start
    url(r'Admin_ClientInfoAdd', views.addClientInfo, name='addClientInfo'),
    url(r'Admin_ClientInfoSave', views.saveClientInfo, name='saveClientInfo'),
    url(r'Admin_ClientInfoList', views.listClientInfos, name='listClientInfo'),
    path('Admin_ClientInfoEdit', views.editClientInfo, name='editClientInfo'),
    path('Admin_ClientInfoUpdate', views.updateClientInfo, name='updateClientInfo'),
    path(r'Admin_ClientInfoDel', views.deleteClientInfo, name='deleteClientInfo'),
    url(r'^ClientInfotListDatatable/data/$', login_required(ClientInfoListJson.as_view()), name='clientinfo_list_json'),
    url(r'^validateRLUnique/$', views.validateUnique, name='validateUnique'),
    url(r'^getModalUsersByClientId/$', views.getModalUsersByClientId, name='getModalUsersByClientId'), 
    url(r'export_client_users_xls', views.export_client_users_xls, name='export_client_users_xls'),  

    # Client Information URLs End


    # Ticket Type URLs Start
    url(r'Admin_TicketTypeAdd', views.addTicketType, name='addTicketType'),
    url(r'Admin_TicketTypeSave', views.saveTicketType, name='saveTicketType'),
    path('Admin_TicketTypeList', views.listTicketTypes, name='listTicketType'),
    path('Admin_TicketTypeEdit', views.editTicketType, name='editTicketType'),
    path('Admin_TicketTypeUpdate', views.updateTicketType, name='updateTicketType'),
    path(r'Admin_TicketTypeDel', views.deleteTicketType, name='deleteTicketType'),
    url(r'^TicketTypetListDatatable/data/$', login_required(TicketTypeListJson.as_view()), name='tickettype_list_json'),
    url(r'^validateRLUnique/$', views.validateUnique, name='validateUnique'),
    url(r'^TicketTypeJsonData/$', views.TicketTypeJsonData, name='TicketTypeJsonData'),    
    url(r'^getParentIDValue/$', views.getParentIDValue, name='getParentIDValue'),    
    url(r'^export_tickettypes_xls/$', views.export_tickettypes_xls, name='export_tickettypes_xls'),
    # Ticket Type URLs End


    # Priority URLs Start
    url(r'Admin_PriorityAdd', views.addPriority, name='addPriority'),
    url(r'Admin_PrioritySave', views.savePriority, name='savePriority'),
    url(r'Admin_PriorityList', views.listPriority, name='listPriority'),
    path('Admin_PriorityEdit', views.editPriority, name='editPriority'),
    path('Admin_PriorityUpdate', views.updatePriority, name='updatePriority'),
    path(r'Admin_PriorityDel', views.deletePriority, name='deletePriority'),
    url(r'^PrioritytListDatatable/data/$', login_required(PriorityListJson.as_view()), name='priority_list_json'),
    url(r'^validatePUnique/$', views.validatePUnique, name='validatePUnique'),
    path(r'Admin_PriorityEmailNotification', views.priorityEmailNotification, name='priorityEmailNotification'),
    path(r'getModalToAddUserPermissionsInPermission', views.getModalToAddUserPermissionsInPermission, name='getModalToAddUserPermissionsInPermission'),
    url(r'Admin_SavePriorityUserNotificationPermissions', views.savePriorityUserNotificationPermissions, name='savePriorityUserNotificationPermissions'),
    path(r'getModalPriorityEmailPermissionsByID', views.getModalPriorityEmailPermissionsByID, name='getModalPriorityEmailPermissionsByID'),
    url(r'Admin_updatePriorityEmailMobileNotifications', views.updatePriorityEmailMobileNotifications, name='updatePriorityEmailMobileNotifications'),
    url(r'deletePriorityEmailMobilePermissions', views.deletePriorityEmailMobilePermissions, name='deletePriorityEmailMobilePermissions'),
    # Priority URLs End


    # Solution URLs Start
    url(r'Admin_SolutionAdd', views.addSolution, name='addSolution'),
    url(r'Admin_SolutionSave', views.saveSolution, name='saveSolution'),
    url(r'Admin_SolutionList', views.listSolution, name='listSolution'),
    url('Admin_SolutionEdit', views.editSolution, name='editSolution'),
    path('Admin_SolutionUpdate', views.updateSolution, name='updateSolution'),
    path(r'Admin_SolutionDel', views.deleteSolution, name='deleteSolution'),
    url(r'^SolutiontListDatatable/data/$', login_required(SolutionListJson.as_view()), name='solution_list_json'),
    url(r'^validateSolUnique/$', views.validateSolUnique, name='validateSolUnique'),

    # Solution URLs End


    # SubStatus URLs Start
    url(r'Admin_SubStatusAdd', views.addSubStatus, name='addSubStatus'),
    url(r'Admin_SubStatusSave', views.saveSubStatus, name='saveSubStatus'),
    url(r'Admin_SubStatusList', views.listSubStatus, name='listSubStatus'),
    path('Admin_SubStatusEdit', views.editSubStatus, name='editSubStatus'),
    path('Admin_SubStatusUpdate', views.updateSubStatus, name='updateSubStatus'),
    path(r'Admin_SubStatusDel', views.deleteSubStatus, name='deleteSubStatus'),
    url(r'^SubStatustListDatatable/data/$', login_required(SubStatusListJson.as_view()), name='sub_status_list_json'),
    url(r'^validateStatusUnique/$', views.validateStatusUnique, name='validateStatusUnique'),

    # Sub Status URLs End


    # Task URLs Start
    url(r'Admin_TaskAdd', views.addTask, name='addTask'),
    url(r'Admin_TaskSave', views.saveTask, name='saveTask'),
    url(r'Admin_TaskList', views.listTask, name='listTask'),
    path('Admin_TaskEdit', views.editTask, name='editTask'),
    path('Admin_TaskUpdate', views.updateTask, name='updateTask'),
    path(r'Admin_TaskDel', views.deleteTask, name='deleteTask'),
    url(r'^TaskListDatatable/data/$', login_required(TaskListJson.as_view()), name='task_list_json'),
    url(r'^validateTaskUnique/$', views.validateTaskUnique, name='validateTaskUnique'),
    url(r'Admin_TaskGroupAdd', views.addTaskGroup, name='AddTaskGroup'),
    url(r'Admin_TaskGroupSave', views.saveTaskGroup, name='saveTaskGroup'),
    url(r'Admin_TaskGroupList', views.listTaskGroup, name='listTaskGroup'),
    path('Admin_TaskGroupEdit', views.editTaskGroup, name='editTaskGroup'),
    path('Admin_TaskGroupUpdate', views.updateTaskGroup, name='updateTaskGroup'),
    path(r'Admin_TaskGroupDel', views.deleteTaskGroup, name='deleteTaskGroup'),
    url(r'^TaskGroupListDatatable/data/$', login_required(TaskGroupListJson.as_view()), name='taskgroup_list_json'),
    url(r'^getModalGroupTasksById/$', views.getModalGroupTasksById, name='getModalGroupTasksById'),
    url(r'^saveModalTaskManagerByTaskGroupId/$', views.saveModalTaskManagerByTaskGroupId, name='saveModalTaskManagerByTaskGroupId'),
    url(r'^getTaskTypeById/$', views.getTaskTypeById, name='getTaskTypeById'),
    url(r'^getGroupModalTaskManagerById/$', views.getGroupModalTaskManagerById, name='getGroupModalTaskManagerById'),
    url(r'^getGroupTableTaskManagerById/$', views.getGroupTableTaskManagerById, name='getGroupTableTaskManagerById'),
    url(r'^getTaskManagerByTaskgroupId/$', views.getTaskManagerByTaskgroupId, name='getTaskManagerByTaskgroupId'),
    url(r'Admin_RestrictTaskGroupSave/$', views.saveRestrictTaskGroup, name='saveRestrictTaskGroup'),
    url(r'Admin_RestrictTaskGroupDelete', views.deleteRestrictTaskGroup, name='deleteRestrictTaskGroup'),
    path('Admin_TaskGroupChildList', views.childlistTaskGroup, name='childlistTaskGroup'),
    url('Admin_GetAllTaskGroupJson', views.getAllTaskGroupJson, name='getAllTaskGroupJson'),
    url('Admin_GetTasksByTaskGroup', views.getTasksByTaskGroup, name='getTasksByTaskGroup'),
    url(r'Admin_RestrictTaskSave/$', views.saveRestrictTask, name='saveRestrictTask'),
    url(r'Admin_RestrictTaskDelete', views.deleteRestrictTask, name='deleteRestrictTask'),
    # Sub Status URLs EndgetTaskManagerByTicketId


    # My ATG URLs Start
    url(r'Home_MyTicket', views.myTickets, name='myTickets'),
    url(r'^MyTicketListDatatable/data/$', login_required(MyTicketListJson.as_view()), name='myticket_list_json'),
    url(r'Home_SaveTicket', views.saveTicket, name='saveTicket'),
    path('Home_ViewTicket', views.viewTicket, name='viewTicket'),
    url(r'^editTicket', views.editTicket, name='editTicket'),
    url(r'Home_UpdateTicket', views.updateTicket, name='updateTicket'),
    url(r'updateTicketTaskManager', views.updateTicketTaskManager, name='updateTicketTaskManager'),
    url(r'^deleteTicket', views.deleteTicket, name='deleteTicket'),
    path('Home_CloseTicket/<int:id>', views.closeTicket, name='closeTicket'),
    path('Home_AttachTicket', views.attachTicket, name='attachTicket'),
    url(r'SaveTAttachs', views.saveTAttachs, name='saveTAttachs'),
    url(r'SaveDropAttachment', views.saveDropAttachment, name='saveDropAttachment'),
    url(r'Home_DeleteAttach', views.deleteAttach, name='deleteAttach'),
    url(r'getLatesAttachementByTicketId', views.getLatesAttachementByTicketId, name='getLatesAttachementByTicketId'),
    url(r'deleteAttachementByAttachId', views.deleteAttachementByAttachId, name='deleteAttachementByAttachId'),
    url(r'^editNoteTicket', views.editNoteTicket, name='editNoteTicket'),
    url(r'Home_UpdateNoteTicket', views.updateNoteTicket, name='updateNoteTicket'),
    url(r'^deleteNoteTicket', views.deleteNoteTicket, name='deleteNoteTicket'),
    url(r'DashboardSettings', views.dashboardSettings, name='dashboardSettings'),
    url('systemOverview', views.systemOverview, name='systemOverview'),
    url('openTicketsByTicketType', views.openTicketsByTicketType, name='openTicketsByTicketType'),
    url('openTicketsBySubtype', views.openTicketsBySubtype, name='openTicketsBySubtype'),
    url('openTicketsBySubstatus', views.openTicketsBySubstatus, name='openTicketsBySubstatus'),
    url('openTicketsByPriority', views.openTicketsByPriority, name='openTicketsByPriority'),
    url('openTicketsByOrganization', views.openTicketsByOrganization, name='openTicketsByOrganization'),
    url('openTicketsByAccount', views.openTicketsByAccount, name='openTicketsByAccount'),
    url('openTicketsByAssignee', views.openTicketsByAssignee, name='openTicketsByAssignee'),
    url('monthlyPerformance', views.monthlyPerformance, name='monthlyPerformance'),
    url('openTicketsByNextAction', views.openTicketsByNextAction, name='openTicketsByNextAction'),
    url('currentQtrPerformance', views.currentQtrPerformance, name='currentQtrPerformance'),
    url('availableTasksByAssignee', views.availableTasksByAssignee, name='availableTasksByAssignee'),
    url('openTasksByAssignee', views.openTasksByAssignee, name='openTasksByAssignee'),
    url('openTicketsByDeptAssigned', views.openTicketsByDeptAssigned, name='openTicketsByDeptAssigned'),
    url('openTicketsByDeptSubmitting', views.openTicketsByDeptSubmitting, name='openTicketsByDeptSubmitting'),
    url('saveDashboardPanel', views.saveDashboardPanel, name='saveDashboardPanel'),
    url('mySettings', views.mySettings, name='mySettings'),
    url('saveMySettings', views.saveMySettings, name='saveMySettings'),
    url('changePassword', views.changePassword, name='changePassword'),
    url('PasswordChange', views.PasswordChange, name='PasswordChange'),
    url(r'^cloneTicket', views.cloneTicket, name='cloneTicket'),
    url(r'^ticketLookUp', views.ticketLookUp, name='ticketLookUp'),
    url(r'^saveModalTaskManagerByTicketId/$', views.saveModalTaskManagerByTicketId, name='saveModalTaskManagerByTicketId'),
    url(r'^getTaskManagerByTicketId/$', views.getTaskManagerByTicketId, name='getTaskManagerByTicketId'),
    url(r'^updateTicketSubstatusById/$', views.updateTicketSubstatusById, name='updateTicketSubstatusById'),
    url(r'^updateTicketStatusById/$', views.updateTicketStatusById, name='updateTicketStatusById'),
    url(r'^clearNullTicketTasks/$', views.clearNullTicketTasks, name='clearNullTicketTasks'),
    url(r'^setTicketNotesByLaborNoteId/$', views.setTicketNotesByLaborNoteId, name='setTicketNotesByLaborNoteId'),
    url(r'^editDescTicket', views.editDescTicket, name='editDescTicket'),
    url(r'Home_UpdateDescTicket', views.updateDescTicket, name='updateDescTicket'),
    url(r'deleteLaborTicketNoteById', views.deleteLaborTicketNoteById, name='deleteLaborTicketNoteById'),
    url(r'savePhoneNumber', views.savePhoneNumber, name='savePhoneNumber'),
    
    

    # My ATG URLs End


    # Submit Ticket URLs Start
    url(r'Home_SubmitTicket', views.submitTicket, name='submitTicket'),
    url(r'^getClientInformationById/$', views.getClientInformationById, name='getClientInformationById'),
    url(r'^getTicketTypeChildById/$', views.getTicketTypeChildById, name='getTicketTypeChildById'),
    url(r'^getClientId/$', views.getClientId, name='getClientId'),
    url(r'^getUsersByOrgId/$', views.getUsersByOrgId, name='getUsersByOrgId'),
    url(r'^getModalOrgDetailById/$', views.getModalOrgDetailById, name='getModalOrgDetailById'),
    url(r'^getModalOrgHistoryById/$', views.getModalOrgHistoryById, name='getModalOrgHistoryById'),
    url(r'^getModalCallerDetailById/$', views.getModalCallerDetailById, name='getModalCallerDetailById'),
    url(r'^getModalCallerHistoryById/$', views.getModalCallerHistoryById, name='getModalCallerHistoryById'),
    url(r'^getModalAccountDetailById/$', views.getModalAccountDetailById, name='getModalAccountDetailById'),
    url(r'^getModalAccountHistoryById/$', views.getModalAccountHistoryById, name='getModalAccountHistoryById'),
    url(r'^getModalTaskManagerById/$', views.getModalTaskManagerById, name='getModalTaskManagerById'),
    url(r'^getTableTaskManagerById/$', views.getTableTaskManagerById, name='getTableTaskManagerById'),


    # Submit Ticket URLs End


    # Search Ticket URLs Start
    url(r'Home_SearchTicket', views.searchTicket, name='searchTicket'),
    url(r'Home_TicketsSearchList', views.ticketSearchResults, name='ticketSearchResults'),
    url(r'Home_SaveSearchTicket', views.ticketSaveSearch, name='ticketSaveSearch'),
    url(r'Home_UpdateSavedSearchTicket', views.ticketUpdateSavedSearch, name='ticketUpdateSavedSearch'),
    url(r'^deleteSavedSearch/$', views.deleteSavedSearch, name='deleteSavedSearch'),
    url(r'copySavedSearch', views.copySavedSearch, name='copySavedSearch'),
    url(r'^export_tickets_xls/$', views.export_tickets_xls, name='export_tickets_xls'),

    url(r'Home_ticketSearchStatsList', views.ticketSearchStatsList, name='ticketSearchStatsList'),


    # Search Ticket URLs End


    # Reports URLs Start
    url(r'Home_GetSavedReports', views.savedSearches, name='savedSearches'),
    url(r'Home_saveSearchProcess', views.saveSearchProcess, name='saveSearchProcess'),
    url(r'^savedSearchRemove/$', views.savedSearchRemove, name='savedSearchRemove'),
    url(r'^savedSearchRemove2/$', views.savedSearchRemove2, name='savedSearchRemove2'),
    url(r'Home_GetSummaryReports', views.summaryReports, name='summaryReports'),
    url(r'Home_getReportDateRange', views.getReportDateRange, name='getReportDateRange'),
    url(r'Home_getSummaryReportResults', views.summaryReportResults, name='summaryReportResults'),
    url(r'Home_getSummaryReportTicketList', views.getSummaryReportTicketList, name='getSummaryReportTicketList'),
    url(r'Home_GetReportWriter', views.reportWriterQueries, name='reportWriterQueries'),
    url(r'Home_NewQuery', views.newQuery, name='newQuery'),
    url(r'getPairSelectedFields', views.getPairSelectedFields, name='getPairSelectedFields'),
    url(r'getPairFields', views.getPairFields, name='getPairFields'),
    url(r'Query2', views.secondQuery, name='secondQuery'),
    url(r'getFieldsConditions', views.getFieldsConditions, name='getFieldsConditions'),
    url(r'setSelectedFields', views.setSelectedFields, name='setSelectedFields'),
    url(r'Query3', views.thirdQuery, name='thirdQuery'),
    url(r'setFilters', views.setFilters, name='setFilters'),
    url(r'saveFinalNewQuery', views.saveFinalNewQuery, name='saveFinalNewQuery'),
    url(r'Home_qbQueryProcess', views.qbQueryProcess, name='qbQueryProcess'),
    url(r'Home_EditQueryStep1', views.editQueryStep1, name='editQueryStep1'),
    url(r'Home_EditQueryStep2', views.editQueryStep2, name='editQueryStep2'),
    url(r'Home_EditQueryStep3', views.editQueryStep3, name='editQueryStep3'),
    url(r'updateFinalNewQuery', views.updateFinalNewQuery, name='updateFinalNewQuery'),
    url(r'^deleteQBQuery/$', views.deleteQBQuery, name='deleteQBQuery'),
    url(r'^deleteRBQuery/$', views.deleteRBQuery, name='deleteRBQuery'),
    url(r'^cloneQBQuery/$', views.cloneQBQuery, name='cloneQBQuery'),
    url(r'^cloneRBQuery/$', views.cloneRBQuery, name='cloneRBQuery'),
    url(r'^Home_ReportWriterSettings/$', views.reportWriterSettings, name='reportWriterSettings'),
    url(r'^Home_UpdateReportSettings/$', views.updateReportSettings, name='updateReportSettings'),
    url(r'getModalReportDataSet', views.getModalReportDataSet, name='getModalReportDataSet'),
    url(r'getQueryDescriptionById', views.getQueryDescriptionById, name='getQueryDescriptionById'),
    url(r'getModalQueryDef', views.getModalQueryDef, name='getModalQueryDef'),
    url(r'getModalReportDef', views.getModalReportDef, name='getModalReportDef'),
    url(r'Home_reportWriterReports', views.reportWriterReports, name='reportWriterReports'),
    url(r'Home_NewReport', views.newReport, name='newReport'),
    url(r'getQueryFields', views.getQueryFields, name='getQueryFields'),
    url(r'Home_Step2NewReport', views.secondReport, name='secondReport'),
    url(r'getQuerySelectedFields', views.getQuerySelectedFields, name='getQuerySelectedFields'),
    url(r'setReportQuerySelectedFields', views.setReportQuerySelectedFields, name='setReportQuerySelectedFields'),
    url(r'Home_Step3NewReport', views.thirdReport, name='thirdReport'),
    url(r'setReportGroupSelectedFields', views.setReportGroupSelectedFields, name='setReportGroupSelectedFields'),
    url(r'Home_Step4NewReport', views.fourthReport, name='fourthReport'),
    url(r'setReportSortOrderVal', views.setReportSortOrderVal, name='setReportSortOrderVal'),
    url(r'setSavedSortExpression', views.setSavedSortExpression, name='setSavedSortExpression'),
    url(r'Home_Step5NewReport', views.fifthReport, name='fifthReport'),
    url(r'setSavedFormatExpression', views.setSavedFormatExpression, name='setSavedFormatExpression'),
    url(r'Home_Step6NewReport', views.sixthReport, name='sixthReport'),
    url(r'saveFinalNewReport', views.saveFinalNewReport, name='saveFinalNewReport'),
    url(r'Home_rbReportProcess', views.rbReportProcess, name='rbReportProcess'),
    url(r'getReportDescriptionById', views.getReportDescriptionById, name='getReportDescriptionById'),
    url(r'Home_addScheduledReport', views.addScheduledReport, name='addScheduledReport'),
    url(r'getReportsByReportType', views.getReportsByReportType, name='getReportsByReportType'),
    url(r'saveScheduleReport', views.saveScheduleReport, name='saveScheduleReport'),
    url(r'Home_listScheduledReport', views.lsitScheduleReport, name='lsitScheduleReport'),
    path(r'Home_ScheduledReportDel', views.DelScheduleReport, name='deleteSch'),
    path(r'Home_ScheduledReportEdit', views.editScheduleReport, name='editSch'),
    path(r'Home_ScheduledReportUpdate', views.updateScheduledReport, name='updateSch'),
    url(r'Home_ScheduledReportRecpientAdd', views.addScheduledReportRecpient, name='saveSchRepRes'),
    url(r'Home_ScheduledReportRecpientdel', views.delScheduledReportRecpient, name='deleterepSch'),
    url(r'Home_editReportStep1', views.editReportStep1, name='editReportStep1'),
    url(r'Home_editReportStep2', views.editReportStep2, name='editReportStep2'),
    url(r'Home_editReportStep3', views.editReportStep3, name='editReportStep3'),
    url(r'Home_editReportStep4', views.editReportStep4, name='editReportStep4'),
    url(r'Home_editReportStep5', views.editReportStep5, name='editReportStep5'),
    url(r'Home_editReportStep6', views.editReportStep6, name='editReportStep6'),
    url(r'Home_updateFinalReport', views.updateFinalReport, name='updateFinalReport'),
    url(r'^ScheduleRepListDatatable/data/$', login_required(ScheduleRptListJson.as_view()), name='sch_list_json'),
    url(r'^export_rb_query_Report_xls/$', views.export_rb_query_Report_xls, name='export_rb_query_Report_xls'),
    url(r'^export_rb_report_Report_xls/$', views.export_rb_report_Report_xls, name='export_rb_report_Report_xls'),
    url(r'^isSaveSearchShareable/$', views.isSaveSearchShareable, name='isSaveSearchShareable'), 
    # Reports Ticket URLs End

    # Unassigened Tickets URLs Start
    url(r'Home_UnassignedTickets', views.unassignedTickets, name='unassignedTickets'),
    url(r'save_UnassignedTickets', views.save_UnassignedTickets, name='save_UnassignedTickets'),
    url(r'assignTicketToSelf', views.assignTicketToSelf, name='assignTicketToSelf'),
    url(r'ConfigureSubmitTicketFields', views.ConfigureSubmitTicketFields, name='ConfigureSubmitTicketFields'),


    # Unassigened Tickets Ticket URLs End

    # Email Notifications Ticket URLs Start

    url(r'Home_EmailNotification', views.tickets, name='tickets'),
    url(r'ticketsListAll', views.ticketsListAll, name='ticketsListAll'),
    url(r'getModalActionDetailById', views.getModalActionDetailById, name='getModalActionDetailById'),
    url(r'updateTicketsEmailPermission', views.updateTicketsEmailPermission, name='updateTicketsEmailPermission'),
    url(r'ticketsDefaultDistribution', views.ticketsDefaultDistribution, name='ticketsDefaultDistribution'),
    url(r'Admin_editEmailMobileNotifications', views.editEmailMobileNotifications, name='editEmailMobileNotifications'),
    url(r'Admin_updateEmailMobileNotifications', views.updateEmailMobileNotifications, name='updateEmailMobileNotifications'),
    url(r'Admin_deleteEmailMobileNotifications', views.deleteEmailMobileNotifications, name='deleteEmailMobileNotifications'),
    url(r'Admin_tasksEmail', views.tasks, name='tasks'),
    url(r'Admin_tasksDefaultDistribution', views.tasksDefaultDistribution, name='tasksDefaultDistribution'),
    url(r'getModalTaskEmailPermissionsByID', views.getModalTaskEmailPermissionsByID, name='getModalTaskEmailPermissionsByID'),
    url(r'updateTasksEmailPermission', views.updateTasksEmailPermission, name='updateTasksEmailPermission'),
    url('AddCustomMessages', views.addCustomMessages, name='addCustomMessages'),
    url(r'ShowCustomMessages', views.showCustomMessages, name='showCustomMessages'),
    url(r'SaveCustomMessages', views.saveCustomMessages, name='saveCustomMessages'),
    
    # Email Notifications URLs End

    # System Notifications Ticket URLs Start

    url(r'Admin_HoursOfOperation', views.addHoursOfOperation, name='addHoursOfOperation'),
    url(r'Admin_SaveHoursOfOperation', views.saveHoursOfOperation, name='saveHoursOfOperation'),
    url(r'Admin_SaveDatesClosed', views.saveDatesClosed, name='saveDatesClosed'),
    url(r'Admin_addSiteAppearance', views.addSiteAppearance, name='addSystemSettings'),
    url(r'Admin_SaveSiteAppearance', views.saveSiteAppearance, name='saveSiteAppearance'),
    url(r'Admin_SaveFiles', views.saveSiteAppearanceFiles, name='saveSiteAppearanceFiles'),
    url(r'Admin_addEmailSettings', views.addEmailSettings, name='addEmailSettings'),
    url(r'Admin_saveEmailSettings', views.saveEmailSettings, name='saveEmailSettings'),
    url(r'Admin_viewEmailLogs', views.viewEmailLogs, name='viewEmailLog'),
    url(r'^EmailListdatatable/data/$', login_required(EmailsListJson.as_view()), name='email_list_json'),
    path(r'Admin_EmailBody', views.viewEmailBody, name='viewEmailBody'),
    url(r'^HoursOfOperationListdatatable/data/$', login_required(HoursOfOperationListJson.as_view()), name='hoursofoperation_list_json'),
    url(r'Admin_removeFaviconAppearance', views.removeFaviconSiteAppearance, name='removeFaviconSiteAppearance'),
    url(r'Admin_removeLeftLogoSiteAppearance', views.removeLeftLogoSiteAppearance, name='removeLeftLogoSiteAppearance'),
    url(r'Admin_removeRightLogoSiteAppearance', views.removeRightLogoSiteAppearance, name='removeRightLogoSiteAppearance'),
    # url(r'Admin_SaveHistoryHoursOfOperation', views.saveHistoryHoursOfOperation, name='saveHistoryHoursOfOperation'),
    path(r'smtpConnectionTest', views.smtpConnectionTest, name='smtpConnectionTest'),
    url(r'Admin_deleteDatesClosed', views.deleteDatesClosed, name='deleteDatesClosed'),

    
    # System Notifications Ticket URLs End


    # Business Rules URLs Start
     url(r'Admin_BusinessRulesAdd', views.addBusinessRules, name='addBusinessRules'),
     url(r'Admin_BusinessRulesSave', views.saveBusinessRules, name='saveBusinessRules'),
     url(r'Admin_BusinessRulesList', views.listBusinessRules, name='listBusinessRules'),
     url(r'^BusinessRulesListdatatable/data/$', login_required(BusinessRulesListJson.as_view()), name='business_rules_json'),
     path(r'Admin_BusinessRulesEdit', views.editBusinessRules, name='editBusinessRules'),
     path(r'Admin_BusinessRulesDel', views.deleteBusinessRules, name='deleteBusinessRules'),
     path('Admin_BusinessRulesUpdate', views.updateBusinessRules, name='updateBusinessRules'),
     url(r'Admin_BusinessRulesPrecedence', views.precedenceBusinessRules, name='precedenceBusinessRules'),
     url(r'Admin_PrecedenceBusinessRulesSave', views.savePrecedenceBusinessRules, name='savePrecedenceBusinessRules'),
     url(r'Admin_BusinessRulesSubstatus', views.substatusBusinessRules, name='substatusBusinessRules'),
     url(r'Admin_SubstatusBusinessRulesSave', views.saveSubstatusBusinessRules, name='saveSubstatusBusinessRules'),
     url(r'Admin_SubstatusBusinessRulesEdit', views.editSubstatusBusinessRules, name='editSubstatusBusinessRules'),
     path('Admin_SubstatusBusinessRulesUpdate', views.updateSubstatusBusinessRules, name='updateSubstatusBusinessRules'),
     url(r'Admin_SubstatusBusinessRulesDelete', views.deleteSubstatusBusinessRules, name='deleteSubstatusBusinessRules'),
     url(r'Admin_PauseClockBusinessRulesSave', views.savePauseClockBusinessRules, name='savePauseClockBusinessRules'),
     url(r'Admin_PauseClockBusinessRulesDelete', views.deletePauseClockBusinessRules, name='deletePauseClockBusinessRules'),
     path('Admin_BusinessRulesAutoAssignment', views.autoAssignmentBusinessRules, name='autoAssignmentBusinessRules'),
     url(r'Admin_EscalationRulesAdd', views.addEscalationRules, name='addEscalationRules'),
     url(r'Admin_EscalationRulesSave', views.saveEscalationRules, name='saveEscalationRules'),
     url(r'Admin_EscalationRulesList', views.listEscalationRules, name='listEscalationRules'),
    url(r'^getEscalationRulesListJson/$', views.getEscalationRulesListJson, name='getEscalationRulesListJson'),
    path(r'Admin_EscalationRulesEdit', views.editEscalationRules, name='editEscalationRules'),
    path('Admin_EscalationRulesUpdate', views.updateEscalationRules, name='updateEscalationRules'),
    path('Admin_EscalationRulesDelete', views.deleteEscalationRules, name='deleteEscalationRules'),
    path('runEscalationRules', views.runEscalationRules, name='runEscalationRules'),
    # Business Rules URLs End

    # System Notifications Ticket URLs Start
    # Mailbox Ticket URLs Start

    url(r'Admin_addIEmMailboxes', views.addIEmMailboxes, name='addIEmMailboxes'),
    url(r'Admin_saveMailBox', views.saveMailBox, name='saveMailBox'),
    url(r'Admin_addUserTemplate', views.addUserTemplate, name='addUserTemplate'),
    url(r'Admin_saveUserTemplateModal', views.saveUserTemplateModal, name='saveUserTemplateModal'),
    url('runMailBox', views.runMailBox, name='runMailBox'),
    url(r'createUserFromTemplate', views.createUserFromTemplate, name='createUserFromTemplate'),
    url(r'createUserFromOrganization', views.createUserFromOrganization, name='createUserFromOrganization'),
    path(r'testConnectionMailBox', views.testConnectionMailBox, name='testConnectionMailBox'),
    path('Admin_MailBoxList', views.listMailBox, name='listMailBox'),
    url(r'^mailBoxListDatatable/data/$', login_required(MailBoxListJson.as_view()), name='mail_box_list_json'),
    path(r'Admin_MailBoxEdit', views.editMailBox, name='editMailBox'),
    path('Admin_MailBoxUpdate', views.updateMailBox, name='updateMailBox'),
    path(r'Admin_MailBoxDel', views.deleteMailBox, name='deleteMailBox'),
    url(r'Admin_addExcludeText', views.addExcludeText, name='addExcludeText'),
    url(r'Admin_listExcludeText', views.listExcludeText, name='listExcludeText'),
    url(r'Admin_saveExcludeText', views.saveExcludeText, name='saveExcludeText'),
    url(r'^ExcludeTextDataTable/data/$', login_required(ExcludeTextJSON.as_view()), name='exclude_text_list_json'),
    path(r'Admin_ExcludeTextEdit', views.excludeTextEdit, name='excludeTextEdit'),
    path('Admin_ExcludeTextUpdate', views.excludeTextUpdate, name='excludeTextUpdate'),
    path(r'Admin_ExcludeTextDel', views.excludeTextDel, name='excludeTextDel'),
    url(r'Admin_addKeywords', views.addKeywords, name='addKeywords'),
    url(r'Admin_listKeywords', views.listKeywords, name='listKeywords'),
    url(r'Admin_saveKeywords', views.saveKeywords, name='saveKeywords'),
    url(r'^KeywordsDataTable/data/$', login_required(KeywordsJSON.as_view()), name='keywords_list_json'),
    path(r'Admin_KeywordsEdit', views.keywordsEdit, name='keywordsEdit'),
    path('Admin_KeywordsUpdate', views.keywordsUpdate, name='keywordsUpdate'),
    path(r'Admin_KeywordsDel', views.keywordsDel, name='keywordsDel'),
    url(r'Admin_EmailTokens', views.emailTokens, name='emailTokens'),
    url(r'getModalCommadToken', views.getModalCommadToken, name='getModalCommadToken'),
    url(r'updateCommandToken', views.updateCommandToken, name='updateCommandToken'),
    url(r'getModalFieldToken', views.getModalFieldToken, name='getModalFieldToken'),
    url(r'updateFieldToken', views.updateFieldToken, name='updateFieldToken'),
    url(r'Admin_SaveFieldToken', views.saveFieldToken, name='saveFieldToken'),
    path(r'Admin_FieldTokenDel', views.deleteFieldToken, name='deleteFieldToken'),
    url(r'Admin_BlockedAttachments', views.blockedAttachments, name='blockedAttachments'),
    url(r'getModalAttachment', views.getModalAttachment, name='getModalAttachment'),
    url(r'Admin_SaveBlockedAttachemts', views.saveBlockedAttachemts, name='saveBlockedAttachemts'),
    url(r'^BlockedAttachmentsDataTable/data/$', login_required(BlockedAttachmentsJSON.as_view()), name='blocked_attachments_list_json'),
    path(r'Admin_blockedAttachmentsDel', views.deleteBlockedAttachments, name='deleteBlockedAttachments'),
    url(r'Admin_ViewLog', views.viewLog, name='viewLog'),
    path(r'Admin_getviewLogBody', views.viewLogBody, name='viewLogBody'),
    url(r'^MailBoxEmailViewLogDataTable/data/$', login_required(MailBoxEmailViewLogJSON.as_view()), name='view_log_list_json'),
    url(r'Admin_GetAllViewLogData', views.getAllViewLogData, name='getAllViewLogData'),
    # Mailbox Ticket URLs End

    # Account URLs Start
    url(r'Admin_AccounAtdd', views.addAccount, name='addAccount'),
    url(r'Admin_AccountSave', views.saveAccount, name='saveAccount'),
    url(r'Admin_AccountList', views.listAccount, name='listAccount'),
    url(r'^getAccountListJson/$', views.getAccountListJson, name='getAccountListJson'), 
    # Account URLs End

    # Iorad URLs Start
    url(r'Admin_ListIoradTutorials', views.listIoradTutorials, name='listIoradTutorials'),
    url(r'^getIoradTutorials/$', views.getIoradTutorials, name='getIoradTutorials'),
    url(r'^openAddIoradModal/$', views.openAddIoradModal, name='openAddIoradModal'),
    url(r'^saveIorad/$', views.saveIorad, name='saveIorad'),
    url(r'^openEditIoradModal/$', views.openEditIoradModal, name='openEditIoradModal'),
    url(r'^updateIorad/$', views.updateIorad, name='updateIorad'),
    url(r'^openDelIoradModal/$', views.openDelIoradModal, name='openDelIoradModal'),
    url(r'^deleteIorad/$', views.deleteIorad, name='deleteIorad'),
    url(r'^viewIorad/$', views.viewIorad, name='viewIorad'),
    url(r'^backwardIoradTutorial/$', views.backwardIoradTutorial, name='backwardIoradTutorial'),
    url(r'^forwardIoradTutorial/$', views.forwardIoradTutorial, name='forwardIoradTutorial'),
    url(r'^IoradTutorials/$', views.IoradTutorials, name='IoradTutorials'),
    # Iorad URLs End

    #Open Tickets by clients graph
    url('openTicketsByClients', views.openTicketsByClients, name='openTicketsByClients'),
    #Open Tickets by countyr graph
    url('openTicketsByCountry', views.openTicketsByCountry, name='openTicketsByCountry'),

    #Test URLS
    # url(r'Admin_test', views.getGrandParentTicketType, name='getGrandParentTicketType'),
    url('orgUserExists', views.orgUserExists, name='orgUserExists'),
    url('getDepartment', views.getDepartment, name='getDepartment'),
    url('getOrg', views.getOrg, name='getOrg'),

    url(r'Cron_RunDailyScheduleJob', views.runDailyScheduleJob, name='runDailyScheduleJob'),
]
handler404 = 'myapp.views.error_404'