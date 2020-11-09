from functools import reduce
from django.db.models.signals import (post_save, post_delete, pre_save)
from django.dispatch import receiver
from django.conf import settings
from asgiref.sync import async_to_sync as _
from vjit_network.core import models
from vjit_network.api import models as apimodels
from vjit_network.api import serializers
from onesignal import OneSignal, DeviceNotification

notify = OneSignal(settings.ONESIGNAL_APP_ID, settings.ONESIGNAL_REST_API_KEY)

@receiver(post_save, sender=apimodels.UserNotification)
def user_notification_on_post_create(sender, instance, created, **kwargs):
    if created:
        # render template
        payload = instance.get_payload()
        player_ids = instance.user.devices.filter(
            active=True).values_list('player_id', flat=True)

        if player_ids:
            notification = DeviceNotification(
                include_player_ids=list(player_ids),
                include_external_user_ids=[],
                contents={
                    "en": payload['content']
                }, headings={
                    "en": payload['title']
                },
                url=payload['launch_url'],
                chrome_web_icon=payload['icon'],
                firefox_icon=payload['icon'],
                chrome_web_image=payload['image'],
                small_icon=payload['icon'],
                big_picture=payload['image'],
                priority=10,
                android_channel_id=settings.ONESINGAL_ANDROID_CHANNEL_ID,
            )
            notify.send(notification)


@receiver(post_save, sender=models.Comment)
def comment_on_create_or_update(sender, instance, created, **kwargs):
    if created and instance.content_object and isinstance(instance.content_object, models.Post):
        if instance.parent is None:
            notification_recipient = instance.content_object.create_by
        else:
            notification_recipient = instance.parent.create_by
        if notification_recipient == instance.create_by:
            return
        if instance.parent is None:
            new_notification = apimodels.Notification.objects.create(
                actor=instance.create_by,
                template=apimodels.NotificationTemplate.objects.get(pk=4),
                payload=serializers.CommentSerializer(
                    instance, fields=['id', 'content', 'object_id']
                ).data
            )
        else:
            new_notification = apimodels.Notification.objects.create(
                actor=instance.create_by,
                template=apimodels.NotificationTemplate.objects.get(pk=5),
                payload=serializers.CommentSerializer(
                    instance, fields=['id', 'content', 'object_id', 'parent']
                ).data
            )
        apimodels.UserNotification.objects.create(
            user=notification_recipient,
            notification=new_notification
        )


@receiver(pre_save, sender=models.Post)
def post_on_pre_save(sender, instance, raw, **kwargs):
    instance.update_fields = []
    # inject update_fields to instance send to post_save
    if not instance._state.adding:
        # instance in updating
        origin = models.Post.objects.get(id=instance.id)
        is_public_code_changed = origin.public_code != instance.public_code
        if is_public_code_changed:
            instance.update_fields.append('public_code')


@receiver(post_save, sender=models.Post)
def post_on_create_or_update(sender, instance, created, **kwargs):
    post_fields = {
        'fields': ['id', 'content', 'icon', 'title',
                   'sub_title', 'group.id', 'group.name', 'group.slug'],
        'expand': ['group']
    }
    if created:
        if instance.public_code == models.Post.PublicCode.WAITING:
            apimodels.UserNotification.objects.create(
                user=instance.group.create_by,
                notification=apimodels.Notification.objects.create(
                    actor=instance.create_by,
                    template=apimodels.NotificationTemplate.objects.get(pk=7),
                    payload=serializers.PostSerializer(
                        instance, **post_fields).data
                )
            )
    else:
        if "public_code" in instance.update_fields:
            if instance.public_code == models.Post.PublicCode.ACCEPT:
                # send to all members in group
                new_notification = apimodels.Notification.objects.create(
                    actor=instance.create_by,
                    template=apimodels.NotificationTemplate.objects.get(pk=6),
                    payload=serializers.PostSerializer(instance, **post_fields).data
                )
                users_in_group = instance.group.group_members.filter(
                    is_active=True).exclude(user=instance.create_by)
                notification_recipients = [apimodels.UserNotification(
                    user=member.user, notification=new_notification) for member in users_in_group]
                apimodels.UserNotification.objects.bulk_create(
                    notification_recipients)
                # send to post create by
                apimodels.UserNotification.objects.create(
                    user=instance.create_by,
                    notification=apimodels.Notification.objects.create(
                        actor=instance.create_by,
                        template=apimodels.NotificationTemplate.objects.get(pk=8),
                        payload=serializers.PostSerializer(instance, **post_fields).data
                    )
                )
            elif instance.public_code == models.Post.PublicCode.WAITING:
                apimodels.UserNotification.objects.create(
                    user=instance.create_by,
                    notification=apimodels.Notification.objects.create(
                        actor=instance.create_by,
                        template=apimodels.NotificationTemplate.objects.get(pk=9),
                        payload=serializers.PostSerializer(instance, **post_fields).data
                    )
                )