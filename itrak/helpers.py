# from itrak.helpers import send_email_helper
from django.conf import settings
from django.core.mail import send_mail
from itrak.models import *

SUBJECT = 'ATG Ticket Assigned'
BODY = 'Hi, An ATG Ticket is assigned to you, kindly check the description and acknowledge as well. Thanks.'
def send_email_helper(to_email):
    check = send_mail(
                    SUBJECT, #Subject
                    BODY, #Body
                    settings.EMAIL_HOST_USER,
                    [to_email]
                    )
    # print(check)
    return

def create_email_helper(assignee_name, assignee_email, ticket_id):
    Emails.objects.create(
        to_user_id=assignee_name,
        to_email=assignee_email,
        subject=SUBJECT,
        body=BODY,
        rc=0,
        ticket=ticket_id,
    )
    return 