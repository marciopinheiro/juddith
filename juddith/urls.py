#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import admin as juddith_admin

from graphene_django.views import GraphQLView
from juddith.schema import schema

# Admin Site Config

admin.site.site_header = 'Juddith'
admin.site.index_title = _('Administration')
admin.site.add_action(juddith_admin.activate)
admin.site.add_action(juddith_admin.deactivate)
admin.site.add_action(juddith_admin.duplicate)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path('webhooks/', include('application.webhooks')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('app/', include('application.urls')),
    path('', include('website.urls')),
)