from functools import reduce
from django.db.models.signals import (post_save, post_delete, pre_save)
from django.dispatch import receiver
from django.conf import settings
from vjit_network.core.models import Comment, Post, User
from vjit_network.api.models import UserNotification, Notification, NotificationTemplate
from vjit_network.api import serializers
from vjit_network.api.push_notification import send
from vjit_network.api.utils import NotificationBuilder
from onesignal import OneSignal, DeviceNotification

notify = OneSignal(settings.ONESIGNAL_APP_ID, settings.ONESIGNAL_REST_API_KEY)

TEMPLATE_COMMENT = 4
TEMPLATE_COMMENT_REPLY = 5
TEMPLATE_POST_ACCEPT_ALL_MEMBER = 6
TEMPLATE_POST_ACCEPT_CREATE_BY = 8
TEMPLATE_POST_WAITING = 7
TEMPLATE_POST_DISSENT = 9


@receiver(post_save, sender=Notification)
def notification_on_post_save(sender, instance, created, **kwargs):
    if not created and instance.is_publish:
        send(instance)


@receiver(post_save, sender=Comment)
def comment_on_create_or_update(sender, instance, created, **kwargs):
    if not created:
        return
    if isinstance(instance.content_object, Post):
        if instance.parent is None:
            notification_recipient = instance.content_object.create_by
        else:
            notification_recipient = instance.parent.create_by
        if notification_recipient == instance.create_by:
            return
        notification_actor = instance.create_by
        if instance.parent is None:
            notification_template_id = TEMPLATE_COMMENT
            payload_fields = ['id', 'content', 'object_id']
        else:
            notification_template_id = TEMPLATE_COMMENT_REPLY
            payload_fields = ['id', 'content', 'object_id', 'parent']

        notification_payload = serializers.CommentSerializer(
            instance, fields=payload_fields).data

        NotificationBuilder.push(
            actor=notification_actor,
            template_id=notification_template_id,
            payload=notification_payload,
            recipients=[notification_recipient]
        )


@receiver(pre_save, sender=Post)
def post_on_pre_save(sender, instance, raw, **kwargs):
    instance.update_fields = []
    # inject update_fields to instance send to post_save
    if not instance._state.adding:
        # instance in updating
        origin = Post.objects.get(id=instance.id)
        is_public_code_changed = origin.public_code != instance.public_code
        if is_public_code_changed:
            instance.update_fields.append('public_code')


@receiver(post_save, sender=Post)
def post_on_post_save(sender, instance, created, **kwargs):
    post_fields = {
        'fields': ['id', 'content', 'icon', 'title',
                   'sub_title', 'group.id', 'group.name', 'group.slug'],
        'expand': ['group']
    }
    notification_payload = serializers.PostSerializer(
        instance, **post_fields).data
    if created:
        system_admins = User.objects.filter(is_staff=True, is_active=True)
        NotificationBuilder.push(
            actor=instance.create_by,
            template_id=TEMPLATE_POST_WAITING,
            payload=notification_payload,
            recipients=system_admins
        )
    else:
        if "public_code" not in instance.update_fields:
            return
        if instance.public_code == Post.PublicCode.ACCEPT:
            # send to all members in group
            group_members = instance.group.group_members
            users_in_group = group_members.filter(
                is_active=True).exclude(user=instance.create_by)

            NotificationBuilder.push(
                actor=instance.create_by,
                template_id=TEMPLATE_POST_ACCEPT_ALL_MEMBER,
                payload=notification_payload,
                recipients=users_in_group
            )

            # send to post create by
            NotificationBuilder.push(
                actor=instance.create_by,
                template_id=TEMPLATE_POST_ACCEPT_CREATE_BY,
                payload=notification_payload,
                recipients=[instance.create_by]
            )
        elif instance.public_code == Post.PublicCode.DISSENT:
            NotificationBuilder.push(
                actor=instance.create_by,
                template_id=TEMPLATE_POST_DISSENT,
                payload=notification_payload,
                recipients=[instance.create_by]
            )
