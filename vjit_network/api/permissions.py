from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    DjangoModelPermissions,
    BasePermission,
    DjangoModelPermissionsOrAnonReadOnly,
    SAFE_METHODS
)

from vjit_network.core import models


class CustomDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class IsMyObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.create_by and request.user == obj.create_by


class GroupPermission(IsAuthenticated):
    pass
    # def has_permission(self, request, view):
    #     if request.user and request.user.is_authenticated:
    #         return True
    #     if view.action == 'retrieve':
    #         return True
    #     return False

    # def has_object_permission(self, request, view, obj):
    #     if request.method in SAFE_METHODS:
    #         if not (request.user and request.user.is_authenticated):
    #             return obj.setting.allow_other_system_see_info
    #         return True
    #     return obj.group_members.filter(user=request.user, is_admin=True, admin_accepted=True, user_accepted=True).exists()


class GroupUserPermission(CustomDjangoModelPermissions):
    pass
    # def has_object_permission(self, request, view, obj):
    #     if request.method in SAFE_METHODS:
    #         return True
    #     return request.user == obj.user or obj.group.group_members.filter(user=request.user, is_admin=True).exists()


class UserPermission(CustomDjangoModelPermissions):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if not (request.user and request.user.is_authenticated):
                return obj.setting.allow_other_system_see_your_profile
            return True
        return request.user == obj

class UserSettingPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class GroupSettingPermission(BasePermission):
    def has_permission(self, request, view):
        return view.action in ['partial_update', 'update']

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        has_permission = obj.group.group_members.filter(
            user=request.user, is_admin=True, admin_accepted=True, user_accepted=True).exists()
        return has_permission

class StudentPermission(IsAuthenticated):
    pass

class CompanyPermission(IsAuthenticated):
    pass
    # def has_permission(self, request, view):
    #     if view.action == 'retrieve':
    #         return True
    #     return request.user and request.user.is_authenticated

    # def has_object_permission(self, request, view, obj):
    #     if request.method in SAFE_METHODS:
    #         if not (request.user and request.user.is_authenticated):
    #             return obj.setting.allow_other_system_see_info
    #         return True
    #     return request.user == obj.create_by


class CompanySettingPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return request.user == obj.company.create_by


class PostPermission(IsAuthenticated):
    pass
    # def has_permission(self, request, view):
    #     if request.user and request.user.is_authenticated:
    #         return True
    #     if view.action == 'retrieve':
    #         return True
    #     return False

    # def has_object_permission(self, request, view, obj):
    #     if request.method in SAFE_METHODS:
    #         if not (request.user and request.user.is_authenticated):
    #             return obj.create_by.setting.allow_other_system_see_your_posts
    #         return True
    #     if isinstance(obj.content_object, models.Group):
    #         group = obj.content_object
    #         has_admin_group_permission = group.group_members.filter(
    #             user=request.user,
    #             is_admin=True,
    #             admin_accepted=True,
    #             user_accepted=True
    #         ).exists()
    #         return has_admin_group_permission or request.user == obj.create_by
    #     return request.user == obj.create_by
