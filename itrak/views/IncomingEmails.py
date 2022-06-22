from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from itrak.models import Organization, Client
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Q
from itrak.views.Load import *
from itrak.views.Email import *
from itrak.helpers import *
from django.core import signing
from django.db import transaction, IntegrityError,connection
from dateutil import tz
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
import email
import imaplib
from imaplib import IMAP4
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models.expressions import RawSQL
from django.db.models.query import QuerySet
from django.template.loader import render_to_string, get_template
import os
import base64
import time
from email.utils import getaddresses

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
@active_user_required
def addIEmMailboxes(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    global_user = isGlobalUser(request)
    org_id = request.user.user_org_id
    user_id = request.user.id
    if request.user.user_type_slug != global_user:
        try:
            data = HoursOfOperation.objects.filter(sys_is_delete=0).first()
            organizations = Organization.objects.filter(org_id=org_id).filter(org_is_delete=0).filter(org_is_active=1)
            clients = Client.objects.filter(cl_is_delete=0)
            ticketTypes = get_tickettype_data(request) 
            users = User.objects.filter(user_org_id=org_id).filter(is_delete=0,user_type = 0 )
            user_templates = UserTemplate.objects.filter(template_org_id = request.user.user_org_id).filter(is_delete=0)
        except HoursOfOperation.DoesNotExist:
            data = ''
    else:
        try:
            data = HoursOfOperation.objects.filter(sys_is_delete=0).first()
            organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1)
            clients = Client.objects.filter(cl_is_delete=0)
            ticketTypes = get_tickettype_data(request) 
            users = User.objects.filter(is_delete=0,user_type = 0 )
            user_templates = UserTemplate.objects.filter(is_delete=0)
        except HoursOfOperation.DoesNotExist:
            data = ''
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
        'data': data,
        'organizations': organizations,
        'clients': clients,
        'ticketTypes': ticketTypes,
        'users': users,
        'user_templates': user_templates,
    }
    return render(request, 'itrak/IncomingEmail/add_IEM_Mailboxes.html', context)

@active_user_required
def saveMailBox(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id    
    errors_list = []
    if 'server_type' in request.POST and request.POST['server_type'] == 'IMAP' or request.POST['server_type'] == 'POP3':
        if 'mail_server' not in request.POST or request.POST['mail_server'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Mail Server.'))
    if 'server_type' in request.POST and request.POST['server_type'] == 'Exchange':
        if 'version' not in request.POST or request.POST['version'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Version.'))
    if 'enable_auto_discover' not in request.POST:
        if 'mail_server' not in request.POST or request.POST['mail_server'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Mail Server.'))
        if 'domain' not in request.POST or request.POST['domain'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter domain.'))
        if 'EWS_server_url' not in request.POST or request.POST['EWS_server_url'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter EWS Server Url.'))
    if 'account_id' not in request.POST or request.POST['account_id'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Account ID.'))
    if 'password' not in request.POST or request.POST['password'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Password.'))
    if 'default_ticket_type' not in request.POST or request.POST['default_ticket_type'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Default Ticket Type.'))
    if 'submitting_user' not in request.POST or request.POST['submitting_user'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter Submitting User.'))
    if 'cc_user' not in request.POST or request.POST['cc_user'] == '':
        errors_list.append(messages.error(request, 'Request Failed! Please Enter CC Users on Ticket distribution list.'))
    if errors_list:
        return redirect('addIEmMailboxes')

    if request.method == 'POST':           
        if 'active' in request.POST and request.POST['active']:
            active = 1
        else:
            active = 0
        server_type = request.POST.get('server_type') if 'server_type' in request.POST else ''            
        enable_auto_discover = request.POST.get('enable_auto_discover') if 'enable_auto_discover' in request.POST else ''            
        mail_server = request.POST.get('mail_server') if 'mail_server' in request.POST else '' 
        use_TLS = request.POST.get('use_TLS') if 'use_TLS' in request.POST else ''            
        TLS_port = request.POST.get('TLS_port') if 'TLS_port' in request.POST else ''            
        domain = request.POST.get('domain') if 'domain' in request.POST else ''            
        version = request.POST.get('version') if 'version' in request.POST else ''            
        EWS_server_url = request.POST.get('EWS_server_url') if 'EWS_server_url' in request.POST else ''            
        account_id = request.POST.get('account_id') if 'account_id' in request.POST else ''            
        password = request.POST.get('password') if 'password' in request.POST else ''            
        return_address = request.POST.get('return_address') if 'return_address' in request.POST else ''           
        from_name = request.POST.get('from_name') if 'from_name' in request.POST else ''            
        delete_message_processing = request.POST.get('delete_message_processing') if 'delete_message_processing' in request.POST else ''            
        if 'assign_to' in request.POST and request.POST['assign_to']:
            assign_to = request.POST.get('assign_to') 
        else:
            assign_to = None
        quick_pick = request.POST.get('quick_pick') if 'quick_pick' in request.POST else ''            
        default_quick_pick = request.POST.get('default_quick_pick') if 'default_quick_pick' in request.POST else ''            
        assign_ticket_type = request.POST.get('assign_ticket_type') if 'assign_ticket_type' in request.POST else 0            
        if 'default_ticket_type' in request.POST and request.POST['default_ticket_type']:
            default_ticket_type = request.POST.get('default_ticket_type')
        else:
            default_ticket_type = 0
        submitting_user = request.POST.get('submitting_user') if 'submitting_user' in request.POST else ''
        if 'caller_id1' in request.POST and request.POST['caller_id1']:
            caller_id1 = request.POST.get('caller_id1') 
        else:  
            caller_id1 = 0
        if 'caller_id2' in request.POST and request.POST['caller_id2']:
            caller_id2 = request.POST.get('caller_id2') 
        else:  
            caller_id2 = 0

        if 'submit_user_organization' in request.POST and request.POST['submit_user_organization']:
            submit_user_organization = request.POST.get('submit_user_organization') 
        else:  
            submit_user_organization = None

        if 'submit_user_client' in request.POST and request.POST['submit_user_client']:
            submit_user_client = request.POST.get('submit_user_client') 
        else:  
            submit_user_client = None

        additional_option1 = request.POST.get('additional_option1') if 'additional_option1' in request.POST else ''            
        additional_option2 = request.POST.get('additional_option2') if 'additional_option2' in request.POST else ''            
        additional_option3 = request.POST.get('additional_option3') if 'additional_option3' in request.POST else ''            
        enable_cc_list = request.POST.get('enable_cc_list') if 'enable_cc_list' in request.POST else ''            
        cc_user = request.POST.get('cc_user') if 'cc_user' in request.POST else '' 
        if 'add_user_template' in request.POST and request.POST['add_user_template']:
            add_user_template = request.POST.get('add_user_template') 
        else:  
            add_user_template = 0       

        if 'cc_user_organization' in request.POST and request.POST['cc_user_organization']:
            cc_user_organization = request.POST.get('cc_user_organization') 
        else:  
            cc_user_organization = 0   

        if 'cc_user_client' in request.POST and request.POST['cc_user_client']:
            cc_user_client = request.POST.get('cc_user_client') 
        else:  
            cc_user_client = 0  

        cc_user_checkbox1 = request.POST.get('cc_user_checkbox1') if 'cc_user_checkbox1' in request.POST else ''            
        cc_user_checkbox2 = request.POST.get('cc_user_checkbox2') if 'cc_user_checkbox2' in request.POST else ''            
        reopen_tickets = request.POST.get('reopen_tickets') if 'reopen_tickets' in request.POST else ''            
        notify_on_error = request.POST.get('notify_on_error') if 'notify_on_error' in request.POST else ''            
        max_size = request.POST.get('max_size') if 'max_size' in request.POST else ''            
        refuse_count = request.POST.get('refuse_count') if 'refuse_count' in request.POST else ''            
        within_count = request.POST.get('within_count') if 'within_count' in request.POST else ''            
        # return HttpResponse(assign_to)
        MailBox.objects.create(
            active=active,
            server_type=server_type,
            enable_auto_discover=enable_auto_discover,
            mail_server=mail_server,
            use_TLS=use_TLS,
            TLS_port=TLS_port,
            domain=domain,
            version=version,
            EWS_server_url=EWS_server_url,
            account_id=account_id,
            password=password,
            return_address=return_address,
            from_name=from_name,
            delete_message_processing=delete_message_processing,
            assign_to=assign_to,
            quick_pick=quick_pick,
            default_quick_pick=default_quick_pick,
            assign_ticket_type=assign_ticket_type,
            default_ticket_type=default_ticket_type,
            submitting_user=submitting_user,
            caller_id1=caller_id1,
            caller_id2=caller_id2,
            submit_user_organization=submit_user_organization,
            submit_user_client=submit_user_client,
            additional_option1=additional_option1,
            additional_option2=additional_option2,
            additional_option3=additional_option3,
            enable_cc_list=enable_cc_list,
            cc_user=cc_user,
            add_user_template=add_user_template,
            cc_user_organization=cc_user_organization,
            cc_user_client=cc_user_client,
            cc_user_checkbox1=cc_user_checkbox1,
            cc_user_checkbox2=cc_user_checkbox2,
            reopen_tickets=reopen_tickets,
            notify_on_error=notify_on_error,
            max_size=max_size,
            refuse_count=refuse_count,
            within_count=within_count,
            mail_box_org_id = org_id,
        )
        
        messages.success(request, 'Request Succeed! Mailbox added.')
        return redirect('addIEmMailboxes')
    else:
        messages.error(request, 'Request Failed! Mailbox cannot be added. Please try again.')
        return redirect('addIEmMailboxes')

@active_user_required
def runMailBox(request):
    global_user = isGlobalUser(request)
    current_user_id = request.user.id
    org_id = request.user.user_id
    if request.user.user_type_slug != global_user:
        mailboxs = MailBox.objects.filter(is_active=1).filter(is_delete=0).filter(mail_box_org_id=current_user_id)
    else:
        mailboxs = MailBox.objects.filter(is_active=1).filter(is_delete=0)
    for mailbox in mailboxs:
        # mailbox = MailBox.objects.get(mail_box_id=mailbox)
        mail_box_id = mailbox.mail_box_id
        mail_server = mailbox.mail_server
        account_id = mailbox.account_id
        password = mailbox.password
        TLS_port = mailbox.TLS_port
        responseMsgsArray = []
        # connection to imap  
        conn = imaplib.IMAP4_SSL(mail_server,TLS_port)
        try:
            (retcode, capabilities) = conn.login(account_id, password)
        except:
            messages.error(request, 'Request Failed! Unable to connect to Mailbox. Please try again.')
            return redirect('addIEmMailboxes')
		
        conn.select('"INBOX"') 
        (retcode, messagess) = conn.uid('search', None, "ALL")
        if retcode == 'OK':
            for num in messagess[0].split():

                emailResponseMsgs = {}
                typ, data = conn.uid('fetch', num,'(RFC822)')
                msg = email.message_from_bytes((data[0][1]))
                toAddress = email.utils.parseaddr(msg['to'])
                toAddress = toAddress[1]
                fromFull = email.utils.parseaddr(msg['from'])
                fromName = fromFull[0]
                fromAddress = fromFull[1]
                ccAddress = email.utils.parseaddr(msg['cc'])
                ccAddress1 = ccAddress[1]
                ccs = msg.get_all('cc', [])
                resent_ccs = msg.get_all('resent-cc', [])
                cc_recipients = getaddresses(ccs  + resent_ccs)
                
                ccEmailList = []
                for a, b in cc_recipients:
                    ccEmailList.append(b)
                # return HttpResponse('insideloop')
                bccs = msg.get_all('bcc', [])
                resent_bccs = msg.get_all('resent-bcc', [])
                bcc_recipients = getaddresses(bccs  + resent_bccs)
                
                bccAddress = email.utils.parseaddr(msg['bcc'])
                bccAddress1 = bccAddress[1]
                subject = msg["subject"]
                body = msg["body"]
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload()
                        break
                receivedDate = email.utils.parsedate(msg["Date"])
                receivedDate = time.mktime(receivedDate)
                receivedDate = datetime.utcfromtimestamp(receivedDate).strftime('%Y-%m-%d %H:%M:%S')
                emailResponseMsgs["To"] = toAddress
                emailResponseMsgs["From"] = fromAddress
                emailResponseMsgs["CC"] = ccEmailList
                emailResponseMsgs["BCC"] = ccEmailList
                emailResponseMsgs["Subject"] = subject
                emailResponseMsgs["Body"] = body
                # return HttpResponse(emailResponseMsgs["Subject"])
                
                

                #CHECK EXCLUDE TEXT
                allExcludeTexts = ExcludeText.objects.filter(etext_is_delete = 0)
                isExcludeText = False
                for text in allExcludeTexts:
                    if text.etext_name in body:
                        isExcludeText = True
                        
                if isExcludeText:
                    ticket_description = ''
                else: 
                    ticket_description = body
                 
                
                #CHECK KEYWORDS FROM SUBJECT OR FROM ADDRESS
                allKeywords = Keyword.objects.filter(keywords_is_delete = 0)
                isKeywordExclude = False
                for keyword in allKeywords:
                    if keyword.keywords_search_in == 1:
                        if keyword.keywords_search_for == 1:
                            if keyword.keywords_name == subject:
                                isKeywordExclude = True
                        else:
                            if keyword.keywords_name in subject:
                                isKeywordExclude = True
                    else:
                        if keyword.keywords_search_for == 1:
                            if keyword.keywords_name == fromAddress:
                                isKeywordExclude = True
                        else:
                            if keyword.keywords_name in fromAddress:
                                isKeywordExclude = True
                
                if isKeywordExclude:
                    #MOVE MESSAGE TO ProcessedEmails FOLDER
                    result = conn.uid('COPY', num, 'ProcessedEmails')
                    if result[0] == 'OK':
                        
                        mov, data = conn.uid('STORE', num , '+FLAGS', '(\Deleted)')
                        conn.expunge()
                    emailResponseMsgs["Exclude keywords"] = "record skipped due to exclude keywords"
                    responseMsgsArray.append(emailResponseMsgs)  
                    continue
                
                mailbox = MailBox.objects.get(mail_box_id=mail_box_id)
                assign_ticket_type = mailbox.assign_ticket_type
                assign_to = mailbox.assign_to
                client_id = mailbox.submit_user_client
                org_id = mailbox.submit_user_organization
                
                # check ticket type
                if assign_ticket_type == 'ticket_type_or_subtype_name_exactly':  
                    ticketTypes = TicketType.objects.filter(ttype_name=msg['Subject'],ttype_is_active=1,ttype_is_delete=0)         
                    if ticketTypes:
                        for ticketType in ticketTypes:
                            ticket_type =  ticketType.ttype_id
                        
                        ticket_type = getGrandParentTicketType(request, ticket_type=ticket_type)
                    else:
                        ticket_type = mailbox.default_ticket_type  
                elif assign_ticket_type == 'ticket_type_or_subtype_name':
                    ticketTypes = TicketType.objects.filter(ttype_name__contains=msg['Subject'],ttype_is_active = 1,ttype_is_delete=0)
                    if ticketTypes:
                        for ticketType in ticketTypes:
                            ticket_type =  ticketType.ttype_id
                        ticket_type = getGrandParentTicketType(request, ticket_type=ticket_type)
                    else:
                        ticket_type = mailbox.default_ticket_type
                elif assign_ticket_type == 'do_not_derive':
                    ticket_type = mailbox.default_ticket_type

                emailResponseMsgs["Ticket Type ID"] = ticket_type
                
                # CHECK SUBMITTER USER
                submitting_user = mailbox.submitting_user
                if(submitting_user == "Accept_email_from_existing_ATG_iTrak_users_only"):
                    IsUserExixtInATGSystem = User.objects.filter(email=fromAddress).filter(is_delete = 0).count()
                    # return HttpResponse(fromAddress)
                    if IsUserExixtInATGSystem > 0:
                        userData = User.objects.get(email=fromAddress)
                        user_id = userData.id
                        emailResponseMsgs["User ID"] = user_id
                    else:
                        emailResponseMsgs["User ID"] = "User is not exists in ATG DATABASE"
                        responseMsgsArray.append(emailResponseMsgs)  
                        continue
                elif(submitting_user == "Submit_new_Ticket_or_add_Note_as_this_user"):
                    user_id = mailbox.caller_id1
                    emailResponseMsgs["User ID"] = user_id
                elif(submitting_user == "Create_users_from_this_template"):
                    user_temp_id = mailbox.caller_id2
                    additional_option1 = mailbox.additional_option1
                    IsUserExixtInATGSystem = User.objects.filter(email=fromAddress).count()
                    if IsUserExixtInATGSystem > 0:
                        userData = User.objects.get(email=fromAddress)
                        user_id = userData.id
                        emailResponseMsgs["User ID"] = "User already exits in DB:"+ str(user_id)
                    else:
                        if additional_option1 == "additional_option1":
                            user_id = createUserFromTemplate(request, user_temp_id, fromAddress, 1)
                            emailResponseMsgs["User ID"] = "User Created with Login Access:"+ str(user_id)
                        else:
                            user_id = createUserFromTemplate(request, user_temp_id, fromAddress, 0)
                            emailResponseMsgs["User ID"] = "User Created with No Login Access:"+ str(user_id)

                elif(submitting_user == "Create_users_with_these_default_values"):
                    submit_user_organization = mailbox.submit_user_organization
                    submit_user_client = mailbox.submit_user_client
                    IsUserExixtInATGSystem = User.objects.filter(email=fromAddress).count()
                    
                    if IsUserExixtInATGSystem > 0:
                        userData = User.objects.get(email=fromAddress)
                        user_id = userData.id
                        emailResponseMsgs["User ID"] = "User already exits in DB"+ str(user_id)
                    else:
                        user_id = createUserFromOrganization(request, submit_user_organization, submit_user_client, fromAddress)
                        emailResponseMsgs["User ID"] = "User created with given OrgID and ClientID:"+ str(user_id)
                
                
                
                # CHECK CC Users
                cc_user = mailbox.cc_user
                if(cc_user == "Only_add_existing_ATG_iTrak_users_to_Issue_distribution_list"):
                    existingATGUsersListInCC = []
                    for i in ccEmailList:
                        isUserExistsInATG = User.objects.filter(email=i).count()
                        if isUserExistsInATG:
                            existingATGUsersListInCC.append(i)
                    emailResponseMsgs["CC Users which exists in ATG"] = existingATGUsersListInCC
                else:
                    enable_cc_list = mailbox.enable_cc_list
                    if enable_cc_list == "enable_cc_list":
                        if(cc_user == "Create_users_from_this_template"):
                            user_temp_id = mailbox.add_user_template
                            cc_user_checkbox1 = mailbox.cc_user_checkbox1
                            existingATGUsersListInCC = []
                            for i in ccEmailList:
                                existingATGUsersListInCC.append(i)
                                IsUserExixtInATGSystem = User.objects.filter(email=i).count()
                                if IsUserExixtInATGSystem == 0:
                                    if cc_user_checkbox1 == "cc_user_checkbox1":
                                        cc_new_user = createUserFromTemplate(request, user_temp_id, i, 1)
                                        emailResponseMsgs["Users created from CC list which was not in ATG(with login access):"] = cc_new_user
                                    else:
                                        cc_new_user = createUserFromTemplate(request, user_temp_id, i, 0)
                                        emailResponseMsgs["Users created from CC list which was not in ATG(with out login Access):"] = cc_new_user
                            emailResponseMsgs["All Users in CC list"] = existingATGUsersListInCC
                        elif(cc_user == "Create_users_with_these_default_values"):
                            
                            cc_user_organization = mailbox.cc_user_organization
                            cc_user_client = mailbox.cc_user_client
                            existingATGUsersListInCC = []
                            for i in ccEmailList:
                                existingATGUsersListInCC.append(i)
                                IsUserExixtInATGSystem = User.objects.filter(email=i).count()
                                if IsUserExixtInATGSystem == 0:
                                    cc_new_user_with_Org = createUserFromOrganization(request, cc_user_organization, cc_user_client, i)
                                    emailResponseMsgs["User Created from CC having OrgID and ClientID:"] = existingATGUsersListInCC
                                    emailResponseMsgs["All Users in CC list"] = cc_new_user_with_Org
                
                submit_date = datetime.today().strftime('%Y-%m-%d')
                submit_time = datetime.now().strftime('%I:%M %p')
                with transaction.atomic():
                    
                    submit_date = datetime.strptime(submit_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                
                    submit_time = datetime.strptime(submit_time, '%I:%M %p').strftime('%H:%M:%S')
                    tempdateTime = str(submit_date) + ' ' + str(submit_time)

                    dateTime = datetime.strptime(tempdateTime, '%Y-%m-%d %H:%M:%S')

                    uTimeZone = MySettings.objects.filter(m_user_id=user_id).first().m_time_zone

                    # METHOD 1: Hardcode zones:
                    from_zone = tz.gettz(uTimeZone)
                    to_zone = tz.gettz('UTC')

                    # utc = datetime.utcnow()
                    utc = dateTime

                    # Tell the datetime object that it's in UTC time zone since
                    # datetime objects are 'naive' by default
                    utc = utc.replace(tzinfo=from_zone)

                    # Convert time zone
                    central = utc.astimezone(to_zone)

                    submitted_at = central
                    org_id = org_id
                    caller_id = user_id
                    client_id = client_id
                    clientinfo_id = ''
                    record_locator = ''
                    caller_name = ''
                    caller_phone = ''
                    caller_email = ''
                    passenger_name = ''
                    subject = 'Ticket From IEM'
                    description = ticket_description
                    ticket_type = ticket_type
                    subtype1 = ''
                    subtype2 = ''
                    subtype3 = ''
                    subtype4 = ''
                    priority = 4
                    ticket_substatus = 1
                    traveler_vip = ''
                    payout_required = None
                    error_goodwill = None
                    amount_saved = ''
                    airline_ticket = ''
                    agent_responsible = None
                    vendor_responsible = None
                    vresponsible_city = None
                    ticket_payout_amount = None
                    ticket_order_of_pay = None
                    ticket_attention = None
                    ticket_company = None
                    ticket_address = None
                    notes_on_check = None
                    check_number = None
                    check_approved_by = None
                    corr_cont_actions = 'IEM Mailbox'
                    ticket_root_cause = None
                    corrective_action = None
                    ticket_note = ''
                    is_private = 'True'
                    labour_hours_hours = 0
                    labour_hours_minutes = 0
                    assign_to = assign_to
                    
                    obj = Ticket(
                        submitted_date=submit_date,
                        submitted_time=submit_time,
                        submitted_at=submitted_at,
                        ticket_org_id=org_id,
                        ticket_caller_id=caller_id,
                        ticket_client_id=client_id,
                        ticket_clientinformation_id=clientinfo_id,
                        ticket_record_locator=record_locator,
                        ticket_caller_name=caller_name,
                        ticket_caller_phone=caller_phone,
                        ticket_caller_email=caller_email,
                        ticket_passenger_name=passenger_name,
                        subject=subject,
                        description=description,
                        ticket_type_id=ticket_type,
                        ticket_subtype1_id=subtype1,
                        ticket_subtype2_id=subtype2,
                        ticket_subtype3_id=subtype3,
                        ticket_subtype4_id=subtype4,
                        priority_id=priority,
                        ticket_status=0,
                        ticket_sub_status_id=ticket_substatus,
                        is_traveler_vip=traveler_vip,
                        is_payout_required=payout_required,
                        agent_error_goodwill=error_goodwill,
                        amount_saved=amount_saved,
                        airline_ticket_no=airline_ticket,
                        agent_responsible=agent_responsible,
                        vendor_responsible=vendor_responsible,
                        vresponsible_city=vresponsible_city,
                        ticket_payout_amount=ticket_payout_amount,
                        ticket_order_of_pay=ticket_order_of_pay,
                        ticket_attention=ticket_attention,
                        ticket_company=ticket_company,
                        ticket_address=ticket_address,
                        notes_on_check=notes_on_check,
                        check_number=check_number,
                        check_approved_by=check_approved_by,
                        corr_cont_actions=corr_cont_actions,
                        ticket_root_cause=ticket_root_cause,
                        corrective_action=corrective_action,
                        ticket_created_by_id=user_id,
                        ticket_is_open_by_id=user_id,
                    )
                    obj.save()
                    insert_id = Ticket.objects.latest('pk').ticket_id
                    TObj = Ticket.objects.get(pk=insert_id)
                    emailResponseMsgs["Ticket ID"] = insert_id
                    
                    # return HttpResponse(insert_id)

                    # Assigned Object Insertion
                    if assign_to:
                        try:
                            TObj.ticket_assign_to_id = assign_to
                            TObj.ticket_assign_by_id = request.user.id
                            TObj.ticket_assign_at = datetime.now(timezone.utc)
                            TObj.save()
                        except IntegrityError:
                            transaction.rollback()
                            messages.error(request, 'Request Failed! Ticket cannot be submitted.Please try again.')
                            return redirect('submitTicket')
                    send_Auto_Email_On_Assign_Ticket(assign_to, insert_id, fromAddress, existingATGUsersListInCC)
                    send_Auto_Email_On_Submit_Ticket(user_id, insert_id, fromAddress, existingATGUsersListInCC)
                    # send_Auto_Email_On_Note_Ticket(user_id,insert_id)        

                #EMAIL LOG ENTRY TO TRACK PROCESSED EMAILS
                view_log_obj = MailBoxEmailViewLog(
                    evl_mail_box_id = mail_box_id
                    ,evl_to = toAddress
                    ,evl_from = fromAddress
                    ,evl_cc = ccAddress1
                    ,evl_bcc = bccAddress1
                    ,evl_subject = subject
                    ,evl_body = body
                    ,evl_received_date = receivedDate
                    ,evl_ticket_id = insert_id
                    ,evl_org_id = current_user_id
                )
                view_log_obj.save()

                # DOWNLOAD ATTACHMENTS
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        responseMsgsArray.append(emailResponseMsgs)  
                        continue
                    if part.get('Content-Disposition') is None:
                        responseMsgsArray.append(emailResponseMsgs)  
                        continue
                    fileName = part.get_filename()
                    if bool(fileName):
                        filePath = os.path.join('C:/Users/bali/attachments/', fileName)
                        if not os.path.isfile(filePath) :
                            fp = open(filePath, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()

                    attach_obj =IncomingEmailAttachement(
                        attach_name = fileName,
                        email_id = view_log_obj.evl_id
                    )
                    attach_obj.save()
                
                #ADD ASSINED_TO LOG
                if assign_to:
                    to_email = User.objects.get(id=assign_to).email
                    assignee_name = User.objects.get(id=assign_to).first_name
                    
                    obj1 = TicketUserRoleLog(
                        urlog_ticket_id=insert_id,
                        urlog_user_id=assign_to,
                        urlog_event=1,
                        urlog_created_by_id=request.user.id
                    )
                    obj1.save()
                    ticket_id = id
                    send_email_helper(to_email)
                    create_email_helper(assignee_name, to_email, ticket_id)

                #MOVE MESSAGE TO ProcessedEmails FOLDER
                result = conn.uid('COPY', num, 'ProcessedEmails')
                if result[0] == 'OK':
                    mov, data = conn.uid('STORE', num , '+FLAGS', '(\Deleted)')
                    conn.expunge()
                responseMsgsArray.append(emailResponseMsgs)
                return HttpResponse(123)  
                
            return HttpResponse(json.dumps(responseMsgsArray), content_type="application/json")
        conn.close()   

@csrf_exempt
def addUserTemplate(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        user_id = request.user.id
        org_id = request.user.user_org_id
        global_user = isGlobalUser(request)
        if request.user.user_type_slug != global_user:
            user = User.objects.get(id=request.user.id)
            organizations = Organization.objects.filter(org_id=org_id).filter(org_is_active=1).filter(org_is_delete=0)
            departments = Department.objects.filter(user_org_id=org_id).filter(d_is_delete=0)
            clients = Client.objects.filter(cl_is_delete=0)
            permissions = PermissionSection.objects.filter(is_active=1).all()
            disabled_actions= permissions_not_allowed(request, user)
            disabled_sub_action= sub_permissions_not_allowed(request, user)
        else:
            user = User.objects.get(id=request.user.id)
            organizations = Organization.objects.filter(org_is_active=1).filter(org_is_delete=0)
            departments = Department.objects.filter(d_is_delete=0)
            clients = Client.objects.filter(cl_is_delete=0)
            permissions = PermissionSection.objects.filter(is_active=1).all()
            disabled_actions= permissions_not_allowed(request, user)
            disabled_sub_action= sub_permissions_not_allowed(request, user)
        load_sidebar = get_sidebar(request)
        context = {
            'user': user,
            'organizations': organizations,
            'departments': departments,
            'clients': clients,
            'permissions': permissions,
            'sidebar': load_sidebar,
            'timezones': pytz.common_timezones,
            'disabled_actions': disabled_actions,
            'disabled_sub_action': disabled_sub_action,
        }
        return render(request, 'itrak/IncomingEmail/add_user_template_modal.html', context)
        
@active_user_required
def saveUserTemplateModal(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    # return HttpResponse(request.POST.get('user_type'))
    user = User.objects.get(id=request.user.id)
    org_id = request.user.user_org_id
    if request.method == 'POST':
        user_type = 2
        if 'user_cus_id' in request.POST:
            user_cus_id = request.POST.get('user_cus_id')
        if 'first_name' in request.POST and request.POST['first_name']:
            first_name = request.POST.get('first_name')
        if 'last_name' in request.POST and request.POST['last_name']:
            last_name = request.POST.get('last_name')
        if 'display_name' in request.POST:
            display_name = request.POST.get('display_name')
        
        obj = UserTemplate(
            user_type=user_type, 
            username=user_cus_id, 
            email=user_cus_id, 
            first_name=first_name, 
            last_name=last_name, 
            display_name=display_name,
            template_org_id=org_id,
             
        )
        obj.save()

        #Add User Menu Permision in DB Start#

        menu_ids = request.POST.getlist('menus')
        submenu_ids = request.POST.getlist('submenus')

        for id in submenu_ids:
            permit_obj = UserTemplateMenuPermission(user_id= obj.user_temp_id, submenu_id = id)
            permit_obj.save()

        for id in menu_ids:
            permit_obj = UserTemplateMenuPermission(user_id= obj.user_temp_id, menu_id = id)
            permit_obj.save()
        #Add User Menu Permision in DB End#

        #Adding Permission Actions to UserActionPermission table        
        permission_actions = request.POST.getlist('permission_action')
        permission_sub_actions = request.POST.getlist('permission_sub_action')
        # user = UserTemplate.objects.get(pk=str(obj.user_temp_id))
        # return HttpResponse(user)
        for permission_action in permission_actions:
            permission_action_obj = PermissionAction.objects.get(perm_act_id=permission_action)
            user_act_obj = UserTemplateActionPermission(user_id=obj.user_temp_id, perm_act_id=permission_action_obj.perm_act_id)
            user_act_obj.save()
        for permission_sub_action in permission_sub_actions:
            per_sub_action_obj = PermissionSubAction.objects.get(sub_act_id=permission_sub_action)
            user_act_obj = UserTemplateSubActionPermission(user_id=obj.user_temp_id, sub_act_id=per_sub_action_obj.sub_act_id)
            user_act_obj.save()
        
        #END Adding Permission Actions to UserActionPermission table 
        messages.success(request, 'Request Succeed! User Template added.')
        return redirect('addIEmMailboxes')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! User Template cannot be added.Please try again.')
        return redirect('addIEmMailboxes')

# MailBox List Request Start#

@csrf_exempt
def testConnectionMailBox(request):
    if request.is_ajax() and request.method == 'POST':
        mail_server = request.POST.get('mail_server')
        account_id = request.POST.get('account_id')
        password = request.POST.get('password')
        TLS_port = request.POST.get('TLS_port')
        try:
            # connection to imap  
            conn = imaplib.IMAP4_SSL(mail_server, TLS_port)
            (retcode, capabilities) = conn.login(account_id, password)
            return HttpResponse(json.dumps(retcode), content_type="application/json")
        except:
            return HttpResponse(json.dumps("Fail!, Credentials issue."), content_type="application/json")
        
    else:
        return HttpResponse(json.dumps("Not a valid ajax function"), content_type="application/json")

@active_user_required
def listMailBox(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/incomingEmail/mailBox_list.html', context)

# MailBox List Request End#

#Datatable Code Start Here#
class MailBoxListJson(BaseDatatableView):
    # The model we're going to show
    model = MailBox

    # define the columns that will be returned
    # columns = ['action', 'org_id', 'org_name', 'is_internal', 'display']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    # order_columns = ['', 'mail_box_id']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        # signer = Signer(salt='extra')
        # original = signer.sign(rid)
        # value = signer.unsign(original)
        # new = base64.b64decode(value).decode('ascii')
        # # return HttpResponse(original)
        # print(type(new))
        rid = signing.dumps(row.mail_box_id)

        if column == 'action':
            return '<a href="Admin_MailBoxEdit?MBID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_MailBoxDel?MBID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'     
        elif column == 'is_active':
            if row.is_active == True:
                return escape('{0}'.format('Yes'))
            else:
                return escape('{0}'.format('No'))
        elif column == 'default_ticket_type':
            if row.default_ticket_type:
                ticketTypeData = TicketType.objects.get(pk= row.default_ticket_type)
                if ticketTypeData:
                    return ticketTypeData.ttype_name
                else:
                    return ""
        elif column == 'assign_to': 
                if row.assign_to: 
                    try:
                        userData = User.objects.get(pk= row.assign_to)
                        if userData:
                            return userData.last_name+' ,'+userData.first_name
                        else:
                            return ""
                    except User.DoesNotExist:
                        return ""

        else:
            return super(MailBoxListJson, self).render_column(row, column)

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        global_user = isGlobalUser(self.request)
        user_id = self.request.user.id
        org_id = self.request.user.user_org_id
        if self.request.user.user_type_slug != global_user:
            return MailBox.objects.filter(mail_box_org_id=org_id).filter(is_delete=0)
        else:
            return MailBox.objects.filter(is_delete=0)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        # if search:
        #     qs = qs.filter(Q(org_id__icontains=search) | Q(org_name__icontains=search))
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

#Mail Box Edit Request Start#
@active_user_required
def editMailBox(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('MBID')
    org_id = request.user.user_org_id
    user_id = request.user.id
    global_user = isGlobalUser(request)
    try:
        mailbox_id = signing.loads(id)
        mailBoxData = MailBox.objects.get(pk=mailbox_id)
    except MailBox.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not mailBoxData:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listMailBox')
    else:
        if request.user.user_type_slug != global_user:
            data = HoursOfOperation.objects.filter(sys_is_delete=0).first()
            organizations = Organization.objects.filter(org_id=org_id).filter(org_is_delete=0).filter(org_is_active=1)
            clients = Client.objects.filter(cl_is_delete=0)
            ticketTypes = get_tickettype_data(request) 
            users = User.objects.filter(user_org_id=org_id).filter(is_delete=0,user_type=0)
            user_templates = UserTemplate.objects.filter(is_delete=0).filter(template_org_id=org_id)
        else:
            data = HoursOfOperation.objects.filter(sys_is_delete=0).first()
            organizations = Organization.objects.filter(org_is_delete=0).filter(org_is_active=1)
            clients = Client.objects.filter(cl_is_delete=0)
            ticketTypes = get_tickettype_data(request) 
            users = User.objects.filter(is_delete=0,user_type=0)
            user_templates = UserTemplate.objects.filter(is_delete=0)
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data,
            'organizations': organizations,
            'clients': clients,
            'ticketTypes': ticketTypes,
            'users': users,
            'user_templates': user_templates,
            'mailBoxData': mailBoxData,
        }
        return render(request, 'itrak/IncomingEmail/edit_IEM_Mailboxes.html', context)

# Mail Box Edit Request End#

#Mail Box Update Request Start
@active_user_required
def updateMailBox(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('mail_box_id')
        errors_list = []
        if 'server_type' in request.POST and request.POST['server_type'] == 'IMAP' or request.POST['server_type'] == 'POP3':
            if 'mail_server' not in request.POST or request.POST['mail_server'] == '':
                errors_list.append(messages.error(request, 'Request Failed! Please Enter Mail Server.'))
        if 'server_type' in request.POST and request.POST['server_type'] == 'Exchange':
            if 'version' not in request.POST or request.POST['version'] == '':
                errors_list.append(messages.error(request, 'Request Failed! Please Enter Version.'))
        if 'enable_auto_discover' not in request.POST:
            if 'mail_server' not in request.POST or request.POST['mail_server'] == '':
                errors_list.append(messages.error(request, 'Request Failed! Please Enter Mail Server.'))
            if 'domain' not in request.POST or request.POST['domain'] == '':
                errors_list.append(messages.error(request, 'Request Failed! Please Enter domain.'))
            if 'EWS_server_url' not in request.POST or request.POST['EWS_server_url'] == '':
                errors_list.append(messages.error(request, 'Request Failed! Please Enter EWS Server Url.'))
        if 'account_id' not in request.POST or request.POST['account_id'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Account ID.'))
        if 'password' not in request.POST or request.POST['password'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Password.'))
        if 'default_ticket_type' not in request.POST or request.POST['default_ticket_type'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Default Ticket Type.'))
        if 'submitting_user' not in request.POST or request.POST['submitting_user'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter Submitting User.'))
        if 'cc_user' not in request.POST or request.POST['cc_user'] == '':
            errors_list.append(messages.error(request, 'Request Failed! Please Enter CC Users on Ticket distribution list.'))
        if errors_list:
            
            return redirect(reverse('editMailBox') + '?MBID=' + str(signing.dumps(id)))
        try:
            obj = MailBox.objects.get(pk=id)
        except Organization.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect("/Admin_MailBoxList")
        else:
            if 'active' in request.POST and request.POST['active']:
                obj.is_active = 1
            else:
                obj.is_active = 0

            if 'server_type' in request.POST and request.POST['server_type']:
                obj.server_type = request.POST.get('server_type')
            if 'mail_server' in request.POST and request.POST['mail_server']:
                obj.mail_server = request.POST.get('mail_server')
            if 'use_TLS' in request.POST and request.POST['use_TLS']:
                obj.use_TLS = request.POST.get('use_TLS')
            if 'TLS_port' in request.POST and request.POST['TLS_port']:
                obj.TLS_port = request.POST.get('TLS_port')
            if 'account_id' in request.POST and request.POST['account_id']:
                obj.account_id = request.POST.get('account_id')
            if 'password' in request.POST and request.POST['password']:
                obj.password = request.POST.get('password')
            if 'return_address' in request.POST and request.POST['return_address']:
                obj.return_address = request.POST.get('return_address')
            if 'from_name' in request.POST and request.POST['from_name']:
                obj.from_name = request.POST.get('from_name')
            if 'delete_message_processing' in request.POST and request.POST['delete_message_processing']:
                obj.delete_message_processing = request.POST.get('delete_message_processing')
            if 'assign_to' in request.POST and request.POST['assign_to']:
                obj.assign_to = request.POST.get('assign_to')
            if 'quick_pick' in request.POST and request.POST['quick_pick']:
                obj.quick_pick = request.POST.get('quick_pick')
            if 'default_quick_pick' in request.POST and request.POST['default_quick_pick']:
                obj.default_quick_pick = request.POST.get('default_quick_pick')
            if 'assign_ticket_type' in request.POST and request.POST['assign_ticket_type']:
                obj.assign_ticket_type = request.POST.get('assign_ticket_type')
            if 'default_ticket_type' in request.POST and request.POST['default_ticket_type']:
                obj.default_ticket_type = request.POST.get('default_ticket_type')
            if 'submitting_user' in request.POST and request.POST['submitting_user']:
                obj.submitting_user = request.POST.get('submitting_user')
            if 'caller_id1' in request.POST and request.POST['caller_id1']:
                obj.caller_id1 = request.POST.get('caller_id1')
            if 'caller_id2' in request.POST and request.POST['caller_id2']:
                obj.caller_id2 = request.POST.get('caller_id2')
            if 'submit_user_organization' in request.POST and request.POST['submit_user_organization']:
                obj.submit_user_organization = request.POST.get('submit_user_organization')
            if 'submit_user_client' in request.POST and request.POST['submit_user_client']:
                obj.submit_user_client = request.POST.get('submit_user_client')
            if 'additional_option1' in request.POST and request.POST['additional_option1']:
                obj.additional_option1 = request.POST.get('additional_option1')
            else:
                obj.additional_option1 = ""
            if 'additional_option2' in request.POST and request.POST['additional_option2']:
                obj.additional_option2 = request.POST.get('additional_option2')
            else:
                obj.additional_option2 = ""
            if 'additional_option3' in request.POST and request.POST['additional_option3']:
                obj.additional_option3 = request.POST.get('additional_option3')
            else:
                obj.additional_option3 = ""
            if 'enable_cc_list' in request.POST and request.POST['enable_cc_list']:
                obj.enable_cc_list = request.POST.get('enable_cc_list')
            if 'cc_user' in request.POST and request.POST['cc_user']:
                obj.cc_user = request.POST.get('cc_user')
            if 'add_user_template' in request.POST and request.POST['add_user_template']:
                obj.add_user_template = request.POST.get('add_user_template')
            if 'cc_user_organization' in request.POST and request.POST['cc_user_organization']:
                obj.cc_user_organization = request.POST.get('cc_user_organization')
            if 'cc_user_client' in request.POST and request.POST['cc_user_client']:
                obj.cc_user_client = request.POST.get('cc_user_client')
            if 'cc_user_checkbox1' in request.POST and request.POST['cc_user_checkbox1']:
                obj.cc_user_checkbox1 = request.POST.get('cc_user_checkbox1')
            else:
                obj.cc_user_checkbox1 = ""
            if 'cc_user_checkbox2' in request.POST and request.POST['cc_user_checkbox2']:
                obj.cc_user_checkbox2 = request.POST.get('cc_user_checkbox2')
            else:
                obj.cc_user_checkbox2 = ""
            if 'reopen_tickets' in request.POST and request.POST['reopen_tickets']:
                obj.reopen_tickets = request.POST.get('reopen_tickets')
            else:
                obj.reopen_tickets = ""
            if 'notify_on_error' in request.POST and request.POST['notify_on_error']:
                obj.notify_on_error = request.POST.get('notify_on_error')
            if 'max_size' in request.POST and request.POST['max_size']:
                obj.max_size = request.POST.get('max_size')
            if 'refuse_count' in request.POST and request.POST['refuse_count']:
                obj.refuse_count = request.POST.get('refuse_count')
            if 'within_count' in request.POST and request.POST['within_count']:
                obj.within_count = request.POST.get('within_count')
            # return HttpResponse(obj)
            obj.save()
            
            messages.success(request, 'Request Succeed! MailBox updated.')
            return redirect('listMailBox')
    else:
        messages.error(request, 'Request Failed! MailBox cannot be updated.Please try again.')
        return redirect('listOrg')

# Mail Box Update Request End#


# Mail Box Delete Request Start#

@active_user_required
def deleteMailBox(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('MBID')
    mailbox_id = signing.loads(id)
    try:
        obj = MailBox.objects.get(pk=mailbox_id)
    except MailBox.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listMailBox')
    else:
        obj.is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! MailBox deleted.')
        return redirect('listMailBox')

# Mail Box Delete Request End#


def send_Auto_Email_On_Assign_Ticket(user_id, ticket_id, email_to, email_cc):
    user = User.objects.get(id=user_id)
    subject = 'On Assign #'+str(ticket_id)+' Ticket Assigned to you 😎'         
    message = 'Hi, <br> A #'+str(ticket_id)+' Ticket is assigned to you. Please have a look on your account at ATG Extra Project <span style="font-size:20px">&#128525;</span>.<br><br> Thanks. <br> Regards, <br>World best known 😎, <br> ATG Extra Team.'
    event_name = 'ticket_action_on_assign'
    action_item = 'Ticket'
    send_email(to=email_to, subject=subject, message=message, event_name=event_name, action_item=action_item)
    return
def send_Auto_Email_On_Submit_Ticket(user_id, ticket_id, email_to, email_cc):
    user = User.objects.get(id=user_id)
    subject = 'On Assign #'+str(ticket_id)+' Ticket Assigned to you 😎'
    message = 'Hi, <br> A #'+str(ticket_id)+' Ticket is created by Script. Please have a look on your account at ATG Extra Project <span style="font-size:20px">&#128525;</span>.<br><br> Thanks. <br> Regards, <br>World best known 😎, <br> ATG Extra Team.'
    event_name = 'ticket_action_on_assign'
    action_item = 'Ticket'
    send_email(to=email_to, subject=subject, message=message, event_name=event_name, action_item=action_item)
    return
# def send_Auto_Email_On_Note_Ticket(user_id):
#     user = User.objects.get(id=user_id)
#     subject = 'On Assign #'+str(ticket_id)+' Ticket Assigned to you 😎'         
#     message = 'Hi, <br> A #'+str(ticket_id)+' Ticket is assigned to you. Please have a look on your account at ATG Extra Project <span style="font-size:20px">&#128525;</span>.<br><br> Thanks. <br> Regards, <br>World best known 😎, <br> ATG Extra Team.'
#     send_email(to=email_to, subject=subject, message=message)
#     return

# Exclude Text Request Start#

@active_user_required
def listExcludeText(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/IncomingEmail/list_exclude_text.html', context)

# Exclude Text Request End#

# Exclude Text Add Request Start#

@active_user_required
def addExcludeText(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/IncomingEmail/add_exclude_text.html', context)

# Exclude Text Add Request End#

# Save Exclude Text Request Start#

@active_user_required
def saveExcludeText(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.user.user_org_id
        if 'etext_name' in request.POST and request.POST['etext_name']:
            etext_name = request.POST.get('etext_name')

        obj = ExcludeText(etext_name=etext_name, etext_org_id=org_id)
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Exclude Text added.')
        return redirect('addExcludeText')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Exclude Text cannot be added.Please try again.')
        return redirect('addExcludeText')

# Save Exclude Text Request End#

#Datatable Code Start Here#
class ExcludeTextJSON(BaseDatatableView):
    # The model we're going to show
    model = ExcludeText

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
        user_id = self.request.user.id
        org_id = self.request.user.user_org_id
        global_user = isGlobalUser(self.request)
        if self.request.user.user_type_slug != global_user:
            return ExcludeText.objects.filter(etext_is_delete=0).filter(etext_org_id=org_id)
        else:
            return ExcludeText.objects.filter(etext_is_delete=0)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.etext_id)

        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_ExcludeTextEdit?ETID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_ExcludeTextDel?ETID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        else:
            return super(ExcludeTextJSON, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(etext_id__icontains=search) | Q(etext_name__icontains=search))
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
        #             ("{0}".format('OK')),
        #             escape(item.org_id),  # escape HTML for security reasons
        #             escape(item.org_name),  # escape HTML for security reasons
        #             escape(item.is_internal),  # escape HTML for security reasons
        #             escape("{0}".format('OK'))
        #             # item.get_state_display(),
        #             # item.created.strftime("%Y-%m-%d %H:%M:%S"),
        #
        #         ])
        #     return json_data
    

#Exclude Text json data

#Exclude Text Edit Request Start#

@active_user_required
def excludeTextEdit(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('ETID')
    try:
        etext_id = signing.loads(id)
        data = ExcludeText.objects.get(pk=etext_id)
    except ExcludeText.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listExcludeText')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data,
        }
        return render(request, 'itrak/IncomingEmail/edit_exclude_text.html', context)

#Exclude Text Edit Request End#

#Exclude Text Update Request Start
@active_user_required
def excludeTextUpdate(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('etext_id')
        
        # Instead of having an error on your server,
        # your user will get a 404 meaning that he tries to access a non existing resource.
        # data = get_object_or_404(Organization , pk = id)
        try:
            obj = ExcludeText.objects.get(pk=id)
            # return HttpResponse(obj)
        except ExcludeText.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listExcludeText')
        else:
            if 'etext_name' in request.POST and request.POST['etext_name']:
                obj.etext_name = request.POST.get('etext_name')

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Exclude Text updated.')
            return redirect('listExcludeText')
    else:
        messages.error(request, 'Request Failed! Exclude Text cannot be updated.Please try again.')
        return redirect('listExcludeText')

#Exclude Text Update Request End#


#Exclude Text Delete Request Start#

@active_user_required
def excludeTextDel(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('ETID')
    try:
        etext_id = signing.loads(id)
        obj = ExcludeText.objects.get(pk=etext_id)
    except ExcludeText.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listExcludeText')
    else:
        obj.etext_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Exclude Text deleted.')
        return redirect('listExcludeText')

#Exclude Text Delete Request End#

@active_user_required
def addKeywords(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar
    }
    return render(request, 'itrak/IncomingEmail/add_keywords.html', context)

@active_user_required
def saveKeywords(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        org_id = request.user.user_org_id
        if 'keywords_name' in request.POST and request.POST['keywords_name']:
            keywords_name = request.POST.get('keywords_name')
        if 'keywords_search_in' in request.POST and request.POST['keywords_search_in']:
            keywords_search_in = request.POST.get('keywords_search_in')
        if 'keywords_search_for' in request.POST and request.POST['keywords_search_for']:
            keywords_search_for = request.POST.get('keywords_search_for')
        obj = Keyword(
            keywords_name = keywords_name,
            keywords_search_in = keywords_search_in,
            keywords_search_for = keywords_search_for,
            keywords_org_id = org_id
        )
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Keywords added.')
        return redirect('addKeywords')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Keywords cannot be added.Please try again.')
        return redirect('addKeywords')

@active_user_required
def listKeywords(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/IncomingEmail/list_keywords.html', context)

class KeywordsJSON(BaseDatatableView):
    # The model we're going to show
    model = Keyword

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
        global_user = isGlobalUser(self.request)
        org_id = self.request.user.user_org_id
        user_id = self.request.user.id
        if self.request.user.user_type_slug != global_user:
            return Keyword.objects.filter(keywords_is_delete=0).filter(keywords_org_id=org_id)
        else:
            return Keyword.objects.filter(keywords_is_delete=0)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.keywords_id)

        if column == 'action':
            # escape HTML for security reasons
            return '<a href="Admin_KeywordsEdit?KWID=' + str(rid) + '"><i class="fa fa-pencil"></i></a> | <a href="#" data-href="Admin_KeywordsDel?KWID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'keywords_search_in':
            if row.keywords_search_in == 1:
                return "Subject"
            else:
                return "From Address"
        elif column == 'keywords_search_for':
            if row.keywords_search_for == 1:
                return "Exact Match"
            else:
                return "Contains"
        else:
            return super(KeywordsJSON, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(keywords_id__icontains=search) | Q(keywords_name__icontains=search))
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
    

#Exclude Text json data

def keywordsEdit(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('KWID')
    try:
        keywords_id = signing.loads(id)
        data = Keyword.objects.get(pk=keywords_id)
    except Keyword.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not data:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listKeywords')
    else:
        load_sidebar = get_sidebar(request)
        context = {
            'sidebar': load_sidebar,
            'data': data,
        }
        return render(request, 'itrak/IncomingEmail/edit_keywords.html', context)

def keywordsUpdate(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        id = request.POST.get('keywords_id')
        try:
            obj = Keyword.objects.get(pk=id)
            # return HttpResponse(obj)
        except Keyword.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('listKeywords')
        else:
            if 'keywords_name' in request.POST and request.POST['keywords_name']:
                obj.keywords_name = request.POST.get('keywords_name')
            if 'keywords_search_in' in request.POST and request.POST['keywords_search_in']:
                obj.keywords_search_in = request.POST.get('keywords_search_in')
            if 'keywords_search_for' in request.POST and request.POST['keywords_search_for']:
                obj.keywords_search_for = request.POST.get('keywords_search_for')

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Keywords updated.')
            return redirect('listKeywords')
    else:
        messages.error(request, 'Request Failed! Keywords cannot be updated.Please try again.')
        return redirect('listKeywords')

def keywordsDel(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('KWID')
    try:
        keywords_id = signing.loads(id)
        obj = Keyword.objects.get(pk=keywords_id)
    except Keyword.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('listKeywords')
    else:
        obj.keywords_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Keywords deleted.')
        return redirect('listKeywords')

@active_user_required
def emailTokens(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    commandTokens = CommandToken.objects.filter(ct_is_delete=0)
    fieldTokens = FieldToken.objects.filter(ft_is_delete=0).filter(ft_org_id = request.user.user_org_id)
    context = {
        'sidebar': load_sidebar,
        'commandTokens': commandTokens,
        'fieldTokens': fieldTokens,
    }
    return render(request, 'itrak/IncomingEmail/email_tokens.html', context)

@csrf_exempt
def getModalCommadToken(request):
    if request.method == 'POST':
        commandToken = CommandToken.objects.filter(ct_id=request.POST.get('ct_id')).first()
        context = {
            'commandToken': commandToken,
        }
        return render(request, 'itrak/IncomingEmail/command_token_modal.html', context)

def updateCommandToken(request):
    if request.method == 'POST':
        id = request.POST.get('ct_id')
        try:
            obj = CommandToken.objects.get(pk=id)
            # return HttpResponse(obj)
        except CommandToken.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('emailTokens')
        else:
            if 'ct_token_identifier' in request.POST and request.POST['ct_token_identifier']:
                obj.ct_token_identifier = request.POST.get('ct_token_identifier')

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Command Token updated.')
            return redirect('emailTokens')
    else:
        messages.error(request, 'Request Failed! Command Token cannot be updated.Please try again.')
        return redirect('emailTokens')

@csrf_exempt
def getModalFieldToken(request):
    if request.method == 'POST':
        fieldToken = FieldToken.objects.filter(ft_id=request.POST.get('ft_id')).first()
        context = {
            'fieldToken': fieldToken,
        }
        return render(request, 'itrak/IncomingEmail/field_token_modal.html', context)

def updateFieldToken(request):
    if request.method == 'POST':
        id = request.POST.get('ft_id')
        try:
            obj = FieldToken.objects.get(pk=id)
            # return HttpResponse(obj)
        except FieldToken.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        # If Object Response is Empty
        if not obj:
            messages.success(request, 'Request Failed! No Record Found.')
            return redirect('emailTokens')
        else:
            if 'ft_token_identifier' in request.POST and request.POST['ft_token_identifier']:
                obj.ft_token_identifier = request.POST.get('ft_token_identifier')

            obj.save()
            # return HttpResponse('Success')
            messages.success(request, 'Request Succeed! Field Token updated.')
            return redirect('emailTokens')
    else:
        messages.error(request, 'Request Failed! Field Token cannot be updated.Please try again.')
        return redirect('emailTokens')

@active_user_required
def saveFieldToken(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST':
        if 'ft_token_identifier' in request.POST and request.POST['ft_token_identifier']:
            ft_token_identifier = request.POST.get('ft_token_identifier')
        if 'ft_field_name' in request.POST and request.POST['ft_field_name']:
            ft_field_name = request.POST.get('ft_field_name')
        obj = FieldToken(
            ft_field_name = ft_field_name,
            ft_token_identifier = ft_token_identifier,
            ft_is_deletable = 1,
            ft_is_active = 1,
            ft_org_id = request.user.user_org_id
        )
        obj.save()
        # return HttpResponse('Success')
        messages.success(request, 'Request Succeed! Field Token added.')
        return redirect('emailTokens')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! Keywords cannot be added.Please try again.')
        return redirect('emailTokens')

def deleteFieldToken(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('FTID')
    try:
        obj = FieldToken.objects.get(pk=id)
    except FieldToken.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('emailTokens')
    else:
        obj.ft_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Field Token deleted.')
        return redirect('emailTokens')

@active_user_required
def blockedAttachments(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    context = {
        'sidebar': load_sidebar,
    }
    return render(request, 'itrak/IncomingEmail/blocked_attachments.html', context)
    
@csrf_exempt
def getModalAttachment(request):
    if request.method == 'POST':
        context = {
        }
        return render(request, 'itrak/IncomingEmail/attachment_modal.html', context)

def saveBlockedAttachemts(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.method == 'POST' and len(request.FILES) != 0:
        if 'upload_attachemt' in request.FILES:
            myfile = request.FILES['upload_attachemt']
            size = myfile.size/1000
            if size > 1000:
                file_size = str(round((size/1000), 2)) + 'MB'
            else:
                file_size = str(round(size, 2)) + 'KB'
            newattach = BlockedAttachment(
                ba_upload_attachment = myfile, 
                ba_file_name = myfile, 
                ba_file_size = file_size, 
                ba_attach_created_by_id = request.user.id,
                ba_org_id = request.user.user_org_id
            )
            newattach.save()
            messages.success(request, 'Request Succeed! file uploaded successfully.')
            return redirect('blockedAttachments')
    else:
        messages.error(request, 'Request Failed! Attachment cannot be submitted.Please try again.')
        return redirect('blockedAttachments')

class BlockedAttachmentsJSON(BaseDatatableView):
    # The model we're going to show
    model = BlockedAttachment

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
        return BlockedAttachment.objects.filter(ba_is_delete=0).filter(ba_org_id = self.request.user.user_org_id)

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.ba_id)

        if column == 'action':
            # escape HTML for security reasons
            return '<a href="#" data-href="Admin_blockedAttachmentsDel?BAID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        elif column == 'ba_created_at':
            if row.ba_created_at is not None:
                local_dt = row.ba_created_at
                return datetime.strptime(str(local_dt),'%Y-%m-%d %H:%M:%S.%f%z').strftime('%m/%d/%Y %I:%M %p') 
        else:
            return super(BlockedAttachmentsJSON, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(ba_file_name__icontains=search))
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
    
def deleteBlockedAttachments(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    id = request.GET.get('BAID')
    ba_id = signing.loads(id)
    try:
        obj = BlockedAttachment.objects.get(pk=ba_id)
    except BlockedAttachment.DoesNotExist:
        return render_to_response('itrak/page-404.html')
    # If Object Response is Empty
    if not obj:
        messages.success(request, 'Request Failed! No Record Found.')
        return redirect('blockedAttachments')
    else:
        obj.ba_is_delete = 1
        obj.save()
        messages.success(request, 'Request Success! Attachment deleted.')
        return redirect('blockedAttachments')

@active_user_required
def viewLog(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    load_sidebar = get_sidebar(request)
    if request.method == 'POST':
        org_id = request.user.user_org_id
        print(org_id)
        user_id = request.user.id
        global_user = isGlobalUser(request)  
        received_from = request.POST.get('received_from') if 'received_from' in request.POST else '' 
        received_to = request.POST.get('received_to') if 'received_to' in request.POST else '' 
        processed_from = request.POST.get('processed_from') if 'processed_from' in request.POST else '' 
        processed_to = request.POST.get('processed_to') if 'processed_to' in request.POST else '' 
        account_id = request.POST.get('account_id') if 'account_id' in request.POST else '' 
        account_id_like = account_id+'%'
        sender_email = request.POST.get('sender_email') if 'sender_email' in request.POST else '' 
        sender_email_like = sender_email+'%'
        # status = request.POST.get('status') if 'status' in request.POST else 0
        status_message = request.POST.get('status_message') if 'status_message' in request.POST else '' 
        status_message_like = status_message+'%'
        subject = request.POST.get('subject') if 'subject' in request.POST else '' 
        subject_like = subject+'%'
        attachment_name = request.POST.get('attachment_name') if 'attachment_name' in request.POST else '' 
        attachment_name_like = attachment_name+'%'
        # if request.user.user_type_slug != global_user:
        records = MailBoxEmailViewLog.objects.raw('''SELECT a.*, b.* FROM AT_MailBoxEmailViewLogs a INNER JOIN AT_MailBoxs b ON b.mail_box_id = a.evl_mail_box_id
        and a.evl_received_date between %s and %s
        and a.evl_processed_date between %s and %s
        and b.account_id like %s
        and a.evl_from like %s
        and a.evl_subject like %s
        and a.evl_org_id = %s
        '''
        , [received_from, received_to, processed_from, processed_to, account_id_like, sender_email_like, subject_like, org_id]
        )
        # else:
        #     records = MailBoxEmailViewLog.objects.raw('''SELECT a.*, b.* FROM AT_MailBoxEmailViewLogs a INNER JOIN AT_MailBoxs b ON b.mail_box_id = a.evl_mail_box_id
        #         and a.evl_received_date between %s and %s
        #         and a.evl_processed_date between %s and %s
        #         and b.account_id like %s
        #         and a.evl_from like %s
        #         and a.evl_subject like %s
        #     '''
        #     , [received_from, received_to, processed_from, processed_to, account_id_like, sender_email_like, subject_like]
        #     )
        context = {
            'received_from': received_from,
            'received_to': received_to,
            'processed_from': processed_from,
            'processed_to': processed_to,
            'account_id': account_id,
            'sender_email': sender_email,
            'status_message': status_message,
            'subject': subject,
            'sender_email': sender_email,
            'attachment_name': attachment_name,
            'MailBoxEmailViewLogData': records,
        }
        return render(request, 'itrak/IncomingEmail/view_log.html', context)
        
    else:
        records = MailBoxEmailViewLog.objects.raw('''
        SELECT a.*, b.* FROM AT_MailBoxEmailViewLogs a INNER JOIN AT_MailBoxs b ON b.mail_box_id = a.evl_mail_box_id
        ''')
        context = {
            'sidebar': load_sidebar,
            'MailBoxEmailViewLogData': records,
        }
        return render(request, 'itrak/IncomingEmail/view_log.html', context)

class MailBoxEmailViewLogJSON(BaseDatatableView):
    # The model we're going to show
    model = MailBoxEmailViewLog

    # define the columns that will be returned
    # columns = ['action', 'org_id', 'org_name', 'is_internal', 'display']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    # order_columns = ['evl_id']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        # return MailBoxEmailViewLog.objects.filter(evl_id=1)
        org_id = self.request.user.user_org_id
        user_id = self.request.user.id
        global_user = isGlobalUser(self.request) 
        if request.user.user_type_slug != global_user:
            records = MailBoxEmailViewLog.objects.raw('''
            SELECT a.*, b.*,count(*) as count
            FROM AT_MailBoxEmailViewLogs a
            INNER JOIN AT_MailBoxs b ON b.mail_box_id = a.evl_mail_box_id
            where evl_org_id = '''+"'"+org_id+"'"+'''
            Order by a.evl_id desc
            ''')
        else:
            records = MailBoxEmailViewLog.objects.raw('''
            SELECT a.*, b.*,count(*) as count
            FROM AT_MailBoxEmailViewLogs a
            INNER JOIN AT_MailBoxs b ON b.mail_box_id = a.evl_mail_box_id
            Order by a.evl_id desc
            ''')
        return records

    def render_column(self, row, column):
        # We want to render user as a custom column
        rid = signing.dumps(row.evl_id)
        if column == 'action':
            # escape HTML for security reasons
            return '<a href="#" data-href="Admin_blockedAttachmentsDel?BAID=' + str(rid) + '" data-toggle="modal" data-target="#confirm-delete"><i class="fa fa-trash-o"></a>'
        # elif column == 'ba_created_at':
        #     convertedTimeZone  = getDateTimeByTimezone('2020-05-28 21:53:00.0000000',row.ba_attach_created_by_id)
        #     return convertedTimeZone
        else:
            return super(MailBoxEmailViewLogJSON, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(evl_id__icontains=search))
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

@csrf_exempt
def viewLogBody(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    if request.is_ajax():
        if request.method == 'POST':
            evl_id=request.POST.get('evl_id')
            to = MailBoxEmailViewLog.objects.get(evl_id=evl_id).evl_to
            subject = MailBoxEmailViewLog.objects.get(evl_id=evl_id).evl_subject
            body = MailBoxEmailViewLog.objects.get(evl_id=evl_id).evl_body
            # print(data)
            return HttpResponse(json.dumps({'to':to, 'subject': subject, 'body' : body}), content_type="application/json")

#GET ALL VIEW LOG DATA FOR EJ2 GRID
@csrf_exempt
def getAllViewLogData(request):
    if request.user.admin != 1:
        return render(request, 'itrak\page-404.html')
    org_id = request.user.user_org_id
    user_id = request.user.id
    global_user = isGlobalUser(request) 
    # if request.user.user_type_slug != global_user:
    SQL = '''
    SELECT * 
    FROM AT_MailBoxEmailViewLogs a
    INNER JOIN AT_MailBoxs m ON m.mail_box_id = a.evl_mail_box_id
    WHERE 1=1 and evl_org_id = '''+"'"+str(org_id)+"'"+'''
    '''
    # else:
    #     SQL = '''
    #         SELECT * 
    #         FROM AT_MailBoxEmailViewLogs a
    #         INNER JOIN AT_MailBoxs m ON m.mail_box_id = a.evl_mail_box_id
    #         WHERE 1=1
    #     '''
    filtersArray = []
    if request.GET.get('received_from') != '' and request.GET.get('received_to') != '':
        SQL += 'AND a.evl_received_date between %s and %s '
        received_from = request.GET.get('received_from')
        received_to = request.GET.get('received_to')
        received_from = received_from+' 00:00:00'
        received_to = received_to+' 23:59:59'
        filtersArray.append(received_from)
        filtersArray.append(received_to)
    elif request.GET.get('received_from') != '' and request.GET.get('received_to') == '':
        SQL += 'AND a.evl_received_date > %s '
        received_from = request.GET.get('received_from')
        received_from = received_from+' 00:00:00'
        filtersArray.append(received_from)
    elif request.GET.get('received_from') == '' and request.GET.get('received_to') != '':
        SQL += 'AND a.evl_received_date < %s '
        received_to = request.GET.get('received_to')
        received_to = received_to+' 23:59:59'
        filtersArray.append(received_to)

    if request.GET.get('processed_from') != '' and request.GET.get('processed_to') != '':
        SQL += 'AND a.evl_processed_date between %s and %s '
        processed_from = request.GET.get('processed_from')
        processed_to = request.GET.get('processed_to')
        processed_from = processed_from+' 00:00:00'
        processed_to = processed_to+' 23:59:59'
        filtersArray.append(processed_from)
        filtersArray.append(processed_to)
    elif request.GET.get('processed_from') != '' and request.GET.get('processed_to') == '':
        SQL += 'AND a.evl_processed_date > %s '
        processed_from = request.GET.get('processed_from')
        processed_from = processed_from+' 00:00:00'
        filtersArray.append(processed_from)
    elif request.GET.get('processed_from') == '' and request.GET.get('processed_to') != '':
        SQL += 'AND a.evl_processed_date < %s '
        processed_to = request.GET.get('processed_to')
        processed_to = processed_to+' 23:59:59'
        filtersArray.append(processed_to)

    if request.method == 'POST' and 'account_id' in request.GET  and request.GET.get('account_id') != '':
        SQL += 'AND M.account_id LIKE %s '
        account_id = request.GET.get('account_id')
        account_id = '%'+account_id+'%'
        filtersArray.append(account_id)
    if request.method == 'POST' and 'sender_email' in request.GET  and request.GET.get('sender_email') != '':
        SQL += 'AND a.evl_from like %s '
        sender_email = request.GET.get('sender_email')
        sender_email = '%'+sender_email+'%'
        filtersArray.append(sender_email)
    if request.method == 'POST' and 'status' in request.GET  and request.GET.get('status') != '0':
        SQL += 'AND a.evl_status = %s '
        status = request.GET.get('status')
        filtersArray.append(status)
    if request.method == 'POST' and 'status_message' in request.GET  and request.GET.get('status_message') != '':
        SQL += 'AND a.evl_status_message like %s '
        status_message = request.GET.get('status_message')
        status_message = '%'+status_message+'%'
        filtersArray.append(status_message)
    if request.method == 'POST' and 'subject' in request.GET  and request.GET.get('subject') != '':
        SQL += 'AND a.evl_subject like %s '
        subject = request.GET.get('subject')
        subject = '%'+subject+'%'
        filtersArray.append(subject)
    if request.method == 'POST' and 'attachment_name' in request.GET  and request.GET.get('attachment_name') != '':
        SQL += 'AND a.evl_attachment like %s '
        attachment_name = request.GET.get('attachment_name')
        attachment_name = '%'+attachment_name+'%'
        filtersArray.append(attachment_name)
    # return HttpResponse(SQL)
    resultArray = []
    if len(filtersArray) > 0:
        resultData = MailBoxEmailViewLog.objects.raw(SQL,filtersArray)
        if resultData:
            for resultData in resultData:
                resutlCurrentRecord = {}
                resutlCurrentRecord['mail_server'] = resultData.mail_server
                resutlCurrentRecord['account_id'] = resultData.account_id
                resutlCurrentRecord['evl_from'] = resultData.evl_from
                resutlCurrentRecord['evl_subject'] = resultData.evl_subject
                # resutlCurrentRecord['evl_body'] = resultData.evl_body
                resutlCurrentRecord['evl_body'] =  '<a href="javascript:void(0)" evl_id="'+str(resultData.evl_id)+'" id="email_body" data-toggle="modal" data-target="#viewEmailBodyModal">View Body</a>'
                resutlCurrentRecord['evl_received_date'] = resultData.evl_received_date.strftime("%m/%d/%Y")
                resutlCurrentRecord['evl_processed_date'] = resultData.evl_processed_date.strftime("%m/%d/%Y")
                resultArray.append(resutlCurrentRecord)
        
    
    return HttpResponse(json.dumps(resultArray), content_type="application/json")

def createUserFromTemplate(request, user_temp_id, user_email, login_permit):
    serverTimeZone = 'America/Los_Angeles'
    userTemplateData = UserTemplate.objects.get(pk=user_temp_id)
    obj = User(
        user_type = 2, 
        username = user_email, 
        first_name = userTemplateData.first_name, 
        last_name = userTemplateData.last_name, 
        display_name = userTemplateData.display_name, 
        login_permit = login_permit, 
        phone_no = '', 
        email = user_email, 
        mob_sms_email = '', 
        suppress_email = False, 
        user_dep_id = None, 
        user_org_id = None, 
        user_client_id = None, 
        address1 = '', 
        address2 = '', 
        user_city = '', 
        user_state = '', 
        user_zip_code = None, 
        user_country = '', 
        user_time_zone = serverTimeZone
    )
    obj.default_password = randomString = get_random_string(length=8)
    obj.set_password(randomString)
    obj.save()
    
    m = MySettings(
        m_user_id = obj.id, 
        m_time_zone = serverTimeZone, 
        m_default_page = "", 
        m_ticket_screen = 0,
        m_redirect_to = "",
        m_dashboard_reload = 0, 
        m_show_reload = 'False', 
        m_phone = None, 
        m_email = None,
        m_mob_sms_email = None, 
        m_address1 = None,
        m_address2 = None, 
        m_user_city = None,
        m_user_state = None, 
        m_user_zip_code = None, 
        m_user_country = None
    )
    m.save()

    #EMAIL SENT on USER ADD Start#
    if login_permit:
        subject = 'Login Credentials'
        to = []
        to.append(obj.email)
        support_url = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/'
        dynamic = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/resetPassword?userID=' + obj.username + '&password=' + randomString + ''

        params = {'company_name': 'ATG Extra', 'firstname': obj.first_name, 'lastname': obj.last_name,
                    'default_password': randomString, 'action_url': dynamic,
                    'support_url': support_url}  # Paramters for change in Template Context

        message = render_to_string('itrak/Email/Email-Template/signup_mail.html', params)

        send_email(to=to, subject=subject, message=message)
    
    # EMAIL SENT on USER ADD End#
    getAllMenuPermissionsOfUserTemplate = UserTemplateMenuPermission.objects.filter(user_id = user_temp_id).exclude(menu_id__isnull=True).values_list('menu_id',flat=True)
    getAllSubMenuPermissionsOfUserTemplate = UserTemplateMenuPermission.objects.filter(user_id = user_temp_id).exclude(submenu_id__isnull=True).values_list('submenu_id',flat=True)
    getAllUserTemplateActionPermission = UserTemplateActionPermission.objects.filter(user_id = user_temp_id).values_list('perm_act_id',flat=True)
    getAllUserTemplateSubActionPermission = UserTemplateSubActionPermission.objects.filter(user_id = user_temp_id).values_list('sub_act_id',flat=True)

    #ADD USER MENU AND SUB-MENU PERMISSIONS
    for getAllMenuPermissionsOfUserTemplate in getAllMenuPermissionsOfUserTemplate:
        permit_obj = UserMenuPermissions(user_id= obj.id, menu_id = getAllMenuPermissionsOfUserTemplate)
        permit_obj.save()
    for getAllSubMenuPermissionsOfUserTemplate in getAllSubMenuPermissionsOfUserTemplate:
        permit_obj = UserMenuPermissions(user_id= obj.id, submenu_id = getAllSubMenuPermissionsOfUserTemplate)
        permit_obj.save()

    #ADD USER ACTION AND SUB-ACTION PERMISSIONS
    for getAllUserTemplateActionPermission in getAllUserTemplateActionPermission:
        user_act_obj = UserActionPermission(user_id=obj.id, perm_act_id=getAllUserTemplateActionPermission)
        user_act_obj.save()
    for getAllUserTemplateSubActionPermission in getAllUserTemplateSubActionPermission:
        user_act_obj = UserSubActionPermission(user_id=obj.id, sub_act_id=getAllUserTemplateSubActionPermission)
        user_act_obj.save()

    # return HttpResponse(obj.id)
    return obj.id

def createUserFromOrganization(request, org_id, client_id, user_email):
    # user_email = "basit.ali@techleadz.com"
    # org_id = 1
    # client_id = 1
    serverTimeZone = 'America/Los_Angeles'
    first_name = user_email.split("@",1)[0] 
    last_name = user_email.split("@",1)[0] 
    # username = user_email.split("@",1)[0] 
    display_name = last_name+', '+first_name
    # isUserAlreadyExist = User.objects.filter(username=username).count()
    # if isUserAlreadyExist > 0:
    #     isUserAlreadyExist = isUserAlreadyExist + 1
    #     username = username+str(isUserAlreadyExist)
    # else:
    #     username = username
    
    obj = User(
        user_type = 2, #Template
        username = user_email, 
        first_name = first_name, 
        last_name = last_name, 
        display_name = display_name, 
        login_permit = False, 
        phone_no = '', 
        email = user_email, 
        mob_sms_email = '', 
        suppress_email = False, 
        user_dep_id = None, 
        user_org_id = org_id, 
        user_client_id = client_id, 
        address1 = '', 
        address2 = '', 
        user_city = '', 
        user_state = '', 
        user_zip_code = None, 
        user_country = '', 
        user_time_zone = serverTimeZone
    )
    obj.default_password = randomString = get_random_string(length=8)
    obj.set_password(randomString)
    obj.save()
    
    m = MySettings(
        m_user_id = obj.id, 
        m_time_zone = serverTimeZone, 
        m_default_page = "", 
        m_ticket_screen = 0,
        m_redirect_to = "",
        m_dashboard_reload = 0, 
        m_show_reload = 'False', 
        m_phone = None, 
        m_email = None,
        m_mob_sms_email = None, 
        m_address1 = None,
        m_address2 = None, 
        m_user_city = None,
        m_user_state = None, 
        m_user_zip_code = None, 
        m_user_country = None
    )
    m.save()

    # return HttpResponse(obj.id)
    return obj.id

#get Grand Parent of Ticket Type
def getGrandParentTicketType(request, ticket_type):
    checkLevelFive = TicketType.objects.get(ttype_id =ticket_type, ttype_is_delete = 0, ttype_is_active = 1 )
    if checkLevelFive.parent_id:
        print(checkLevelFive.parent_id)
        checkLevelFour = TicketType.objects.get(ttype_id =checkLevelFive.parent_id, ttype_is_delete = 0, ttype_is_active = 1 ) 
        if checkLevelFour.parent_id:
            checkLevelThree = TicketType.objects.get(ttype_id =checkLevelFour.parent_id, ttype_is_delete = 0, ttype_is_active = 1 )
            if checkLevelThree.parent_id:
                checkLevelTwo = TicketType.objects.get(ttype_id =checkLevelThree.parent_id, ttype_is_delete = 0, ttype_is_active = 1 )
                if checkLevelTwo.parent_id:
                    checkLevelTwo = TicketType.objects.get(ttype_id =checkLevelTwo.parent_id, ttype_is_delete = 0, ttype_is_active = 1 )
                    if not checkLevelTwo.parent_id:
                        ticket_type = checkLevelTwo.ttype_id
                else:
                    ticket_type = checkLevelTwo.ttype_id
            else:
                ticket_type = checkLevelThree.ttype_id
        else:
            ticket_type = checkLevelFour.ttype_id
    else:
        ticket_type = checkLevelFive.ttype_id
    
    return ticket_type
