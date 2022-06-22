from django.shortcuts import render, redirect
from django.template.loader import render_to_string 
from django.contrib.auth.decorators import login_required, user_passes_test
from itrak.models import *
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from django.db.models.query import QuerySet
from itertools import chain
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz
import json
from django.db.models import Case, F, FloatField, IntegerField, Sum, When, Count
from django.db.models.functions import Cast
from django.core import serializers
from django.conf import settings
from django.core import signing
from django import template
from django.core import signing
from django.db.models import F
from datetime import datetime, timezone, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, NamedStyle
from openpyxl.utils import get_column_letter
import json
from html.parser import HTMLParser
from django.core.mail import send_mail
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from itrak.views.Load import *

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
#SMTP Settings start#

def getSMTPSettings(ID):
    smtpSetting = EmailSettings.objects.get(pk = ID)
    smtpArray = {}
    smtpArray["email_server"] = smtpSetting.email_server
    smtpArray["port"] = smtpSetting.port
    smtpArray["user_name"] = smtpSetting.user_name
    smtpArray["password"] = smtpSetting.password
    smtpArray["email_sender_name"] = smtpSetting.email_sender_name
    return smtpArray

#SMTP Settings end#  

# Send Email Request Start#
def send_email(to='' ,subject='', message='',cc = '', bcc = '', fail_silently=False, event_name="", action_item=""):
    smtp = getSMTPSettings(1)
    smtpserver = smtplib.SMTP(smtp['email_server'], smtp['port'])
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(smtp["user_name"], smtp["password"]) 
    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['From'] = smtp["email_sender_name"]
    msg['To'] = ','.join(to)
    msg['Cc'] = cc
    msg['Bcc'] = bcc
    smtpserver.sendmail(smtp["user_name"], to, msg.as_string())  # you just need to add
    smtpserver.close()

    # Save Email Log
    obj = EmailLog(
        to=to,
        cc=cc,
        bcc=bcc,
        subject=subject,
        body=message,
        event_name=event_name,
        action_item=action_item
    )
    obj.save()

# Send Email Request End#

def sendTicketEmail(user_id,ticket_id,ticket_action_slug,ticket_role_slug,event_id):
    user = User.objects.get(id=user_id)
    t_action_id = TicketsActions.objects.get(t_action_slug=ticket_action_slug).t_action_id
    t_role_id = TicketsRoles.objects.get(t_role_slug=ticket_role_slug).t_role_id
    check = TicketsEmailNotificationPermissions.objects.filter(t_email_action_id=t_action_id,t_email_role_id=t_role_id).exists()
    if(check):
        print(ticket_action_slug)
        print(ticket_role_slug)
        to = []
        to.append(user.email)
        is_exist = CustomMessage.objects.filter(cm_event_id=event_id).exists()
        if is_exist == True:
            subject = getSubjectReplaceText(event_id,'updated','ticket',ticket_id)
            message = getMessageReplaceText(event_id,'updated','ticket',ticket_id)
        else:
            subject = getSubjectReplaceText(event_id,'default','ticket',ticket_id)
            message = getMessageReplaceText(event_id,'default','ticket',ticket_id)
        # For Custom Messages End #
        send_email(to=to, subject=subject, message=message, event_name=ticket_action_slug, action_item="Ticket")
        return

def sendTaskEmail(user_id,task_id,task_action_slug,task_role_slug,event_id):

    user = User.objects.get(id=user_id)
    task_action_id = TasksAction.objects.get(task_action_slug=task_action_slug).task_action_id
    task_role_id = TasksRole.objects.get(task_role_slug=task_role_slug).task_role_id
    check = TasksEmailNotificationPermission.objects.filter(t_email_action_id=task_action_id,t_email_role_id=task_role_id).exists()
    if(check):
        print(task_action_slug)
        print(task_role_slug)
        to = []
        to.append(user.email)           
        is_exist = CustomMessage.objects.filter(cm_event_id=event_id).exists()
        if is_exist == True:
            subject = getSubjectReplaceText(event_id,'updated','task',task_id)
            message = getMessageReplaceText(event_id,'updated','task',task_id)
        else:
            subject = getSubjectReplaceText(event_id,'default','task',task_id)
            message = getMessageReplaceText(event_id,'default','task',task_id)
        send_email(to=to, subject=subject, message=message, event_name=task_action_slug, action_item="Task")
        return

# check User Permission for Sub Action
def getUserPermissionsList(action_slug='', org_id=0, client_id=0, dep_id=0, priority_id = 0, dynamicUserID=0):
    allUsers = []
    # check Organization Users Permissions
    orgAct = OrganizationAction.objects.get(org_action_slug = action_slug)
    orgUsers = OrganizationEmailNotificationUserPermission.objects.filter(org_id = org_id, action_id = orgAct.org_action_id)
    for user in orgUsers:
        if user.user_id not in allUsers:
            allUsers.append(user.user_id)
    
    # check client Users Permissions
    cliAct = ClientAction.objects.get(cli_action_slug = action_slug)
    clientUsers = ClientEmailNotificationUserPermission.objects.filter(client_id = client_id, action_id = cliAct.cli_action_id)
    for user in clientUsers:
        if user.user_id not in allUsers: 
            allUsers.append(user.user_id)
    
    # check department Users Permissions
    depAct = DepartmentAction.objects.get(dep_action_slug = action_slug)
    departmentUsers = DepartmentEmailNotificationUserPermission.objects.filter(dep_id = dep_id, action_id = depAct.dep_action_id)
    for user in departmentUsers:
        if user.user_id not in allUsers: 
            allUsers.append(user.user_id)

    # check Priority Users Permissions
    priAct = PriorityAction.objects.get(pri_action_slug = action_slug)
    priorityUsers = PriorityEmailNotificationUserPermission.objects.filter(priority_id = priority_id, action_id = priAct.pri_action_id)
    for user in priorityUsers:
        if user.user_id not in allUsers: 
            allUsers.append(user.user_id)

    if dynamicUserID and int(dynamicUserID) >  0:
        allUsers.append(dynamicUserID)
    allUsers = list(dict.fromkeys(allUsers))
    return allUsers


#Custom Messages Replace Subject Text start#
def getSubjectReplaceText(event,value,ttype,id):
    
    if value == 'updated':
        Subject= json.loads(CustomMessage.objects.values_list('cm_subject', flat=True).get(cm_event_id=event))
    else:
        Subject= json.loads(CustomMessagesEvent.objects.values_list('cme_subject_slug', flat=True).get(cme_id=event))
    
    if ttype == 'ticket':
        ticket = Ticket.objects.get(pk=id)     

        CustomerID = "ATG Extra"
        Organization = "ATG Extra Organization"
        IssueLabel = "Ticket"
        IssueLabelPlural = "Tickets"
        SpecFunc1 = "Record Locator: 123456-A"
        SpecFunc2 = "Caller Name: 123456-B"
        SpecFunc3 = "Caller Phone: 123456-C"
        SpecFunc4 = "Caller Email: 123456-D"
        SpecFunc5 = "Passenger Name: 123456-E"
        TaskDesc = "Has Ink Cartridge Been Replaced?"
        TaskDueDate = "01/01/2000"
        TaskAssignee = "Doe, Jane"
        TaskCompleter = "Doe, John"
        TaskResponse = "Yes"

        # for subject textarea
        Subject = Subject.replace("<@CustomerID>", CustomerID)
        Subject = Subject.replace("<@IssueNbr>", str(ticket.ticket_id))
        Subject = Subject.replace("<@IssueSubj>", str(ticket.subject))
        Subject = Subject.replace("<@Organization>", Organization)
        Subject = Subject.replace("<@IssueLabel>", IssueLabel)
        Subject = Subject.replace("<@IssueLabelPlural>", IssueLabelPlural)
        Subject = Subject.replace("<@SpecFunc1>", SpecFunc1)
        Subject = Subject.replace("<@SpecFunc2>", SpecFunc2)
        Subject = Subject.replace("<@SpecFunc3>", SpecFunc3)
        Subject = Subject.replace("<@SpecFunc4>", SpecFunc4)
        Subject = Subject.replace("<@SpecFunc5>", SpecFunc5)
        Subject = Subject.replace("<@TaskDesc>", TaskDesc)
        Subject = Subject.replace("<@TaskDueDate>", TaskDueDate)
        Subject = Subject.replace("<@TaskAssignee>", TaskAssignee)
        Subject = Subject.replace("<@TaskCompleter>", TaskCompleter)
        Subject = Subject.replace("<@TaskResponse>", TaskResponse)
        Subject = Subject.replace("<@CalEventNbr>", "")
        Subject = Subject.replace("<@CalEventDesc>", "")
        Subject = Subject.replace("<@CalEventDate>", "")
        Subject = Subject.replace("<@CalEventTime>", "")

    if ttype == 'task':
        task = TaskManager.objects.get(pk = id)     
        ticket = Ticket.objects.get(pk = task.tmgr_ticket_id)
        # For encryption id
        encrypted_id = signing.dumps(ticket.ticket_id, salt=settings.SALT_KEY)
        # For Ticket Status
        if ticket.ticket_status == '1':
            status = 'Closed'
        else:     
            status = 'Open'
        # For Task Assigne
        taskassignee = User.objects.values_list('display_name', flat=True).filter(pk=task.task_assigned_to_id)
        
        CustomerID = "ATG Extra"
        Organization = "ATG Extra Organization"
        IssueLabel = "Ticket"
        IssueLabelPlural = "Tickets"
        SpecFunc1 = "Record Locator: 123456-A"
        SpecFunc2 = "Caller Name: 123456-B"
        SpecFunc3 = "Caller Phone: 123456-C"
        SpecFunc4 = "Caller Email: 123456-D"
        SpecFunc5 = "Passenger Name: 123456-E"
        TaskDesc = "Has Ink Cartridge Been Replaced?"
        TaskDueDate = "01/01/2000"
        TaskAssignee = "Doe, Jane"
        TaskCompleter = "Doe, John"
        TaskResponse = "Yes"

        # for subject textarea
        Subject = Subject.replace("<@CustomerID>", CustomerID)
        Subject = Subject.replace("<@IssueNbr>", str(ticket.ticket_id))
        Subject = Subject.replace("<@IssueSubj>", str(ticket.subject))
        Subject = Subject.replace("<@Organization>", Organization)
        Subject = Subject.replace("<@IssueLabel>", IssueLabel)
        Subject = Subject.replace("<@IssueLabelPlural>", IssueLabelPlural)
        Subject = Subject.replace("<@SpecFunc1>", SpecFunc1)
        Subject = Subject.replace("<@SpecFunc2>", SpecFunc2)
        Subject = Subject.replace("<@SpecFunc3>", SpecFunc3)
        Subject = Subject.replace("<@SpecFunc4>", SpecFunc4)
        Subject = Subject.replace("<@SpecFunc5>", SpecFunc5)
        Subject = Subject.replace("<@TaskDesc>", str(task.task_note))
        Subject = Subject.replace("<@TaskDueDate>", str(task.task_due_date))
        Subject = Subject.replace("<@TaskAssignee>", str(taskassignee))
        Subject = Subject.replace("<@TaskCompleter>", str(taskassignee))
        Subject = Subject.replace("<@TaskResponse>", TaskResponse)
        Subject = Subject.replace("<@CalEventNbr>", "")
        Subject = Subject.replace("<@CalEventDesc>", "")
        Subject = Subject.replace("<@CalEventDate>", "")
        Subject = Subject.replace("<@CalEventTime>", "")    
        
    return Subject
#Custom Messages Replace Subject Text end# 

#Custom Messages Replace Message Text start#
def getMessageReplaceText(event,value,ttype,id):
    if value == 'updated':
        Message= CustomMessage.objects.values_list('cm_message', flat=True).get(cm_event_id=event)
    else:
        Message= CustomMessagesEvent.objects.values_list('cme_message_slug', flat=True).get(cme_id=event)

    if ttype == 'ticket':
        ticket = Ticket.objects.get(pk=id)
        # For encryption id 
        encrypted_id = signing.dumps(ticket.ticket_id, salt=settings.SALT_KEY)
        # For Ticket Status
        if ticket.ticket_status == '1':
            status = 'Closed'
        else:     
            status = 'Open'
        # For Ticket ticketnotes  
        ticketnotes = TicketNote.objects.filter(note_ticket_id=id).filter(note_is_delete=0).values_list('note_detail')
        list_ticketnotes=""
        for ticketnote in ticketnotes:
            list_ticketnotes += str(ticketnote)

        list_ticketnotes=list_ticketnotes.replace(")", "")
        list_ticketnotes=list_ticketnotes.replace("(", "")
        list_ticketnotes=list_ticketnotes.replace(",", "")
        list_ticketnotes=list_ticketnotes.replace("'", "")

        # For Ticket tasknotes  
        tasknotes = TaskManager.objects.filter(tmgr_ticket_id=id).filter(tmgr_is_delete=0).values_list('task_note')
        list_tasknotes=""
        for tasknote in tasknotes:
            list_tasknotes += str(tasknote)    

        list_tasknotes=list_tasknotes.replace(")", "")
        list_tasknotes=list_tasknotes.replace("(", "")
        list_tasknotes=list_tasknotes.replace(",", "")
        list_tasknotes=list_tasknotes.replace("'", "")

        CustomerID = "ATG Extra"
        Organization = "ATG Extra Organization"
        IssueLabel = "Ticket"
        IssueLabelPlural = "Tickets"
        SpecFunc1 = "Record Locator: 123456-A"
        SpecFunc2 = "Caller Name: 123456-B"
        SpecFunc3 = "Caller Phone: 123456-C"
        SpecFunc4 = "Caller Email: 123456-D"
        SpecFunc5 = "Passenger Name: 123456-E"
        TaskDesc = "Has Ink Cartridge Been Replaced?"
        TaskDueDate = "01/01/2000"
        TaskAssignee = "Doe, Jane"
        TaskCompleter = "Doe, John"
        TaskResponse = "Yes"
        # IssueLink = '<br><a href="http://'+ request.META['HTTP_HOST'] + '/Home_ViewTicket?tickID='+ str(encrypted_id)+ '">View Ticket</a><br>'
        IssueLink = '<a href="http://40.127.104.66/portal/atg-extra/Home_ViewTicket?tickID='+ str(encrypted_id)+ '">View Ticket</a>'
        IssueDetails =  "Ticket # "+ str(ticket.ticket_id) + " \r\nSubject: " + str(ticket.subject) + "\r\n" + "Status:" + str(status)+ "\r\n...\r\n"
        Solution = ""
        Attachments = ""
        AllNotesExceptNewest = "Notes (Excluding Newest):\r\n[List of all notes except newest]\r\n"
        NewestNote = "Newest Note:\r\n[Newest note on Ticket]\r\n"
        
        # for Message textarea
        Message = Message.replace('"', "")
        Message = Message.replace(r"\r\n", r"<br>")
        Message = Message.replace("<@CustomerID>", CustomerID)
        Message = Message.replace("<@IssueNbr>", str(ticket.ticket_id))
        Message = Message.replace("<@IssueSubj>", str(ticket.subject))
        Message = Message.replace("<@IssueDesc>", 'Ticket Description:'+str(ticket.description+'<br>'))
        Message = Message.replace("<@Organization>", Organization)
        Message = Message.replace("<@SpecFunc1>", SpecFunc1)
        Message = Message.replace("<@SpecFunc2>", SpecFunc2)
        Message = Message.replace("<@SpecFunc3>", SpecFunc3)
        Message = Message.replace("<@SpecFunc4>", SpecFunc4)
        Message = Message.replace("<@SpecFunc5>", SpecFunc5)
        Message = Message.replace("<@TaskDesc>", TaskDesc)
        Message = Message.replace("<@TaskDueDate>", TaskDueDate)
        Message = Message.replace("<@TaskAssignee>", TaskAssignee)
        Message = Message.replace("<@TaskCompleter>", TaskCompleter)
        Message = Message.replace("<@TaskResponse>", TaskResponse)
        Message = Message.replace("<@CalEventNbr>", "")
        Message = Message.replace("<@CalEventDesc>", "")
        Message = Message.replace("<@CalEventDate>", "")
        Message = Message.replace("<@CalEventTime>", "")
        Message = Message.replace("<@IssueLink>", IssueLink)
        Message = Message.replace("<@IssueDetails>", IssueDetails)
        Message = Message.replace("<@TaskList>", 'Tasks:<br>[List of Tasks]'+list_tasknotes)
        Message = Message.replace("<@Solution>", Solution)
        Message = Message.replace("<@Attachments>", Attachments)
        Message = Message.replace("<@IssueLabel>", IssueLabel)
        Message = Message.replace("<@IssueLabelPlural>", IssueLabelPlural)
        Message = Message.replace("<@IssueDesc>", str(ticket.description))
        Message = Message.replace("<@AllNotes>", 'Notes:<br>[List of Notes]'+list_ticketnotes)
        Message = Message.replace("<@AllNotesExceptNewest>", AllNotesExceptNewest)
        Message = Message.replace("<@NewestNote>", NewestNote)

    if ttype == 'task':
        task = TaskManager.objects.get(pk = id) 
        ticket = Ticket.objects.get(pk = task.tmgr_ticket_id)
        # For encryption id
        encrypted_id = signing.dumps(ticket.ticket_id, salt=settings.SALT_KEY)
        # For Ticket Status
        if ticket.ticket_status == '1':
            status = 'Closed'
        else:     
            status = 'Open'
        # For Task Assigne
        taskassignee = User.objects.values_list('display_name', flat=True).filter(pk=task.task_assigned_to_id)
        # For Ticket ticketnotes  
        ticketnotes = TicketNote.objects.filter(note_ticket_id=task.tmgr_ticket_id).filter(note_is_delete=0).values_list('note_detail')
        list_ticketnotes=""
        for ticketnote in ticketnotes:
            list_ticketnotes += str(ticketnote)

        list_ticketnotes=list_ticketnotes.replace(")", "")
        list_ticketnotes=list_ticketnotes.replace("(", "")
        list_ticketnotes=list_ticketnotes.replace(",", "")
        list_ticketnotes=list_ticketnotes.replace("'", "")    

        # For Ticket tasknotes  
        tasknotes = TaskManager.objects.filter(tmgr_ticket_id=task.tmgr_ticket_id).filter(tmgr_is_delete=0).values_list('task_note')
        list_tasknotes=""
        for tasknote in tasknotes:
            list_tasknotes += str(tasknote)    

        list_tasknotes=list_tasknotes.replace(")", "")
        list_tasknotes=list_tasknotes.replace("(", "")
        list_tasknotes=list_tasknotes.replace(",", "")
        list_tasknotes=list_tasknotes.replace("'", "")    


        CustomerID = "ATG Extra"
        Organization = "ATG Extra Organization"
        IssueLabel = "Ticket"
        IssueLabelPlural = "Tickets"
        SpecFunc1 = "Record Locator: 123456-A"
        SpecFunc2 = "Caller Name: 123456-B"
        SpecFunc3 = "Caller Phone: 123456-C"
        SpecFunc4 = "Caller Email: 123456-D"
        SpecFunc5 = "Passenger Name: 123456-E"
        TaskResponse = "Yes"
        # IssueLink = '<br><a href="http://'+ request.META['HTTP_HOST'] + '/Home_ViewTicket?tickID='+ str(encrypted_id)+ '">View Ticket</a><br>'
        IssueLink = '<a href="http://40.127.104.66/portal/atg-extra/Home_ViewTicket?tickID='+ str(encrypted_id)+ '">View Ticket</a>\r\n'
        IssueDetails =  "Ticket # "+ str(ticket.ticket_id) + "\r\nSubject: " + str(ticket.subject) + "\r\n" + "Status:" + str(status)+ "\r\n...\r\n"
        Solution = ""
        Attachments = ""
        AllNotesExceptNewest = "Notes (Excluding Newest):\r\n[List of all notes except newest]\r\n"
        NewestNote = "Newest Note:\r\n[Newest note on Ticket]\r\n"
        
        # for Message textarea
        Message = Message.replace('"', "")
        Message = Message.replace(r"\r\n", r"<br>")
        Message = Message.replace("<@CustomerID>", CustomerID)
        Message = Message.replace("<@IssueNbr>", str(ticket.ticket_id))
        Message = Message.replace("<@IssueSubj>", str(ticket.subject))
        Message = Message.replace("<@IssueDesc>", 'Ticket Description:'+str(ticket.description+'<br>'))
        Message = Message.replace("<@Organization>", Organization)
        Message = Message.replace("<@SpecFunc1>", SpecFunc1)
        Message = Message.replace("<@SpecFunc2>", SpecFunc2)
        Message = Message.replace("<@SpecFunc3>", SpecFunc3)
        Message = Message.replace("<@SpecFunc4>", SpecFunc4)
        Message = Message.replace("<@SpecFunc5>", SpecFunc5)
        Message = Message.replace("<@TaskDesc>", str(task.task_note))
        Message = Message.replace("<@TaskDueDate>", str(task.task_due_date))
        Message = Message.replace("<@TaskAssignee>", str(taskassignee))
        Message = Message.replace("<@TaskCompleter>",str(taskassignee))
        Message = Message.replace("<@TaskResponse>", TaskResponse)
        Message = Message.replace("<@CalEventNbr>", "")
        Message = Message.replace("<@CalEventDesc>", "")
        Message = Message.replace("<@CalEventDate>", "")
        Message = Message.replace("<@CalEventTime>", "")
        Message = Message.replace("<@IssueLink>", IssueLink)
        Message = Message.replace("<@IssueDetails>", IssueDetails)
        Message = Message.replace("<@TaskList>", 'Tasks:<br>[List of Tasks]'+list_tasknotes)
        Message = Message.replace("<@Solution>", Solution)
        Message = Message.replace("<@Attachments>", Attachments)
        Message = Message.replace("<@IssueLabel>", IssueLabel)
        Message = Message.replace("<@IssueLabelPlural>", IssueLabelPlural)
        Message = Message.replace("<@IssueDesc>", str(ticket.description))
        Message = Message.replace("<@AllNotes>", 'Notes:<br>[List of Notes]'+list_ticketnotes)
        Message = Message.replace("<@AllNotesExceptNewest>", AllNotesExceptNewest)
        Message = Message.replace("<@NewestNote>", NewestNote)     
        
    return Message
#Custom Messages Replace Message Text end# 
