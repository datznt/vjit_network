from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import JSONField
from django.template import Template, Context
from django.contrib.sites.models import Site
from django.core.cache import cache
from vjit_network.core.models import UserSetting
from vjit_network.common.models import UUIDPrimaryModel, PerfectModel, CacheKeyModel
from ckeditor.fields import RichTextField

import uuid
import json

User = get_user_model()


class Device(UUIDPrimaryModel, PerfectModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None, related_name='devices')
    device = models.CharField(max_length=100, null=True, blank=False)
    player_id = models.CharField(max_length=255, null=True, blank=False)
    language_code = models.CharField(max_length=2, null=True, blank=True)
    country_code = models.CharField(max_length=2, null=True, blank=True)
    active = models.BooleanField(null=True, blank=False, default=True)

    class Meta:
        unique_together = ('user', 'player_id')
        verbose_name = _('Devices')
        verbose_name_plural = _('Devices')


class NotificationSetting(UUIDPrimaryModel, PerfectModel):
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE,  default=None)
    turn_off_notification = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Notification setting')
        verbose_name_plural = _('Notification settings')


class NotificationTemplate(PerfectModel):
    name = models.CharField(
        max_length=100, verbose_name=_('Name'), default=None)
    image_field_name = models.TextField(
        verbose_name=_('Image display field'), default=None, null=True, blank=True)
    icon_field_name = models.TextField(
        verbose_name=_('Icon display field'), default=None, null=True, blank=True)
    accent_color = models.CharField(
        max_length=8, verbose_name=_('Accent color'), default=None, null=True, blank=True,
        help_text=_('Sets the circle color around your small icon that shows to the left of your notification text. Uses ARGB Hex value (E.g. FF9900FF).'))
    launch_url_format = models.CharField(
        max_length=255, verbose_name=_('Launch url format'), default=None, null=True, blank=True)
    app_url_format = models.CharField(
        max_length=255, verbose_name=_('App url format'), default=None, null=True, blank=True)
    sound = models.CharField(
        max_length=50, verbose_name=_('sound'), default=None, null=True, blank=True,
        help_text=_("The sound that plays when this notification is received by the device. If no sound is specified, the device's default sound will play."))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Notification template')
        verbose_name_plural = _('Notification templates')


class NotificationTemplateLocalization(PerfectModel):
    notification_template = models.ForeignKey(
        NotificationTemplate, on_delete=models.CASCADE, related_name='localizations')
    language = models.CharField(
        verbose_name=_('Language'), 
        max_length=2, 
        default='vi', choices=settings.LANGUAGES,
    )
    title_html = RichTextField(verbose_name=_(
        'Title format html'), default=None)
    title_plantext = models.TextField(
        verbose_name=_('Title format text'), default=None)
    content_html = RichTextField(verbose_name=_(
        'Content format html'), default=None)
    content_plantext = models.TextField(
        verbose_name=_('Content format text'), default=None)

    class Meta:
        unique_together = ('notification_template', 'language')
        verbose_name = _('Notification template localization')
        verbose_name_plural = _('Notification template localizations')


class UserNotification(UUIDPrimaryModel, PerfectModel, CacheKeyModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications_user")
    notification = models.ForeignKey(
        'Notification', on_delete=models.CASCADE, related_name="notifications_user")
    is_read = models.BooleanField(default=False)

    def get_payload(self):
        cache_key = self._payload_cache_key()
        payload = cache.get(cache_key)
        if not payload:
            notify_template = self.notification.template
            user_lang_code = UserSetting.objects.get(
                user=self.user).language
            notification_localization = notify_template.localizations.filter(
                language=user_lang_code).first()
            if not notification_localization:
                notification_localization = notify_template.localizations.first()
            sites_api_domain = Site.objects._get_site_by_id(site_id=1)
            sites_web_domain = Site.objects._get_site_by_id(site_id=2)
            sites_app_domain = Site.objects._get_site_by_id(site_id=3)
            context = Context(
                {
                    'sites': {
                        'api': sites_api_domain.domain,
                        'web': sites_web_domain.domain,
                        'app': sites_app_domain.domain
                    },
                    'actor': self.notification.actor,
                    'payload': self.notification.payload
                }
            )
            # render title notification
            template = Template(notification_localization.title_plantext)
            payload['title'] = template.render(context)
            # render title notification - html
            template = Template(notification_localization.title_html)
            payload['title_html'] = template.render(context)
            # render content notification
            template = Template(notification_localization.content_plantext)
            payload['content'] = template.render(context)
            # render content notification - html
            template = Template(notification_localization.content_html)
            payload['content_html'] = template.render(context)
            # render icon notification
            template = Template(notify_template.icon_field_name)
            payload['icon'] = template.render(context)
            # render image notification
            template = Template(notify_template.image_field_name)
            payload['image'] = template.render(context)
            # render launch url notification
            template = Template(notify_template.launch_url_format)
            payload['launch_url'] = template.render(context)
            # render app url notification
            template = Template(notify_template.app_url_format)
            payload['app_url'] = template.render(context)
            cache.set(cache_key, payload, 60 * 1)
        return payload

    def _payload_cache_key(self,):
        return '_'.join([self.user.cache_key, self.cache_key, 'payload'])

class Notification(UUIDPrimaryModel, PerfectModel):
    actor = models.ForeignKey(
        verbose_name=_('Actor'),
        to=User,
        on_delete=models.CASCADE,
        null=True, blank=False,
        to_field='id', related_name='notifications_actor',
    )
    template = models.ForeignKey(
        verbose_name=_('Notification template'),
        to=NotificationTemplate,
        on_delete=models.CASCADE,
        null=True, blank=False,
        to_field='id', related_name='notifications_created',
    )
    create_at = models.DateTimeField(
        verbose_name=_('Creation time'),
        auto_now_add=True,
    )
    payload = JSONField(
        verbose_name=_('Payload'),
        encoder=json.JSONEncoder,
        null=True, blank=True,
        help_text=_('Data send with notification')
    )
    recipients = models.ManyToManyField(
        User, related_name="notifications", through=UserNotification)
    is_publish = models.BooleanField(
        verbose_name=_('Send the message to the client'),
        default=False
    )

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
