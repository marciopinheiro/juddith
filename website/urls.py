#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('terms/terms-of-use', views.terms_of_use, name='terms_of_use'),
    path('terms/privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('contact', views.contact, name='contact'),
    path('contact/thanks', views.thanks_for_contact, name='thanks_for_contact'),
]
