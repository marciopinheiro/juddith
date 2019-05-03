#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.shortcuts import render, redirect

from .forms import ContactForm
from .services import send_contact_email


def index(request):
    return redirect('application:chat')


def terms_of_use(request):
    return render(request, 'website/terms_of_use.html')


def privacy_policy(request):
    return render(request, 'website/privacy_policy.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_contact_email(form)
            return redirect('website:thanks_for_contact')
    else:
        form = ContactForm()
    return render(request, 'website/contact.html', {'form': form})


def thanks_for_contact(request):
    return render(request, 'website/thanks_for_contact.html')
