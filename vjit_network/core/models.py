from datetime import datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.urls import reverse_lazy
from django.forms import ValidationError
from django.contrib.sites.models import Site
from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField
from urllib.parse import urljoin
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE
from ckeditor.fields import RichTextField

from vjit_network.core import manager, customfields, utils
from vjit_network.common.models import BigIntPrimary, UUIDPrimaryModel, PerfectModel, CreateAtModel, IsActiveModel, CacheKeyModel
from vjit_network.common.validators import FileMaxSizeValidator

import json
import uuid
import os
# Create your models here.

storage = FileSystemStorage(location=settings.MEDIA_ROOT)

OTP_CODE_FROM = settings.OTP_CODE_FROM
OTP_CODE_TO = settings.OTP_CODE_TO
FILE_ALLOWED_EXTENTIONS = settings.FILE_ALLOWED_EXTENTIONS
FILE_MAX_SIZE = settings.FILE_MAX_SIZE


class EmploymentTypeChoices(models.TextChoices):
    FULL_TIME = 'full_time', _('Full-time')
    PART_TIME = 'part_time', _('Part-time')
    CONTRACT = 'contract', _('Contract')
    TEMPORARY = 'temporary', _('Temporary')
    VOLUNTEER = 'volunteer', _('Volunteer')
    INTERNSHIP = 'internship', _('Internship')


class Tag(PerfectModel):
    name = models.CharField(verbose_name=_('Tag name'),  max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class File(UUIDPrimaryModel, CreateAtModel, PerfectModel, CacheKeyModel):
    def directory_path(self):
        """
        0:  user id
        1:  file id
        """
        path_format = '{0}/{1}/'
        return path_format.format(str(self.create_by.pk), str(self.pk))

    def raw_directory_path(self, filename):
        filename = filename.encode('ascii', 'ignore').decode()
        return os.path.join(self.directory_path(), filename)

    def thumbnail_directory_path(self, filename):
        return os.path.join(self.directory_path(), 'thumbnails', filename)

    create_by = models.ForeignKey(
        verbose_name=_('Create by'),
        to='User',
        on_delete=models.CASCADE,
        related_name='files',
        default=None,
        help_text=_("Account to upload this file")
    )
    name = models.CharField(
        verbose_name=_('File name'),
        max_length=255,
        null=True, blank=True, default=None,
        help_text=_("The name of the file")
    )
    size = models.BigIntegerField(
        verbose_name=_('File size'), default=0, null=True, blank=True,
        help_text=_("File size on hard drive")
    )
    mimetype = models.CharField(
        verbose_name=_('Minetype'), max_length=100, null=True, blank=True,
        help_text=_(
            "A media type is a standard that indicates the nature and format of a document, file, or assortment of bytes")
    )
    raw = models.FileField(
        verbose_name=_('File raw'), max_length=500,
        storage=storage, upload_to=raw_directory_path,
        help_text=_("The original file is uploaded from the client"),
        validators=[
            FileExtensionValidator(allowed_extensions=FILE_ALLOWED_EXTENTIONS),
            FileMaxSizeValidator(max_size=FILE_MAX_SIZE)
        ]
    )
    thumbnails = JSONField(
        verbose_name=_('Thumbnails'), encoder=json.JSONEncoder, null=True, blank=True,
        # help_text=_('Field extension of the model')
    )
    attach_posts = GenericRelation(to='AttachPost')

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')

    def has_thumbnail(self):
        return all([hasattr(self, 'thumbnails'),
                    self.thumbnails is not None,
                    len(self.thumbnails['thumbs']) > 0])

    def reverse_thumbnails(self):
        if not self.has_thumbnail():
            return None
        storage = self.raw.storage
        default_site_setting = Site.objects.get_current()
        return [
            urljoin(default_site_setting.domain, storage.url(
                self.thumbnails['path']) + path)
            for path in self.thumbnails['thumbs']
        ]

    @property
    def lazy_thumbnail_url(self):
        cache_key = self._lazy_cache_key()
        thumbnails = cache.get(cache_key)
        if not thumbnails:
            thumbnails = self.reverse_thumbnails()
            cache.set(cache_key, thumbnails, 60 * 1)
        return thumbnails[-1] if thumbnails else None

    def _lazy_cache_key(self):
        return self.cache_key + '_lazy'

    def __str__(self):
        return self.name


class User(BigIntPrimary, AbstractUser, PerfectModel, CacheKeyModel):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = 'unknown'
    GENDER_CHOICES = [
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (UNKNOWN, _("Unknown")),
    ]
    full_name = models.CharField(
        verbose_name=_('Full name'),
        null=True,
        blank=True,
        max_length=131
    )
    avatar = models.OneToOneField(
        verbose_name=_('Avatar'),
        to=File,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    slug = AutoSlugField(
        verbose_name=_('Slug'),
        populate_from='username',
        unique_with=['username'],
        unique=True,
        editable=True
    )
    gender = models.CharField(
        verbose_name=_('Gender'),
        choices=GENDER_CHOICES,
        max_length=7,
        blank=True, null=True,
        default=UNKNOWN,
    )
    is_online = models.BooleanField(
        verbose_name=_('Is online'),
        default=False
    )
    is_student = models.BooleanField(
        verbose_name=_('Is student'),
        default=False
    )
    is_company = models.BooleanField(
        verbose_name=_('Is company'),
        default=False
    )
    objects = manager.UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_fullname(self):
        full_name = ' '.join([self.first_name, self.last_name])
        full_name = full_name.strip()
        return full_name if full_name != '' else '@'+self.username

    def save(self, *args, **kwargs):
        self.full_name = self.get_fullname()
        super().save(*args, **kwargs)


class BlockUser(UUIDPrimaryModel, IsActiveModel, PerfectModel):
    create_by = models.ForeignKey(
        verbose_name=_('Blocker'),
        to=User,
        on_delete=models.CASCADE,
        related_name='block_users',
    )
    blocked_user = models.ForeignKey(
        verbose_name=_('Blocked user'),
        to=User,
        on_delete=models.CASCADE,
        related_name='blocker_list',
    )
    block_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Block time'),
    )

    objects = manager.BlockUserManager()

    def __str__(self):
        return '%s block %s' % (
            self.create_by.username,
            self.blocked_user.username
        )

    def unblock(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    class Meta:
        verbose_name = _('Block user')
        verbose_name_plural = _('Block users')


class O2OUser(models.Model):
    user = models.OneToOneField(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        abstract = True


class VerificationCode(O2OUser, PerfectModel):
    code = models.IntegerField(
        verbose_name=_('Code OTP')
    )
    expired_time = models.DateTimeField(
        verbose_name=_('Expired time'),
        null=False,
        blank=False
    )
    is_enable = models.BooleanField(
        verbose_name=_('Is enable'),
        default=True
    )

    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name = _('Verification code')
        verbose_name_plural = _('Verification codes')


class Link(BigIntPrimary, CreateAtModel, PerfectModel):
    create_by = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        related_name='links',
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        blank=True
    )
    link = models.URLField(
        verbose_name=_('Link url'),
        max_length=255
    )
    title = models.CharField(
        verbose_name=_('Title'),
        null=True,
        blank=True,
        max_length=255
    )
    name = models.CharField(
        verbose_name=_('Link name'),
        null=True,
        blank=True,
        max_length=100
    )
    picture = models.URLField(
        verbose_name=_('Link picture'),
        max_length=500,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.link

    class Meta:
        verbose_name = _('Link')
        verbose_name_plural = _('Links')


class UserSetting(O2OUser, PerfectModel):
    language = models.CharField(
        verbose_name=_('Language'),
        max_length=2, default='vi',
        choices=settings.LANGUAGES,
    )

    class Meta:
        verbose_name = _('User setting')
        verbose_name_plural = _('User settings')


class Skill(BigIntPrimary, CreateAtModel, PerfectModel):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        default=None,
    )
    create_by = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='skills_created',
    )

    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')

    def __str__(self):
        return self.name


class Student(O2OUser, PerfectModel):
    """Profile of account with type are user.

    fields:
        user    -- this is the user account
        gender  -- this is the gender of the user
        extra   -- this is extention field of the model
    """

    phone = PhoneNumberField(
        verbose_name=_('Phone number'),
        null=True,
        blank=True
    )
    birth_date = models.DateField(
        verbose_name=_('Birth date'),
        null=True,
        blank=True
    )
    address = models.CharField(
        verbose_name=_('Address'),
        max_length=255,
        null=True,
        blank=True
    )
    industries = models.ManyToManyField(
        verbose_name=_('Industries'),
        to='Industry',
        related_name='student',
        blank=True,
    )
    skills = models.ManyToManyField(
        verbose_name=_('Skills'),
        to=Skill,
        related_name='student',
        blank=True,
    )
    extra = JSONField(
        encoder=json.JSONEncoder,
        null=True, blank=True,
    )

    posts = GenericRelation(
        to='Post',
        content_type_field='via_type',
        object_id_field='via_id'
    )

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')

    def __str__(self):
        return _("student - ") + self.user.username

    @staticmethod
    def autocomplete_search_fields():
        return ("user__username__icontains",
                "user__first_name__icontains",
                "user__last_name__icontains",
                "user__email__icontains",)


class Experience(BigIntPrimary, PerfectModel):
    student = models.ForeignKey(
        verbose_name=_('Student'),
        to=Student,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=255,
        default=None,
    )
    employment_type = models.CharField(
        verbose_name=_('Employment type'),
        max_length=10,
        default=None,
        null=True,
        blank=True,
        choices=EmploymentTypeChoices.choices,
    )
    company_name = models.CharField(
        verbose_name=_('Company'),
        max_length=125,
        default=None,
    )
    company_lookup = models.ForeignKey(
        verbose_name=_('Company lookup'),
        to='Company',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    location = models.CharField(
        verbose_name=_('Location'),
        max_length=255,
        null=True,
        blank=True,
    )
    is_currently_working = models.BooleanField(
        verbose_name=_('I am currently working in this role'),
        default=False
    )
    start_date = models.DateField(
        verbose_name=_('Start date'),
    )
    end_date = models.DateField(
        verbose_name=_('End date'),
        null=True,
        blank=True
    )
    headline = models.CharField(
        verbose_name=_('Headline'),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        blank=True,
    )
    the_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['the_order']
        verbose_name = _('Experience')
        verbose_name_plural = _('Experiences')


class Education(BigIntPrimary, PerfectModel):
    START_YEAR_CHOICES = list(
        reversed([(r, r) for r in range(1900, datetime.now().year+1)]))
    END_YEAR_CHOICES = list(
        reversed([(r, r) for r in range(1900, datetime.now().year+8)]))
    student = models.ForeignKey(
        verbose_name=_('Student'),
        to=Student,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    school_name = models.CharField(
        verbose_name=_('School'),
        max_length=255,
    )
    degree_name = models.CharField(
        verbose_name=_('Degree'),
        max_length=125,
        null=True,
        blank=True
    )
    field_of_study = models.CharField(
        verbose_name=_('Field of study'),
        max_length=125,
        null=True,
        blank=True
    )
    start_year = models.SmallIntegerField(
        verbose_name=_('Start year'),
        null=True,
        blank=True,
        choices=START_YEAR_CHOICES
    )
    end_year = models.SmallIntegerField(
        verbose_name=_('End year'),
        null=True,
        blank=True,
        choices=END_YEAR_CHOICES
    )
    class_id = models.CharField(
        verbose_name=_('Class id'),
        max_length=10,
        null=True,
        blank=True
    )
    student_code = models.CharField(
        verbose_name=_('Student code'),
        max_length=10,
        null=True,
        blank=True
    )
    activities = models.TextField(
        verbose_name=_('Activities and societies'),
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Education')
        verbose_name_plural = _('Educations')


class GroupUser(BigIntPrimary, IsActiveModel, PerfectModel):
    user = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        related_name='group_members',
        default=None,
    )
    group = models.ForeignKey(
        verbose_name=_('Group'),
        to='Group',
        on_delete=models.CASCADE,
        related_name='group_members',
        default=None,
    )
    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
        auto_now_add=True,
    )

    class Meta:
        unique_together = ['user', 'group']
        verbose_name = _('Join the group')
        verbose_name_plural = _('Join the groups')


class Group(BigIntPrimary, CreateAtModel, PerfectModel, CacheKeyModel):
    create_by = models.ForeignKey(
        verbose_name=_('Group'),
        to=User,
        on_delete=models.CASCADE,
        related_name='admin_groups',
        default=None,
    )
    banner = models.OneToOneField(
        verbose_name=_('Banner'),
        to=File,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=200,
        default=None,
    )
    slug = AutoSlugField(
        verbose_name=_('Slug'),
        populate_from='name',
        unique_with=['name'],
        unique=True,
        editable=True
    )
    description = RichTextField(
        verbose_name=_('Description'),
        null=True,
        blank=True,
    )
    users = models.ManyToManyField(
        to=User,
        through=GroupUser,
        through_fields=('group', 'user'),
        related_name='join_groups',
    )
    members_count = models.IntegerField(
        verbose_name=_('Members count'),
        default=0,
    )
    posts_count = models.IntegerField(
        verbose_name=_('Posts count'),
        default=0,
    )
    # summary = customfields.JSONSchemaField(
    #     schema='schemas/group.summary.json', default=dict, blank=True)

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def update_summary(self):
        self.members_count = self.group_members.filter(is_active=True).count()
        self.posts_count = self.posts.filter(
            public_code=Post.PublicCode.ACCEPT).count()

    @property
    def channel_name(self):
        return "group_%s" % self.id

    def get_files(self):
        return File.objects.filter(
            id__in=list(
                AttachPost.objects.filter(
                    post__in=self.posts.filter(
                        public_code=Post.PublicCode.ACCEPT
                    ),
                    content_type=get_type(File),
                ).values_list('object_id', flat=True)
            )
        )

    def __str__(self):
        return self.name


class View(BigIntPrimary, CreateAtModel, PerfectModel, CacheKeyModel):
    create_by = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        related_name='views',
        default=None,
    )
    post = models.ForeignKey(
        verbose_name=_('Post'),
        to='Post',
        on_delete=models.CASCADE,
        related_name='views',
        default=None,
    )

    class Meta:
        verbose_name = _('View')
        verbose_name_plural = _('Views')
        unique_together = ('create_by', 'post')


class Comment(BigIntPrimary, CreateAtModel, PerfectModel):
    limit = models.Q(app_label='core', model='post')
    create_by = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        default=None,
    )
    content_type = models.ForeignKey(
        verbose_name=_('Content type'),
        to=ContentType,
        limit_choices_to=limit,
        on_delete=models.CASCADE,
    )
    object_id = models.BigIntegerField(
        verbose_name=_('Object id'),
    )
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    parent = models.ForeignKey(
        verbose_name=_('Parent comment'),
        to='self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='childs',
        help_text=_("""If "parent" is "null" then this is "parent" comment.
        if "parent" is different from "null" then this is a "comment" child of "parent""")
    )
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Content of the comment')
    )
    replies_count = models.IntegerField(
        verbose_name=_('Replies count'),
        default=0
    )

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    @property
    def childrens(self):
        query_result = Comment.objects.filter(
            parent=self).order_by('-timestamp')
        return query_result

    def update_summary(self):
        replies_count = self.childrens.count()
        self.replies_count = replies_count


class Industry(PerfectModel):
    name = models.CharField(
        verbose_name=_('Name'), max_length=255, default=None,
        help_text=('The name of the industry')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Industry')
        verbose_name_plural = _('Industries')


class Company(O2OUser, CreateAtModel, PerfectModel):
    PUBLIC_COMPANY = 'PC'
    SELFT_EMPLOYED = 'SE'
    GOVERMENT_AGENCY = 'GA'
    NONPROFIT = 'NR'
    PRIVATELY_HELD = 'PH'
    PARTNERSHIP = 'PR'

    ENTERPRISE_TYPE = [
        (PUBLIC_COMPANY, _('Public Company')),
        (SELFT_EMPLOYED, _('Selft Employed')),
        (GOVERMENT_AGENCY, _('Goverment Agency')),
        (NONPROFIT, _('NonProfit')),
        (PRIVATELY_HELD, _('Privately Held')),
        (PARTNERSHIP, _('Partnership'))
    ]
    logo = models.OneToOneField(
        verbose_name=_('Logo'),
        to=File,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="companies_logo"
    )
    banner = models.OneToOneField(
        verbose_name=_('Banner'),
        to=File,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="companies_banner"
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=140,
    )
    slug = AutoSlugField(
        verbose_name=_('Slug'),
        populate_from='name',
        unique_with=['name'],
        unique=True,
        editable=True,
        blank=True
    )
    industry = models.ForeignKey(
        verbose_name=_('Industry'),
        to=Industry,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    founded = models.IntegerField(
        verbose_name=_('Founded'),
        default=timezone.now().year,
        validators=(MinValueValidator(
            0), MaxValueValidator(timezone.now().year)),
        null=True,
        blank=True
    )
    overview = RichTextField(
        verbose_name=_('Overview'),
        null=True,
        blank=True,
    )
    company_type = models.CharField(
        verbose_name=_('Company type'),
        max_length=2,
        choices=ENTERPRISE_TYPE,
        default=None,
    )
    slogan = models.CharField(
        verbose_name=_('Slogan'),
        max_length=255,
        default=None,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_('Email'),
        default=None
    )
    phone = PhoneNumberField(
        verbose_name=_('Phone'),
        default=None
    )
    address = models.CharField(
        verbose_name=_('Address'),
        max_length=255,
        null=True,
        blank=True
    )
    site_url = models.URLField(
        verbose_name=_('Site url'),
        null=True,
        blank=True,
        max_length=200
    )

    posts = GenericRelation(
        to='Post',
        content_type_field='via_type',
        object_id_field='via_id'
    )

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return _("company - ") + self.name

    @staticmethod
    def autocomplete_search_fields():
        return (
            "name__icontains",
            "email__icontains",
            "phone__icontains"
        )


class Post(BigIntPrimary, SafeDeleteModel, CreateAtModel, PerfectModel, CacheKeyModel):

    _safedelete_policy = SOFT_DELETE

    limit = models.Q(app_label='core', model='student') | models.Q(
        app_label='core', model='company') | models.Q(
        app_label='core', model='user')

    class PublicCode(models.TextChoices):
        ACCEPT = 'accept',  _('Accept')  # admin_accept: t, user_accept: t
        # admin_accept: f, user_accept: t
        WAITING = 'waiting', _('Awaiting approval')
        DISSENT = 'dissent', _('Dissent')  # admin_accept: f, user_accept: f

    create_by = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        null=True, related_name='posts',
    )
    group = models.ForeignKey(
        verbose_name=_('Group'),
        to=Group,
        on_delete=models.CASCADE,
        related_name='posts',
        # default=None
    )
    public_code = models.CharField(
        verbose_name=_('Public code'),
        max_length=30,
        choices=PublicCode.choices,
        default=PublicCode.WAITING,
    )
    content = models.TextField(
        verbose_name=_('Content'),
        null=True,
        blank=True,
    )
    via_type = models.ForeignKey(
        verbose_name=_('Via type'),
        to=ContentType,
        limit_choices_to=limit,
        on_delete=models.CASCADE,
    )
    via_id = models.BigIntegerField(
        verbose_name=_('Via id'),
    )
    via_object = GenericForeignKey(
        ct_field='via_type',
        fk_field='via_id'
    )
    extra = JSONField(
        verbose_name=_('Extra'),
        encoder=json.JSONEncoder,
        null=True, blank=True,
        help_text=_('Field extension of the model')
    )
    views_count = models.IntegerField(
        verbose_name=_('Views count'),
        default=0,
    )
    comments_count = models.IntegerField(
        verbose_name=_('Comments count'),
        default=0,
    )
    comments = GenericRelation(
        to=Comment
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def update_summary(self):
        comments_count = self.comments.filter(parent=None).count()
        self.comments_count = comments_count
        views_count = self.views.count()
        self.views_count = views_count

    @ property
    def icon(self):
        icon = None
        if isinstance(self.via_object, Company):
            if hasattr(self.via_object, "logo") and self.via_object.logo:
                icon = self.via_object.logo
        else:
            if hasattr(self.create_by, "avatar") and self.create_by.avatar:
                icon = self.create_by.avatar
        thumbnails_icon = icon.reverse_thumbnails() if icon else None
        return thumbnails_icon[0] if thumbnails_icon else None

    @ property
    def title(self):
        if isinstance(self.via_object, Company):
            return self.via_object.name
        else:
            return self.create_by.full_name

    @ property
    def sub_title(self):
        if self.group:
            return self.group.name


class Approval(BigIntPrimary, SafeDeleteModel, CreateAtModel, PerfectModel):
    _safedelete_policy = SOFT_DELETE
    user_accept = models.BooleanField(
        verbose_name=_('User accept'),
        default=True
    )
    admin_accept = models.BooleanField(
        verbose_name=_('Admin accept'),
        default=False
    )
    user_reason = models.TextField(
        verbose_name=_('User reason'),
        null=True,
        blank=True,
    )
    admin_reason = models.TextField(
        verbose_name=_('Admin reason'),
        null=True,
        blank=True,
    )
    post = models.ForeignKey(
        verbose_name=_('Post'),
        to=Post,
        on_delete=models.CASCADE,
        default=None,
        related_name='approvals'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('Approval')
        verbose_name_plural = _('Approvals')

    def update_public_code(self):
        if self.admin_accept and self.user_accept:
            self.post.public_code = Post.PublicCode.ACCEPT
        elif not self.admin_accept and self.user_accept:
            self.post.public_code = Post.PublicCode.WAITING
        elif (not self.admin_accept and not self.user_accept) or (self.admin_accept and not self.user_accept):
            self.post.public_code = Post.PublicCode.DISSENT
        self.post.save()

    def __str__(self):
        if self.admin_accept and self.user_accept:
            return _('Consensus opinion.')
        elif not self.admin_accept and self.user_accept:
            return _('Awaiting Approval.')
        elif (not self.admin_accept and not self.user_accept) or (self.admin_accept and not self.user_accept):
            return _('Dissent.')
        return _('Awaiting Approval.')


class AttachPost(BigIntPrimary, SafeDeleteModel, PerfectModel):
    _safedelete_policy = SOFT_DELETE
    limit = models.Q(
        app_label='core', model='file') | models.Q(
        app_label='core', model='link')
    post = models.ForeignKey(
        verbose_name=_('Post'),
        to=Post,
        on_delete=models.CASCADE,
        related_name='attaches',
        default=None,
    )
    content_type = models.ForeignKey(
        verbose_name=_('Content type'),
        to=ContentType,
        limit_choices_to=limit,
        on_delete=models.CASCADE,
        default=None,
    )
    object_id = models.CharField(
        verbose_name=_('Object id'),
        max_length=36,
        default=None,
    )
    content_object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )

    class Meta:
        verbose_name = _('Attach post')
        verbose_name_plural = _('Attaches post')
        # unique_together = ('post', 'content_type', 'object_id')

    def __str__(self):
        return str(self.pk)


class Contact(BigIntPrimary, CreateAtModel, PerfectModel):
    name = models.CharField(
        verbose_name=_('Full name'),
        max_length=255
    )
    phone = PhoneNumberField(
        verbose_name=_('Phone number'),
    )
    email = models.EmailField(
        verbose_name=_('Email'),
    )
    content = models.TextField(
        verbose_name=_('Content'),
    )

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')


class VisitLogger(UUIDPrimaryModel, PerfectModel):
    user = models.ForeignKey(
        verbose_name=_('User'),
        to=User,
        on_delete=models.CASCADE,
        related_name='visit_logger'
    )
    date = models.DateField(
        auto_now_add=True
    )
    visits_count = models.IntegerField(
        default=True
    )

    def increment_for_user(user):
        logger, created = user.visit_logger.get_or_create(date=datetime.now())
        logger.visits_count += 1
        logger.save()

    class Meta:
        verbose_name = _('Visit logger')
        verbose_name_plural = _('Visit loggers')


def get_type(classes):
    try:
        if isinstance(classes, int):
            return ContentType.objects.get_for_id(classes)
        return ContentType.objects.get_for_model(classes)
    except:
        return None
