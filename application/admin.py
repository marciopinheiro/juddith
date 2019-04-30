#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Response, Intent, Elocution, Feature


class ElocutionInline(admin.TabularInline):
    model = Elocution
    exclude = ('created_by', 'last_modified_by', 'created_at', 'updated_at')
    extra = 1


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('name', 'description', 'tag', 'feature__call',
                     'response__name', 'feature__name')
    list_filter = ('status',)
    list_display = ('name', 'tag', 'get_response_name',
                    'get_feature_name', 'status')
    list_display_links = ('name',)
    list_select_related = autocomplete_fields = ('feature', 'response')
    readonly_fields = ('created_by', 'last_modified_by', 'created_at',
                       'updated_at')
    inlines = (ElocutionInline,)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.last_modified_by = request.user
        obj.save()

    def get_response_name(self, obj):
        if obj.response:
            return obj.response.name

        return '-'

    def get_feature_name(self, obj):
        if obj.feature:
            return obj.feature.name

        return '-'

    get_response_name.short_description = _('response')
    get_response_name.admin_order_field = 'response__name'

    get_feature_name.short_description = _('feature')
    get_feature_name.admin_order_field = 'feature__name'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('name', 'description')
    list_filter = ('status',)
    list_display = ('name', 'status')
    list_display_links = ('name',)
    filter_horizontal = ('elocutions',)
    readonly_fields = ('created_by', 'last_modified_by', 'created_at',
                       'updated_at')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.last_modified_by = request.user
        obj.save()


@admin.register(Elocution)
class ElocutionAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('intent__name', 'text')
    list_filter = ('status',)
    list_display = ('text', 'get_intent_name', 'status')
    list_display_links = ('text',)
    list_select_related = autocomplete_fields = ('intent',)
    readonly_fields = ('created_by', 'last_modified_by', 'created_at',
                       'updated_at')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.last_modified_by = request.user
        obj.save()

    def get_intent_name(self, obj):
        if obj.intent is not None:
            return obj.intent.name

        return '---'

    get_intent_name.short_description = _('intent')
    get_intent_name.admin_order_field = 'intent__name'


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    show_full_result_count = False
    search_fields = ('name', 'description', 'call', 'empty_message',
                     'error_message')
    list_filter = ('status',)
    list_display = ('name', 'empty_message', 'error_message', 'status')
    list_display_links = ('name',)
    readonly_fields = ('created_by', 'last_modified_by', 'created_at',
                       'updated_at')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.last_modified_by = request.user
        obj.save()
