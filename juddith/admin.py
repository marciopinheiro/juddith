from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import IntegrityError


# Global admin custom actions

def activate(modeladmin, request, queryset):
    rows_updated = queryset.update(status=1)

    if rows_updated == 1:
        message_bit = '1 register was'
    else:
        message_bit = f'{rows_updated} registers were'

    modeladmin.message_user(request, _(f'{message_bit} successfully enabled.'))


activate.short_description = _('Activate selected registers')


def deactivate(modeladmin, request, queryset):
    rows_updated = queryset.update(status=0)

    if rows_updated == 1:
        message_bit = '1 register was'
    else:
        message_bit = f'{rows_updated} registers were'

    modeladmin.message_user(request, _(f'{message_bit} successfully disabled.'))


deactivate.short_description = _('Deactivate selected registers')


def duplicate(modeladmin, request, queryset):

    try:
        for obj in queryset:
            obj.pk = None
            obj.created_by = request.user
            obj.last_modified_by = request.user
            obj.created_at = timezone.now()
            obj.updated_at = None
            obj.save()

        if len(queryset) == 1:
            message_bit = '1 register was'
        else:
            message_bit = f'{len(queryset)} registers were'

        modeladmin.message_user(request, _(f'{message_bit} successfully duplicated.'))
    except IntegrityError:
        modeladmin.message_user(request, _(f'Some of the records could not be duplicated because one or more '
                                f'selected records have unique values.'))


duplicate.short_description = _('Duplicate selected registers')
