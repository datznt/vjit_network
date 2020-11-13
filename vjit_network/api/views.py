from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, mixins, viewsets

from django.http import FileResponse, HttpResponseNotFound
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model, logout
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination


from vjit_network.core.models import User, Site, Industry, Skill, UserSetting, Education, Experience, Student, File, Tag, BlockUser, Link, Group, GroupUser, Comment, Approval, AttachPost, Company, View, Post, Contact, VerificationCode
from vjit_network.api.models import NotificationTemplate, NotificationTemplateLocalization, Notification, UserNotification, Device
from vjit_network.api.bussines import otp_code_for_user
from vjit_network.common.mixins import LoggingViewSetMixin
from vjit_network.api import serializers, permissions, utils, filtersets

from wsgiref.util import FileWrapper
import re
# Create your views here.

MAIL_SENDER = settings.EMAIL_HOST_USER


class UserViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin, 
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-username']
    lookup_field = 'slug'
    serializer_class = serializers.EmptySerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.UserFilter
    search_fields = ('username', 'last_name', 'email')
    queryset = User.objects.all()
    permission_classes = (permissions.UserPermission,)
    serializer_classes = {
        'list': serializers.UserSerializer,
        'retrieve': serializers.UserSerializer,
        'update': serializers.UserSerializer,
        'partial_update': serializers.UserSerializer,
        'session_user': serializers.SessionUserSerializer,
        'news_feed': serializers.PostSerializer,
        'files': serializers.FileSerializer
    }

    @action(methods=['GET'], detail=False, url_path='session-user', permission_classes=[IsAuthenticated, ])
    def session_user(self, request):
        user_auth = request.user
        if not (user_auth.is_authenticated and user_auth.is_active):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        VisitLogger.increment_for_user(user=user_auth)
        user_data = self.get_serializer(user_auth).data
        serializer_data = {'user': user_data}
        return Response(data=serializer_data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='news-feed', url_name='news_feed', permission_classes=[IsAuthenticated, ])
    def news_feed(self, request):
        user_req = request.user
        groups_user_is_member = user_req.group_members.all().values_list('group', flat=True)
        blockers = BlockUser.objects.as_user(user_req, to_list_user=True)
        qs = Post.objects.select_related('create_by', 'via_type',).prefetch_related(
            'attaches', 'views', 'comments', 'via_object').filter(
                group__in=groups_user_is_member,
                public_code=Post.PublicCode.ACCEPT
        ).exclude(create_by__in=blockers).order_by("-create_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='files', permission_classes=[IsAuthenticated, ])
    def files(self, request):
        qs = request.user.files.all()
        filter_results = filtersets.FileFilterSet(request.GET, queryset=qs)
        page = self.paginate_queryset(filter_results.qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured(
                "serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {
        'login': serializers.UserLoginSerializer,
        'register': serializers.UserRegisterSerializer,
        'password_change': serializers.PasswordChangeSerializer,
        'password_reset': serializers.PasswordResetSerializer,
        'password_reset_verify': serializers.VerificationOTPSerializer,
        'password_reset_renew': serializers.PasswordRenewSerializer,
    }

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = utils.get_and_authenticate_user(**serializer.validated_data)
        data = serializers.AuthUserSerializer(
            Token.objects.get_or_create(user=user)[0]).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = utils.create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(
            Token.objects.get_or_create(user=user)[0]).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ], url_path='password-change')
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=False, url_path='password-reset', url_name='password_reset', )
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_validated = serializer.validated_data['email']
        password_reset_form = PasswordResetForm(serializer.validated_data)
        user_has_email = next(password_reset_form.get_users(email_validated))
        new_otp = otp_code_for_user(user_has_email)
        password_reset_form.send_mail(
            subject_template_name='core/password_reset_subject.txt',
            email_template_name='core/acc_password_reset_otp.html',
            from_email=MAIL_SENDER,
            to_email=email_validated,
            context={'otp': new_otp.code, 'site_name': 'VJIT Alumni'}
        )
        return Response(data={
            'expired_time': new_otp.expired_time,
            'user': new_otp.user.pk
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='password-reset/verify', url_name='password_reset_verify')
    def password_reset_verify(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_obj = serializer.save()
        token = Token.objects.get_or_create(user=otp_obj.user)[0]
        data = serializers.ForgotTokenSerializer(token).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='password-reset/renew', url_name='password_reset_renew', permission_classes=[IsAuthenticated, ])
    def password_reset_renew(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req_user: User = self.request.user
        req_user.set_password(serializer.validated_data.get('password'))
        req_user.save()
        return Response(status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured(
                "serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class UserSettingViewSet(
        mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    lookup_field = 'id'
    queryset = UserSetting.objects.all()
    serializer_class = serializers.UserSettingSerializer
    permission_classes = (permissions.UserSettingPermission,)


class GroupViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-name']
    ordering_fields = '__all__'
    lookup_field = 'slug'
    serializer_class = serializers.EmptySerializer
    serializer_classes = {
        'list': serializers.GroupSerializer,
        'create': serializers.GroupSerializer,
        'retrieve': serializers.GroupSerializer,
        'update': serializers.GroupSerializer,
        'partial_update': serializers.GroupSerializer,
        'destroy': serializers.GroupSerializer,
        'posts': serializers.PostSerializer,
        'files': serializers.FileSerializer
    }
    permission_classes = (permissions.GroupPermission,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = filtersets.GroupFilter
    search_fields = ('name', 'slug',)
    queryset = Group.objects.all()

    @action(methods=['GET'], detail=True, url_path='posts', permission_classes=[IsAuthenticated, ])
    def posts(self, request, slug=None):
        # user_req = request.user
        instance = self.get_object()
        qs = instance.posts.select_related('create_by', 'via_type', ).prefetch_related('attaches', 'views', 'comments', 'via_object').filter(
            group=instance, public_code=Post.PublicCode.ACCEPT).order_by("-create_at")
        filter_results = filtersets.PostFilter(request.GET, queryset=qs)
        page = self.paginate_queryset(filter_results.qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='files', permission_classes=[IsAuthenticated, ])
    def files(self, request, slug=None):
        instance = self.get_object()
        qs = instance.get_files()
        filter_results = filtersets.FileFilterSet(request.GET, queryset=qs)
        page = self.paginate_queryset(filter_results.qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured(
                "serializer_classes should be a dict mapping.")
        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)


class GroupUserViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-user__username']
    lookup_field = 'id'
    serializer_class = serializers.GroupUserSerializer
    permission_classes = (permissions.GroupUserPermission,)
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.GroupMemberFilter
    search_fields = ('user__username', 'user__last_name',
                     'user__email', 'user__first_name',)
    queryset = GroupUser.objects.all()


class FileViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-create_at']
    serializer_class = serializers.FileSerializer
    permission_classes = (permissions.IsMyObjectPermission,)
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.FileFilterSet
    search_fields = ('name',)
    queryset = File.objects.all()

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(create_by=self.request.user)


class PostViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        LoggingViewSetMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-create_at']
    serializer_class = serializers.PostSerializer
    queryset = (Post.objects.select_related('create_by', 'via_type',).prefetch_related(
        'attaches', 'views', 'comments', 'via_object', 'approvals'))
    permission_classes = (permissions.PostPermission,)
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.PostFilter
    search_fields = ('content', 'create_by__username', 'create_by__last_name',)


class ViewViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-create_at']
    queryset = (View.objects.select_related('create_by', 'post'))
    serializer_class = serializers.ViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.ViewFilterSet
    search_fields = ('create_by__username', 'create_by__last_name',)

    def get_queryset(self):
        qs = super().get_queryset()
        blockers = BlockUser.objects.as_user(
            self.request.user, to_list_user=True)
        qs.exclude(create_by__in=blockers)


class CommentViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['create_at']
    queryset = (Comment.objects.select_related('create_by', 'parent',
                                               'content_type').prefetch_related('content_object'))
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsMyObjectPermission,)
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.CommentFilter
    search_fields = ('create_by__username', 'create_by__last_name',)

    def perform_create(self, serializer):
        serializer.validated_data['create_by'] = self.request.user
        return super(CommentViewSet, self).perform_create(serializer)

    def get_queryset(self):
        qs = super().get_queryset()
        blockers = BlockUser.objects.as_user(
            self.request.user, to_list_user=True)
        qs.exclude(create_by__in=blockers)


class StudentViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    ordering = ['-user']
    lookup_field = 'user'
    queryset = Student.objects.all()
    permission_classes = (permissions.StudentPermission,)
    serializer_class = serializers.StudentSerializer


class CompanyViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-name']
    lookup_field = 'slug'
    queryset = Company.objects.all()
    serializer_class = serializers.CompanySerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    permission_classes = (permissions.CompanyPermission,)
    search_fields = ('name',)

    @action(methods=['GET'], detail=True, url_path='files', permission_classes=[AllowAny])
    def files(self, request, slug=None):
        instance = self.get_object()
        qs = instance.get_files()
        filter_results = filtersets.FileFilterSet(request.GET, queryset=qs)
        page = self.paginate_queryset(filter_results.qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TagViewSet(
        mixins.CreateModelMixin, mixins.RetrieveModelMixin,
        mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    lookup_field = 'id'
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SkillViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    lookup_field = 'id'
    queryset = Skill.objects.all()
    serializer_class = serializers.SkillSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    search_fields = ('name', 'id',)


class IndustryViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    lookup_field = 'id'
    queryset = Industry.objects.all()
    serializer_class = serializers.IndustrySerializer
    permission_classes = (permissions.IsAuthenticated,)


class UserNotificationViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-notification__create_at']
    queryset = (UserNotification.objects.select_related(
        "user", "notification"))
    serializer_class = serializers.UserNotificationSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    filterset_class = filtersets.UserNotificationFilterSet
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class UserDeviceViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-id']
    queryset = (Device.objects.select_related(
        "user"))
    serializer_class = serializers.DeviceSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    permission_classes = (IsAuthenticated,)
    filterset_class = filtersets.DeviceFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class LinkViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-create_at']
    queryset = (Link.objects.select_related(
        "create_by"))
    serializer_class = serializers.LinkSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)


class ContactViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ContactSerializer
    permission_classes = (AllowAny,)
    queryset = Contact.objects.all()


class BlockUserViewSet(
        mixins.ListModelMixin, mixins.UpdateModelMixin,
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    ordering = ['-block_at']
    queryset = (BlockUser.objects.select_related(
        "create_by", 'blocked_user'))
    serializer_class = serializers.BlockUserSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, OrderingFilter)
    permission_classes = (IsAuthenticated,)
    # filterset_class = filtersets.DeviceFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(create_by=self.request.user)
