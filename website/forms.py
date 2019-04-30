#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django import forms
from django.utils.translation import gettext as _


class ContactForm(forms.Form):
    email = forms.EmailField(label='your email', max_length=100)
    message = forms.CharField(label='your message', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        email_field_attrs = {'id': 'inputEmail', 'class': 'form-control',
                             'placeholder': _('your email')}

        message_field_attrs = {'id': 'inputMessage', 'class': 'form-control',
                               'rows': 5, 'placeholder': _('your message')}

        self.fields['email'].widget.attrs.update(email_field_attrs)
        self.fields['message'].widget.attrs.update(message_field_attrs)
