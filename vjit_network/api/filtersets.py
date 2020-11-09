from django_filters import rest_framework as filters

from vjit_network.core.models import Comment, User, View, Group, GroupUser, Post, File, User
from vjit_network.api.models import Device, UserNotification


class CommentFilter(filters.FilterSet):
    parent__isnull = filters.BooleanFilter(
        field_name='parent', lookup_expr='isnull')

    class Meta:
        model = Comment
        fields = ['create_by', 'create_at', 'parent',
                  'parent__isnull', 'content', 'content_type', 'object_id']


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',]


class ViewFilterSet(filters.FilterSet):
    class Meta:
        model = View
        fields = ['create_by', 'post']


class GroupFilter(filters.FilterSet):
    class Meta:
        model = Group
        fields = ['name', 'slug',
                  # 'group_user_users__user',
                  # 'group_user_users__is_admin'
                  ]


class GroupMemberFilter(filters.FilterSet):

    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = GroupUser
        fields = ['group', 'user', 'is_active', ]


class PostFilter(filters.FilterSet):
    attaches__content_type = filters.NumberFilter(
        field_name='attaches__content_type')

    class Meta:
        model = Post
        fields = ['create_by', 'via_type', 'public_code',
                  'via_id', 'create_at', 'content']

class FileFilterSet(filters.FilterSet):
    size__gte = filters.NumberFilter(field_name='size', lookup_expr='gte')
    size__lte = filters.NumberFilter(field_name='size', lookup_expr='lte')
    name__icontains = filters.CharFilter(
        field_name='name', lookup_expr='icontains')
    mimetype__istartswith = filters.CharFilter(
        field_name='mimetype', lookup_expr='istartswith')
    create_at = filters.DateRangeFilter(
        field_name='create_at', lookup_expr='date')
    create_by = filters.NumberFilter(field_name='create_by')

    class Meta:
        model = File
        fields = ["size__gte", "size__lte", "name__icontains",
                  "mimetype__istartswith", "create_at", "create_by"]


class UserNotificationFilterSet(filters.FilterSet):
    user = filters.NumberFilter(field_name="user")

    class Meta:
        model = UserNotification
        fields = ['user', ]


class DeviceFilterSet(filters.FilterSet):
    user = filters.NumberFilter(field_name='user')

    class Meta:
        model = Device
        fields = ['user']