from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from vjit_network.core.models import User, Site, Industry, Skill, UserSetting, Education, Experience, Student, File, Tag, BlockUser, Link, Group, GroupUser, Comment, Approval, AttachPost, Company, View, Post, Contact, VerificationCode
from vjit_network.api.models import NotificationTemplate, NotificationTemplateLocalization, Notification, UserNotification, Device
from vjit_network.common.validators import MaxValueValidator, MinValueValidator, OtpValidator
from vjit_network.api.bussines import otp_is_expired

from django.contrib.auth import password_validation
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from rest_framework_cache.registry import cache_registry
from rest_framework_cache.serializers import CachedSerializerMixin

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework_extensions.serializers import PartialUpdateSerializerMixin

from urllib.parse import urljoin
# Create your serializers class here.


class SiteSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'


class IndustrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'


class SkillSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
        expandable_fields = {
            'create_by': ('vjit_network.api.UserSerializer', {'many': False, }),
        }


class UserSettingSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = UserSetting
        fields = '__all__'


class EducationSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer):
    class Meta:
        model = Education
        # fields = '__all__'
        exclude = ['student']


class ExperienceSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer):
    class Meta:
        model = Experience
        # fields = '__all__'
        exclude = ['student']
        expandable_fields = {
            'company_lookup': ('vjit_network.api.CompanySerializer', {'many': False})
        }


class StudentSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    skills = SkillSerializer(many=True, required=False)
    # address = AddressSerializer(many=False, required=False)
    industries = IndustrySerializer(many=True, required=False)

    class Meta:
        model = Student
        fields = '__all__'
        expandable_fields = {
            'educations': (EducationSerializer, {'many': True}),
            'experiences': (ExperienceSerializer, {'many': True}),
            'skills': ('vjit_network.api.SkillSerializer', {'many': True}),
            # 'address': (AddressSerializer, {'many': False, }),
            'user': ('vjit_network.api.UserSerializer', {'many': False, }),
            'industries': ('vjit_network.api.IndustrySerializer', {'many': True, }),
        }


class FileSerializer(FlexFieldsModelSerializer):
    thumbnails = serializers.SerializerMethodField()
    lazy_thumbnail_url = serializers.ReadOnlyField()

    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ['create_by']
        expandable_fields = {
            'attach_posts': ('vjit_network.api.AttachPostSerializer', {'many': True, }),
        }

    def get_thumbnails(self, instance: File):
        if not instance.thumbnails:
            return None
        cache_key = self._thumbnails_cache_key(instance)
        thumbnails = cache.get(cache_key)
        if not thumbnails:
            storage = instance.raw.storage
            default_site_setting = Site.objects.get_current()
            relative_url = storage.url(instance.thumbnails['path'])
            absolute_url = urljoin(default_site_setting.domain, relative_url)
            thumbnails = {
                'location': absolute_url,
                'nodes': instance.thumbnails['thumbs'],
            }
            cache.set(cache_key, thumbnails, 60 * 1)
        return thumbnails

    def _thumbnails_cache_key(self, file: File):
        return file.cache_key + '_thumbs'


class TagSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(FlexFieldsModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        exclude = ['password', 'user_permissions',
                   'is_superuser', 'groups', ]
        read_only_fields = ('id', 'is_active', 'is_staff',
                            'is_student', 'is_company')
        expandable_fields = {
            'avatar': (FileSerializer, {'many': False, }),
            'company': ('vjit_network.api.CompanySerializer', {'many': False, }),
            'student': ('vjit_network.api.StudentSerializer', {'many': False, }),
            'setting': (UserSettingSerializer, {'many': False, }),
            'join_groups': ('vjit_network.api.GroupSerializer', {'many': True, }),
        }

    def _get_user_request(self):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            return request.user
        return None


class BlockUserSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = BlockUser
        deep = 1
        fields = '__all__'
        read_only_fields = ['block_at']
        expandable_fields = {
            'blocked_user': (UserSerializer, {'many': False, }),
        }


class SessionUserSerializer(UserSerializer):
    notifications_unread_count = serializers.SerializerMethodField()

    def get_notifications_unread_count(self, obj):
        return obj.notifications_user.filter(is_read=False).count()


class LinkSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'
        expandable_fields = {
            'user': (UserSerializer, {'many': False, }),
            'picture': (FileSerializer, {'many': False, }),
        }


class GroupSerializer(FlexFieldsModelSerializer):
    my_info = serializers.SerializerMethodField()
    # my_follow = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'slug', 'description', 'create_by',
                  'banner', 'my_info', 'create_at', 'members_count', 'posts_count']
        read_only_fields = ['members_count']
        expandable_fields = {
            'create_by': (UserSerializer, {'many': False, }),
            'group_members': ("GroupUserSerializer", {'many': True, }),
            # 'setting': (GroupSettingSerializer, {'many': False, }),
            'tags': (TagSerializer, {'many': True, }),
            'banner': (FileSerializer, {'many': False}),
        }

    def _get_user_request(self):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            return request.user
        return None

    def create(self, validated_data):
        invites_members = self.initial_data.pop('members', [])
        group = Group.objects.create(**validated_data)
        for user_group in invites_members:
            user_group['group'] = group.id
            serializer_user_group = GroupUserSerializer(data=user_group)
            serializer_user_group.is_valid(raise_exception=True)
            serializer_user_group.save()
        return group

    def get_my_info(self, obj):
        user_resq = self._get_user_request()
        if user_resq and user_resq.is_authenticated:
            cache_key = self._my_info_cache_key(user_resq, obj)
            group_user = cache.get(cache_key)
            if not group_user:
                group_user = obj.group_members.filter(user=user_resq).first()
                cache.set(cache_key, group_user, 60 * 1)
            if group_user:
                return GroupUserSerializer(group_user, omit=["group"]).data

    def _my_info_cache_key(self, user: User, group: Group):
        return '_'.join([user.cache_key, group.cache_key, 'myinfo'])


class GroupUserSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = GroupUser
        fields = '__all__'
        expandable_fields = {
            'user': (UserSerializer, {'many': False, }),
            'group': (GroupSerializer, {'many': False, }),
        }


class CommentChildrenSerializer(serializers.ModelSerializer):
    create_by = UserSerializer(
        many=False, fields=['id', 'full_name', 'username', 'avatar'], read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(FlexFieldsModelSerializer):
    # my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        expandable_fields = {
            'create_by': (UserSerializer, {'many': False})
        }


class ApprovalPostSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Approval
        fields = '__all__'
        read_only_fields = ['create_at']


class AttachPostSerializer(FlexFieldsModelSerializer,):
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = AttachPost
        fields = '__all__'
        expandable_fields = {
            'post': ('vjit_network.api.PostSerializer', {'many': False}),
        }

    def get_content_object(self, obj):
        _request = None
        if 'request' in self.context:
            _request = self.context.get('request', None)
        if isinstance(obj.content_object, File):
            return {
                'type': 'file',
                'data': FileSerializer(obj.content_object, fields=['id', 'mimetype', 'raw', 'thumbnails', 'name', 'create_at', 'lazy_thumbnail_url', 'size'], context={'request': _request}).data
            }
        elif isinstance(obj.content_object, Link):
            return {
                'type': 'link',
                'data': LinkSerializer(obj.content_object, fields=['id', 'picture', 'title', 'description', 'name', 'link'], context={'request': _request}).data
            }


class CompanySerializer(FlexFieldsModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        expandable_fields = {
            'logo': (FileSerializer, {'many': False}),
            'banner': (FileSerializer, {'many': False}),
            'industry': (IndustrySerializer, {'many': False}),
            # 'address': (AddressSerializer, {'many': False}),
        }


class ViewSerializer(FlexFieldsModelSerializer):

    class Meta:
        model = View
        fields = '__all__'
        expandable_fields = {
            'create_by': (UserSerializer, {'many': False})
        }


class PostSerializer(FlexFieldsModelSerializer, WritableNestedModelSerializer):
    # my_reaction = serializers.SerializerMethodField()
    # content_object = serializers.SerializerMethodField()
    my_view = serializers.SerializerMethodField()
    via_object = serializers.SerializerMethodField()
    attaches = AttachPostSerializer(many=True, required=False, read_only=False)
    icon = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    sub_title = serializers.ReadOnlyField()
    approvals = ApprovalPostSerializer(
        many=True, required=False, read_only=False)

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['views_count', 'comments_count', 'public_code', ]
        expandable_fields = {
            'create_by': (UserSerializer, {'many': False}),
            'group': (GroupSerializer, {'many': False}),
            'attaches': (AttachPostSerializer, {'many': True}),
            'approvals': (ApprovalPostSerializer, {'many': True})
        }

    def get_via_object(self, obj):
        if isinstance(obj.via_object, Student):
            return {
                'type': 'student',
                'data': StudentSerializer(obj.via_object, fields=['user.id', 'user.slug', ], expand=['user']).data
            }
        elif isinstance(obj.via_object, Company):
            return {
                'type': 'company',
                'data': CompanySerializer(obj.via_object, fields=['id', 'name', 'slug', ]).data
            }
        elif isinstance(obj.via_object, User):
            return {
                'type': 'staff',
                'data': UserSerializer(obj.via_object, fields=['id', 'full_name', 'slug', ]).data
            }

    def get_my_view(self, obj: Post):
        user_resq = self._get_user_request()
        if user_resq and user_resq.is_authenticated:
            cache_key = self._my_view_cache_key(user_resq, obj)
            viewed = cache.get(cache_key)
            if not viewed:
                viewed = obj.views.filter(create_by=user_resq).first()
                cache.set(cache_key, viewed, 60 * 1)
            if viewed:
                return ViewSerializer(viewed, omit=["post", "create_by"]).data

    def _my_view_cache_key(self, user: User, post: Post):
        return '_'.join([user.cache_key, post.cache_key, 'myview'])

    def _get_user_request(self):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            return request.user
        return None


class NotificationTemplateLocalizationSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = NotificationTemplateLocalization
        fields = '__all__'


class NotificationTemplateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        expandable_fields = {
            'localizations': (NotificationTemplateLocalizationSerializer, {'many': True})
        }


class NotificationSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        expandable_fields = {
            'template': (NotificationTemplateSerializer, {'many': False}),
            'actor': (UserSerializer, {'many': False})
        }


class UserNotificationSerializer(FlexFieldsModelSerializer):
    payload = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = '__all__'
        expandable_fields = {
            'notification': (NotificationSerializer, {'many': False}),
            'user': (UserSerializer, {'many': False})
        }

    def get_payload(self, obj: UserNotification):
        payload = obj.get_payload()
        return payload

    def get_timestamp(self, obj):
        return obj.notification.create_at


class DeviceSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
        expandable_fields = {
            'create_by': (UserSerializer, {'many': False})
        }


class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()


class AuthUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Token
        fields = '__all__'


class ForgotTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'password', 'first_name', 'last_name')

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user.exists():
            raise serializers.ValidationError("Email is already taken")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                'Current password does not match')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmptySerializer(serializers.Serializer):
    pass


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = '__all__'


class VerificationOTPSerializer(serializers.Serializer):

    user = serializers.IntegerField(
        required=True
    )
    code = serializers.IntegerField(
        required=True
    )

    def validate(self, attrs):
        otp_obj = None
        try:
            otp_obj = VerificationCode.objects.get(**attrs)
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                'otp is invalid')
        if otp_is_expired(otp_obj):
            raise serializers.ValidationError(
                'otp is expired')
        return attrs

    def save(self, **kwargs):
        user = self.validated_data.get('user')
        code = self.validated_data.get('code')
        otp_obj = VerificationCode.objects.get(
            user=user,
            code=code
        )
        otp_obj.is_enable = False
        otp_obj.save()
        return otp_obj


class PasswordRenewSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class LogoutSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
