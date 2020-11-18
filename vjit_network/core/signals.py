from django.db.models.signals import (post_save, post_delete, pre_save)
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from vjit_network.core.utils import create_thumbnail, save_thumbnails
from vjit_network.core.models import File, User, Comment, View, Group, GroupUser, Link, Approval, Post, Company, UserSetting, Student
from vjit_network.api.utils import extraction_link

import mimetypes
import os
import shutil
import logging

logger = logging.getLogger(__name__)

THUMBNAIL_DIMENTIONS = settings.THUMBNAIL_DIMENTIONS


@receiver(post_save, sender=File)
def file_on_post_create(sender, instance, created, **kwargs):
    if created:
        dimensions = THUMBNAIL_DIMENTIONS
        has_thumb, thumb, file_type = create_thumbnail(
            instance.raw, instance.raw.storage, dimensions)
        if not has_thumb and not thumb:
            return
        instance.thumbnails = save_thumbnails(thumb, instance, file_type)
        instance.save()


@receiver(pre_save, sender=File)
def file_on_pre_save(sender, instance: File, raw, **kwargs):
    if instance.raw:
        if not instance.name and instance.raw.name:
            instance.name = instance.raw.name
        if not instance.size and instance.raw.size:
            instance.size = instance.raw.size
        if not instance.mimetype and instance.raw.file.content_type:
            instance.mimetype = instance.raw.file.content_type


@receiver(post_delete, sender=File)
def file_on_post_detete(sender, instance, **kwargs):
    try:
        storage = instance.raw.storage
        path_need_delete = instance.directory_path()
        if storage and storage.exists(path_need_delete):
            path_need_delete_os = storage.path(path_need_delete)
            instance.raw.file.close()
            del storage
            shutil.rmtree(path_need_delete_os)
    except Exception as sysexcept:
        logger.exception(sysexcept)
        # storage.delete(path_need_delete_os)


@receiver(post_save, sender=User)
def user_create_or_update(sender, created, instance, **kwargs):
    if created:
        UserSetting.objects.get_or_create(user=instance)
        if instance.is_student:
            Student.objects.get_or_create(user=instance)
        elif instance.is_company:
            Company.objects.get_or_create(user=instance)


@receiver(pre_save, sender=User)
def user_on_pre_save(sender, instance: User, raw, **kwargs):
    pass
    # if not instance.slug:
    #     instance.slug = instance._get_unique_slug()


@receiver(post_delete, sender=Comment)
def comment_on_delete(sender, instance, **kwargs):
    if instance.content_object and isinstance(instance.content_object, Post):
        try:
            if not instance.parent:
                instance.content_object.update_summary()
                instance.content_object.save()
            else:
                instance.parent.update_summary()
                instance.parent.save()
        except ObjectDoesNotExist:
            pass


@receiver(post_save, sender=Comment)
def comment_on_create_or_update(sender, created, instance, **kwargs):
    if created:
        if instance.content_object and isinstance(instance.content_object, Post):
            if not instance.parent:
                instance.content_object.update_summary()
                instance.content_object.save()
            else:
                instance.parent.update_summary()
                instance.parent.save()


@receiver(post_delete, sender=View)
def view_on_delete(sender, instance, **kwargs):
    if instance.post:
        instance.post.update_summary()
        instance.post.save()


@receiver(post_save, sender=View)
def view_on_create_or_update(sender, created, instance, **kwargs):
    if created and instance.post:
        instance.post.update_summary()
        instance.post.save()


@receiver(post_delete, sender=GroupUser)
def groupuser_on_delete(sender, instance, **kwargs):
    if instance.group:
        instance.group.update_summary()
        instance.group.save()


@receiver(post_save, sender=GroupUser)
def groupuser_on_create_or_update(sender, created, instance, **kwargs):
    if instance.group:
        instance.group.update_summary()
        instance.group.save()


@receiver(post_save, sender=Approval)
def approval_on_create_or_update(sender, created, instance, **kwargs):
    instance.update_public_code()


@receiver(post_delete, sender=Approval)
def approval_on_delete(sender, instance, **kwargs):
    pass


@receiver(post_delete, sender=Post)
def post_on_delete(sender, instance, **kwargs):
    if instance.group:
        instance.group.update_summary()
        instance.group.save()


@receiver(post_save, sender=Post)
def post_on_create_or_update(sender, created, instance, **kwargs):
    if instance.group:
        instance.group.update_summary()
        instance.group.save()


@receiver(pre_save, sender=Link)
def link_on_pre_save(sender, instance, **kwargs):
    extraction = extraction_link(instance.link)
    instance.title = extraction['title']
    instance.description = extraction['description']
    instance.picture = extraction['picture']
    instance.name = extraction['name']
