from datetime import datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.forms import ValidationError
from django.contrib.sites.models import Site
from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField
# from address.models import AddressField
from urllib.parse import urljoin
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE
from ckeditor.fields import RichTextField
from vjit_network.core.customfields import JSONSchemaField
from vjit_network.core import manager


import json
import uuid
import os
# Create your models here.

storage = FileSystemStorage(location=settings.MEDIA_ROOT)

OTP_CODE_FROM = settings.OTP_CODE_FROM
OTP_CODE_TO = settings.OTP_CODE_TO


class EmploymentTypeChoices(models.TextChoices):
    FULL_TIME = 'full_time', _('Full-time')
    PART_TIME = 'part_time', _('Part-time')
    CONTRACT = 'contract', _('Contract')
    TEMPORARY = 'temporary', _('Temporary')
    VOLUNTEER = 'volunteer', _('Volunteer')
    INTERNSHIP = 'internship', _('Internship')


class Tag(models.Model):
    name = models.CharField(verbose_name=_('Tag name'),  max_length=255)

    def __str__(self):
        return self.name


class File(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_by = models.ForeignKey(
        verbose_name=_('Create by'), to='User', on_delete=models.CASCADE, related_name='files', default=None,
        help_text=_("Account to upload this file")
    )
    create_at = models.DateTimeField(
        verbose_name=_('Create at'), auto_now_add=True,
        help_text=_("Specify file upload time")
    )
    name = models.CharField(
        verbose_name=_('File name'), max_length=255, null=True, blank=True, default=None,
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
        help_text=_("The original file is uploaded from the client")
    )
    thumbnails = JSONField(
        verbose_name=_('Thumbnails'), encoder=json.JSONEncoder, null=True, blank=True,
        # help_text=_('Field extension of the model')
    )
    attach_posts = GenericRelation(to='AttachPost')

    class Meta:
        verbose_name = _('File')

    def has_thumbnail(self):
        return hasattr(self, 'thumbnails') and self.thumbnails is not None and len(self.thumbnails['thumbs']) > 0

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
        thumbnails = self.reverse_thumbnails()
        if not thumbnails:
            return None
        return thumbnails[-1]
        # if not self.has_thumbnail():
        #     return None
        # storage = self.raw.storage
        # default_site_setting = Site.objects.get_current()
        # relative_url = storage.url(self.thumbnails['path']) + self.thumbnails['thumbs'][-1]
        # absolute_url = urljoin(default_site_setting.domain, relative_url)
        # return absolute_url

    def __str__(self):
        return self.name


class User(AbstractUser):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = 'unknown'
    GENDER_CHOICES = [
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (UNKNOWN, _("Unknown")),
    ]
    id = models.BigAutoField(primary_key=True)
    avatar = models.OneToOneField(
        to=File,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    slug = AutoSlugField(
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
        default=False
    )
    is_student = models.BooleanField(
        default=False
    )
    is_company = models.BooleanField(
        default=False
    )
    objects = manager.UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    # def _get_unique_slug(self):
    #     slug = slugify(self.username)
    #     unique_slug = slug
    #     num = 1
    #     while User.objects.filter(slug=unique_slug).exists():
    #         unique_slug = '{}-{}'.format(slug, num)
    #         num += 1
    #     return unique_slug

    @property
    def full_name(self):
        full_name = ' '.join([self.first_name, self.last_name])
        full_name = full_name.strip()
        return full_name if full_name != '' else '@'+self.username

    @property
    def channel_name(self):
        return "user_%s" % self.id


class BlockUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
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
    is_active = models.BooleanField(
        verbose_name=_('Is active'),
        default=True
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


class O2OUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        # default=None
    )

    class Meta:
        abstract = True


class VerificationCode(O2OUser):
    code = models.IntegerField(
        verbose_name=_('Code OTP')
    )
    expired_time = models.DateTimeField(
        null=False,
        blank=False
    )
    is_enable = models.BooleanField(
        default=True
    )

    def __str__(self):
        return str(self.code)


class Link(models.Model):
    id = models.BigAutoField(primary_key=True)
    create_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='links',
    )
    create_at = models.DateTimeField(
        auto_now_add=True
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    link = models.URLField(
        max_length=255
    )
    title = models.CharField(
        null=True,
        blank=True,
        max_length=255
    )
    name = models.CharField(
        null=True,
        blank=True,
        max_length=100
    )
    picture = models.URLField(
        max_length=500,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.link


class UserSetting(O2OUser):
    # user = models.OneToOneField(
    #     User
    # )
    language = models.CharField(
        verbose_name=_('Language'),
        max_length=2, default='vi',
        choices=settings.LANGUAGES,
    )

    class Meta:
        verbose_name = _('User setting')
        verbose_name_plural = _('User settings')


class Skill(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        default=None,
    )
    create_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='skills_created',
    )
    create_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('Skill')

    def __str__(self):
        return self.name


class Student(O2OUser):
    """Profile of account with type are user.

    fields:
        user    -- this is the user account
        gender  -- this is the gender of the user
        extra   -- this is extention field of the model
    """

    phone = PhoneNumberField(
        null=True,
        blank=True
    )
    birth_date = models.DateField(
        null=True,
        blank=True
    )
    address = models.CharField(
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

    def __str__(self):
        return _("student - ") + self.user.username

    @staticmethod
    def autocomplete_search_fields():
        return ("user__username__icontains",
                "user__first_name__icontains",
                "user__last_name__icontains",
                "user__email__icontains",)


class Experience(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )
    student = models.ForeignKey(
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
        'Company',
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


class Education(models.Model):
    START_YEAR_CHOICES = list(
        reversed([(r, r) for r in range(1900, datetime.now().year+1)]))
    END_YEAR_CHOICES = list(
        reversed([(r, r) for r in range(1900, datetime.now().year+8)]))
    id = models.BigAutoField(
        primary_key=True
    )
    student = models.ForeignKey(
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
        max_length=10,
        null=True,
        blank=True
    )
    student_code = models.CharField(
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


class GroupUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='group_members',
        default=None,
    )
    group = models.ForeignKey(
        to='Group', on_delete=models.CASCADE,
        related_name='group_members',
        default=None,
    )
    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
        auto_now_add=True,
    )
    is_active = models.BooleanField(
        verbose_name=_('Is active'), default=True
    )

    class Meta:
        unique_together = ['user', 'group']
        verbose_name = _('Join the group')
        verbose_name_plural = _('Join the groups')


class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    create_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='admin_groups',
        default=None,
    )
    create_at = models.DateTimeField(
        auto_now_add=True,
    )
    banner = models.OneToOneField(
        to=File,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    name = models.CharField(
        max_length=200,
        default=None,
    )
    slug = AutoSlugField(
        populate_from='name',
        unique_with=['name'],
        unique=True,
        editable=True
    )
    description = RichTextField(
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
        default=0,
    )
    posts_count = models.IntegerField(
        default=0,
    )
    # summary = JSONSchemaField(
    #     schema='schemas/group.summary.json', default=dict, blank=True)

    class Meta:
        verbose_name = _('Group')

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


class View(models.Model):
    id = models.BigAutoField(primary_key=True)
    create_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='views',
        default=None,
    )
    create_at = models.DateTimeField(
        auto_now_add=True,
    )
    post = models.ForeignKey(
        to='Post',
        on_delete=models.CASCADE,
        related_name='views',
        default=None,
    )

    class Meta:
        verbose_name = _('View')
        unique_together = ('create_by', 'post')


class Comment(models.Model):
    limit = models.Q(app_label='core', model='post')
    id = models.BigAutoField(primary_key=True)
    create_by = models.ForeignKey(
        verbose_name=_('Create by'),
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        default=None,
    )
    create_at = models.DateTimeField(
        auto_now_add=True,
    )
    content_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=limit,
        on_delete=models.CASCADE,
    )
    object_id = models.BigIntegerField()
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
        default=0
    )
    # summary = JSONSchemaField(
    #     schema='schemas/comment.summary.json', default=dict, blank=True)

    class Meta:
        verbose_name = _('Comment')

    @property
    def childrens(self):
        query_result = Comment.objects.filter(
            parent=self).order_by('-timestamp')
        return query_result

    def update_summary(self):
        replies_count = self.childrens.count()
        self.replies_count = replies_count


class Industry(models.Model):
    name = models.CharField(
        verbose_name=_('Name'), max_length=255, default=None,
        help_text=('The name of the industry')
    )

    def __str__(self):
        return self.name


class Company(O2OUser):
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
    create_at = models.DateTimeField(
        auto_now_add=True,
    )
    logo = models.OneToOneField(
        to=File,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="companies_logo"
    )
    banner = models.OneToOneField(
        to=File,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="companies_banner"
    )
    name = models.CharField(
        max_length=140,
    )
    slug = AutoSlugField(
        populate_from='name',
        unique_with=['name'],
        unique=True,
        editable=True,
        blank=True
    )
    industry = models.ForeignKey(
        to=Industry,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    founded = models.IntegerField(
        default=timezone.now().year,
        validators=(MinValueValidator(
            0), MaxValueValidator(timezone.now().year)),
        null=True,
        blank=True
    )
    overview = RichTextField(
        null=True,
        blank=True,
    )
    company_type = models.CharField(
        max_length=2,
        choices=ENTERPRISE_TYPE,
        default=None,
    )
    slogan = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        default=None
    )
    phone = PhoneNumberField(
        default=None
    )
    address = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    site_url = models.URLField(
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


class Post(SafeDeleteModel):

    _safedelete_policy = SOFT_DELETE

    limit = models.Q(app_label='core', model='student') | models.Q(
        app_label='core', model='company') | models.Q(
        app_label='core', model='user')

    class PublicCode(models.TextChoices):
        ACCEPT = 'accept',  _('Accept')  # admin_accept: t, user_accept: t
        # admin_accept: f, user_accept: t
        WAITING = 'waiting', _('Awaiting approval')
        DISSENT = 'dissent', _('Dissent')  # admin_accept: f, user_accept: f

    id = models.BigAutoField(primary_key=True)

    create_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        null=True, related_name='posts',
    )
    group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        related_name='posts',
        # default=None
    )
    public_code = models.CharField(
        max_length=30,
        choices=PublicCode.choices,
        default=PublicCode.WAITING,
    )
    create_at = models.DateTimeField(
        verbose_name=_('Create at'),
        auto_now_add=True,
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
        default=0,
    )
    comments_count = models.IntegerField(
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


class Approval(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    id = models.BigAutoField(
        primary_key=True
    )
    user_accept = models.BooleanField(
        default=True
    )
    admin_accept = models.BooleanField(
        default=False
    )
    user_reason = models.TextField(
        null=True,
        blank=True,
    )
    admin_reason = models.TextField(
        null=True,
        blank=True,
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        default=None,
        related_name='approvals'
    )
    create_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-id']

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


class AttachPost(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    id = models.BigAutoField(primary_key=True)
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


def get_type(classes):
    try:
        if isinstance(classes, int):
            return ContentType.objects.get(pk=classes)
        return ContentType.objects.get_for_model(classes)
    except:
        return None


class Contact(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )
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
    create_at = models.DateTimeField(
        auto_now_add=True
    )


class VisitLogger(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
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