from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from itrak.models import Organization, Client, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
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
from django.apps import apps
from django.utils.dateparse import parse_date




# Create your views here.


# login/Empty Request to the Server
def auth_login(request):
    if not request.user.is_authenticated:
        return render(request, 'itrak/Auth/login.html')
    else:
        return redirect('home')

# login/Empty Request End Here#

@csrf_exempt
#Signin Request through Sign In Page
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(username=username, password=password)
        # print(user.user_org_id)
        
        if user:
            org_status = Organization.objects.get(org_id=user.user_org_id)
            if org_status.org_is_delete == True:
                messages.error(request, 'You are Prohibited to Login.')
                return redirect('signout')
            elif user.is_delete == True:
                messages.error(request, 'Account Doesnot Exist.')
                return redirect('login')
            elif user.login_permit == False:
                messages.error(request, 'Your account has no Login Permission.')
                return redirect('login')            
            elif user.is_active:
                # request.session.set_expiry(2000)  # sets the exp. value of the session
                login(request, user) #the user is now logged in
                if request.POST.get('remember_me', None):
                    request.session.set_expiry(2000)
                try:
                    user_redirect = MySettings.objects.filter(m_user_id=request.user.id).first()
                    return HttpResponseRedirect(user_redirect.m_default_page)
                except:
                    return HttpResponseRedirect('home')
            else:
                messages.warning(request, 'Your account is inactive.')
                return redirect('login')

        else:
            messages.error(request, 'Invalid Login details given.')
            # messages.error(request, 'Someone tried to login and failed.')
            # messages.error(request, "They used username: {} and password: {}".format(username,password)
            return redirect('login')
        # else:
            
    else:
        messages.error(request, 'Request Failed. Please try again.')
        return redirect('login')

#Signin Request End Here#

#Signout Request through Sign In Page

@login_required
def signout(request):
    logout(request)
    messages.success(request, 'Log Out successfully.')
    # try:
    #     just_logged_out = request.session.get('just_logged_out', False)
    # except:
    #     just_logged_out = False
    return redirect('login')


#Signout Request End Here#


#reset Password Request through Email Start

@csrf_exempt
def resetPassword(request):
    userID = request.GET.get('userID')
    password = request.GET.get('password')
    msgID = request.GET.get('msgID')

    if request.user.is_authenticated and request.user.username == userID:
        load_sidebar = get_sidebar(request)
        try:
            obj = User.objects.get(username=request.user.username)
            obj1 = UserSentEmails.objects.get(use_sent_to_id=request.user.id)
        except User.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        context = {
            'sidebar': load_sidebar,
            'user': obj,
            'userSentEmail': obj1
        }
        return render(request, 'itrak/Auth/resetPassword.html', context)
    else:
        try:
            obj = User.objects.get(username=userID)
            obj1 = UserSentEmails.objects.get(use_id=signing.loads(msgID, salt=settings.SALT_KEY))
        except User.DoesNotExist:
            return render_to_response('itrak/page-404.html')
        return render(request, 'itrak/Auth/resetPassword1.html', {'user': obj, 'userSentEmail': obj1 })

# reset Password Request through Email End


def updatePassword(request):

    if request.method == 'POST':
        if 'id' in request.POST and request.POST['id']:
            id = request.POST.get('id')
        try:
            obj = User.objects.get(pk=id)
        except User.DoesNotExist:
            return render_to_response('itrak/page-404.html')

        Email_Time = UserSentEmails.objects.get(pk=request.POST.get('email_time'))
        delta = datetime.now(timezone.utc) - Email_Time.use_created_at
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        # a = 'Current Time: ' + str(datetime.now(timezone.utc)) + '<br>' + 'Email Time: ' + str(Email_Time.use_created_at) + '<br>' + 'Delta: ' + str(delta) + '<br>' + 'Days: ' + str(days) + '<br>' + 'Seconds: ' + str(seconds) + '<br>' + 'Hours: ' + str(hours) + '<br>' + 'Minutes: ' + str(minutes)  
        # return HttpResponse(a)

        if minutes <= 60:
            if 'password1' in request.POST and request.POST['password1']:
                # obj.default_password = request.POST.get('password1')
                obj.set_password(request.POST.get('password1'))
                obj.save()
                # return HttpResponse('Success')
                messages.success(request, 'Request Succeed! Password updated.')
                return redirect("home")
            else:
                messages.error(request, 'Password could not be updated.')
                return redirect("home")
        else: 
            messages.error(request, 'Reset Password link expired.')
            return redirect("home")
    else:
        messages.error(request, 'Password could not be updated.')
        return redirect("home")

# reset Password Request through Email End


#Validate Default Password for Uniqueness Start#

@csrf_exempt
def validatePassword(request):
    if request.is_ajax() and request.method == 'POST':
        user_id = request.POST.get('id')
        d_password = request.POST.get('password')
        # probably you want to add a regex check if the username value is valid here
        if user_id and d_password:
            obj = User.objects.get(username=user_id)
            if d_password == obj.default_password:
                response_data = {'response': 'true'}
            else:
                response_data = {'response': 'false'}

            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Default Password for Uniqueness End#


# Forgot Password Request to the Server
def forgetPassword(request):
    if not request.user.is_authenticated:
        return render(request, 'itrak/Auth/forgetPassword.html')
    else:
        return redirect('home')

# Forgot Password Request End Here#


def forgotPasswordEmail(request):
    if request.method == 'POST':
        if 'email' in request.POST and request.POST['email']:
            email = request.POST.get('email')
            # return HttpResponse(email)

        is_exist = User.objects.filter(email=email).exists()
        if is_exist:
            obj = User.objects.filter(email=email)[:1].get()
            # randomString = get_random_string(length=8)
            # obj.default_password = randomString = get_random_string(length=8)
            # obj.set_password(randomString)
            # obj.save()

            subject = 'Forgot Password'

            obj1 = UserSentEmails(
                use_subject = subject,
                use_sent_to_id = obj.id,
                use_created_by_id = obj.id
            )
            obj1.save()
            insert_id = signing.dumps(UserSentEmails.objects.latest('pk').use_id, salt=settings.SALT_KEY)

            #EMAIL SENT on USER ADD Start#
            to = []
            to.append(email)
            support_url = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/'
            dynamic = 'http://' + request.META['HTTP_HOST'] + '/portal/atg-extra/resetPassword?userID=' + obj.username + '&msgID=' + str(insert_id) + ''

            params = {'company_name': 'ATG Extra', 'firstname': obj.first_name, 'lastname': obj.last_name,
                      'action_url': dynamic,
                      'support_url': support_url}  # Paramters for change in Template Context

            message = render_to_string('itrak/Email/Email-Template/password_reset.html', params)

            send_email(to=to, subject=subject, message=message)
            # EMAIL SENT on USER ADD End#
            messages.success(request,'Request Succeed! An authentication link has been sent to the provided email address.')
            return redirect('addUser')
        else:
            messages.error(request,'Request Failed! Email entered cannot be found.')
            return redirect('addUser')
    else:
        # return HttpResponse('Fail')
        messages.error(request, 'Request Failed! User cannot be added.Please try again.')
        return redirect('addUser')
# Forgot Password Request Start#


# Send Email Request End#

# def send_email(to=['up.phpteam@gmail.com'], f_host=settings.EMAIL_HOST, f_name = settings.EMAIL_NAME,
#                f_port=settings.EMAIL_PORT, f_user=settings.EMAIL_HOST_USER, f_passwd=settings.EMAIL_HOST_PASSWORD,
#                subject='default subject', message='content message', fail_silently=False):

#     smtpserver = smtplib.SMTP(f_host, f_port)
#     smtpserver.ehlo()
#     smtpserver.starttls()
#     smtpserver.ehlo
#     smtpserver.login(f_user, f_passwd)  # from email credential

#     # email = EmailMultiAlternatives(
#     #     subject="Here's your coupon!",
#     #     body=text_body,
#     #     from_email='noreply@example.com',
#     #     to=['someone@example.com', ]
#     # )

#     # email.attach_alternative(html_body, "text/html")
#     # email.mixed_subtype = 'related'
#     #
#     # email.send(fail_silently=False)

#     msg = MIMEText(message, 'html')
#     msg['Subject'] = subject
#     msg['From'] = f_name
#     msg['To'] = to
#     smtpserver.sendmail(f_user, to, msg.as_string())  # you just need to add
#     smtpserver.close()


# Send Email Request End#



#Validate Field Adding for Uniqueness Start#

@csrf_exempt
def validateAddUnique(request):
    if request.is_ajax() and request.method == 'POST':
        fieldValue = request.POST.get('fieldValue')
        modelName = request.POST.get('tbl_name')
        modelAttr = request.POST.get('tbl_field')
        modelDlt = request.POST.get('tbl_dlt_field')
        modelInstance = apps.get_model('itrak', modelName)
        # probably you want to add a regex check if the Task value is valid here

        kwargs = {
            '{0}__{1}'.format(modelAttr, 'iexact'): fieldValue,
        }

        if fieldValue:
            if modelDlt:
                dltargs = {
                    '{0}__{1}'.format(modelDlt, 'iexact'): 1,
                }
                is_exist = modelInstance.objects.filter(**kwargs).exclude(**dltargs).exists()
            else:
                is_exist = modelInstance.objects.filter(**kwargs).exists()
            # is_exist = modelInstance.objects.filter(attrInstance=fieldValue).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Field Adding for Uniqueness End#




#Validate Field Updating for Uniqueness Start#

@csrf_exempt
def validateEditUnique(request):
    if request.is_ajax() and request.method == 'POST':
        fieldValue = request.POST.get('fieldValue')
        currentId = request.POST.get('currentId')
        modelName = request.POST.get('tbl_name')
        modelPk = request.POST.get('tbl_pk')
        modelAttr = request.POST.get('tbl_field')
        modelDlt = request.POST.get('tbl_dlt_field')
        modelInstance = apps.get_model('itrak', modelName)
        # probably you want to add a regex check if the Task value is valid here

        kwargs = {
            '{0}__{1}'.format(modelAttr, 'iexact'): fieldValue,
        }
        excludeargs = {
            '{0}__{1}'.format(modelPk, 'iexact'): currentId,
        }

        if fieldValue:
            if modelDlt:
                dltargs = {
                    '{0}__{1}'.format(modelDlt, 'iexact'): 1,
                }
                is_exist = modelInstance.objects.filter(**kwargs).exclude(**excludeargs).exclude(**dltargs).exists()
            else:
                is_exist = modelInstance.objects.filter(**kwargs).exclude(**excludeargs).exists()
            # is_exist = modelInstance.objects.filter(attrInstance=fieldValue).exists()
            response_data = { 'response': is_exist}
            return JsonResponse(response_data)
    else:
        return HttpResponse('fail')


#Validate Field Updating for Uniqueness End#
@login_required
def error_404(request):
        data = {}
        return render(request,'itrak/page-404.html', data)
@login_required
def error_500(request):
        data = {}
        return render(request,'itrak/page-404.html', data)



