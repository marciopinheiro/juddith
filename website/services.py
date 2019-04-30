#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.core.mail import send_mail


def send_contact_email(form):
    recipients = ['marciopinheiro@yahoo.com']
    subject = 'Juddith - Contact'
    message = form.cleaned_data['message']
    sender = form.cleaned_data['email']
    send_mail(subject, message, sender, recipients)
