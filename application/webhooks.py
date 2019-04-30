#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.urls import path
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from . import integrations

app_name = 'webhooks'

urlpatterns = [
    path('telegram/' + settings.TELEGRAM_TOKEN + '/chat',
         csrf_exempt(integrations.telegram), name='telegram'),

]
