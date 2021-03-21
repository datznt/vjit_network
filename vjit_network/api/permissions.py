from rest_framework.permissions import DjangoModelPermissions, BasePermission, SAFE_METHODS

from vjit_network.core import models


class CustomDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class FilePermission(BasePermission):
    def has_object_permission(self, request, view, obj: models.File):
        req_user: models.User = request.user
        return req_user == obj.create_by


class CommentPermission(BasePermission):
    def has_object_permission(self, request, view, obj: models.Comment):
        req_user: models.User = request.user
        return req_user == obj.create_by


class GroupPermission(BasePermission):

    def has_object_permission(self, request, view, obj: models.Group):
        req_user: models.User = request.user
        if request.method in SAFE_METHODS:
            return True
        return any([req_user.is_staff, req_user == obj.create_by])


class GroupUserPermission(BasePermission):
    def has_object_permission(self, request, view, obj: models.GroupUser):
        req_user: models.User = request.user
        if request.method in SAFE_METHODS:
            return True
        group: models.Group = obj.group
        return any([req_user.is_staff, req_user == group.create_by])


class UserPermission(BasePermission):

    def has_object_permission(self, request, view, obj: models.User):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj


class UserSettingPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True
        return False

    def has_object_permission(self, request, view, obj: models.UserSetting):
        return request.user == obj.user


class StudentPermission(BasePermission):

    def has_object_permission(self, request, view, obj: models.Student):
        req_user: models.User = request.user
        if request.method in SAFE_METHODS:
            return True
        return any([req_user.is_staff, req_user == obj.user])


class CompanyPermission(BasePermission):

    def has_object_permission(self, request, view, obj: models.Company):
        req_user: models.User = request.user
        if request.method in SAFE_METHODS:
            return True
        return any([req_user.is_staff, req_user == obj.user])


class PostPermission(BasePermission):

    # def has_permission(self, request, view):
    #     if view.action == 'list':
    #         return request.user.is_staff
    #     return True

    def has_object_permission(self, request, view, obj: models.Company):
        req_user: models.User = request.user
        if request.method in SAFE_METHODS:
            return True
        return any([req_user.is_staff, req_user == obj.create_by])
