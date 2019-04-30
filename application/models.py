#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class BaseAppModel(object):

    STATUS = (
        (1, 'active'),
        (0, 'inactive'),
    )

    def get_active_status_value(self):
        for value, desc in self.STATUS:
            if desc == 'active':
                return value

    def get_inactive_status_value(self):
        for value, desc in self.STATUS:
            if desc == 'inactive':
                return value

    def get_status_description(self):
        for value, desc in self.STATUS:
            if value == self.status:
                return desc


class Intent(models.Model, BaseAppModel):
    class Meta:
        verbose_name = _('intent')
        verbose_name_plural = _('intentions')

    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), null=True, blank=True)
    tag = models.SlugField(_('tag'), unique=True, max_length=50)
    feature = models.ForeignKey('Feature',
                                verbose_name=_('feature'),
                                null=True, blank=True,
                                on_delete=models.SET_NULL)
    response = models.ForeignKey('Response', verbose_name=_('response'),
                                 null=True, blank=True,
                                 on_delete=models.SET_NULL)

    status = models.IntegerField('status', choices=BaseAppModel.STATUS,
                                 default=1)
    created_by = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='intent_created_by',
                                   verbose_name=_('created by'))
    last_modified_by = models.ForeignKey(User, null=True, blank=True,
                                         on_delete=models.SET_NULL,
                                         related_name='intent_last_modified_by',
                                         verbose_name=_('last modified by'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), default=timezone.now)

    def __str__(self):
        return self.name


class Response(models.Model, BaseAppModel):
    class Meta:
        verbose_name = _('response')
        verbose_name_plural = _('responses')

    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), null=True, blank=True)
    elocutions = models.ManyToManyField('Elocution',
                                        related_name='elocution_responses')

    status = models.IntegerField('status', choices=BaseAppModel.STATUS,
                                 default=1)
    created_by = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='response_created_by',
                                   verbose_name=_('created by'))
    last_modified_by = models.ForeignKey(User, null=True, blank=True,
                                         on_delete=models.SET_NULL,
                                         related_name='response_last_modified_by',
                                         verbose_name=_('last modified by'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), default=timezone.now)

    def __str__(self):
        return self.name

    def get_response_elocution(self):
        import random
        return random.choice(self.elocutions.all()).text


class Elocution(models.Model, BaseAppModel):
    class Meta:
        verbose_name = _('elocution')
        verbose_name_plural = _('elocutions')

    intent = models.ForeignKey(Intent, null=True, blank=True,
                               on_delete=models.CASCADE)
    text = models.TextField(_('text'))

    status = models.IntegerField('status', choices=BaseAppModel.STATUS,
                                 default=1)
    created_by = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='elocution_created_by',
                                   verbose_name=_('created by'))
    last_modified_by = models.ForeignKey(User, null=True, blank=True,
                                         on_delete=models.SET_NULL,
                                         related_name='elocution_last_modified_by',
                                         verbose_name=_('last modified by'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), default=timezone.now)

    def __str__(self):
        return self.text


class Feature(models.Model, BaseAppModel):
    class Meta:
        verbose_name = _('feature')
        verbose_name_plural = _('features')

    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), null=True, blank=True)
    call = models.CharField(_('call'), max_length=200)
    error_message = models.CharField(_('error message'), null=True, blank=True,
                                     max_length=200)
    empty_message = models.CharField(_('empty message'), null=True, blank=True,
                                     max_length=200)

    status = models.IntegerField('status', choices=BaseAppModel.STATUS,
                                 default=1)
    created_by = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='feature_created_by',
                                   verbose_name=_('created by'))
    last_modified_by = models.ForeignKey(User, null=True, blank=True,
                                         on_delete=models.SET_NULL,
                                         related_name='feature_last_modified_by',
                                         verbose_name=_('last modified by'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), default=timezone.now)

    def __str__(self):
        return self.name


# Signals for models

@receiver(pre_save, sender=Intent)
def intent_change_update_at(sender, instance, **kwargs):
    instance.updated_at = timezone.now()


@receiver(pre_save, sender=Response)
def response_change_update_at(sender, instance, **kwargs):
    instance.updated_at = timezone.now()


@receiver(pre_save, sender=Elocution)
def elocution_change_updated_at(sender, instance, **kwargs):
    instance.updated_at = timezone.now()


@receiver(pre_save, sender=Feature)
def feature_change_update_at(sender, instance, **kwargs):
    instance.updated_at = timezone.now()
