from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django.contrib.contenttypes.models import ContentType
from vjit_network.core import models
# Register your models here.


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'device',)
    # date_hierarchy = 'create_at'
    search_fields = ('user', 'device', 'country_code')

    class notification_setting_inline(admin.StackedInline):
        model = models.NotificationSetting
        # fields = ('id', 'can_approve_members', 'can_post_in_group',
        #           'can_approve_posts', 'allow_other_system_see_info')
        readonly_fields = ('id',)
        extra = 1

    inlines = [notification_setting_inline]
    list_per_page = 10


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    # date_hierarchy = 'create_at'
    search_fields = ('id', 'name',)

    class notification_template_localization_inline(admin.StackedInline):
        model = models.NotificationTemplateLocalization
        fields = ('id', 'language', 'title_html',
                  'title_plantext', 'content_html', 'content_plantext')
        readonly_fields = ('id',)
        extra = 1

    inlines = [notification_template_localization_inline]
    list_per_page = 10


class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('id', 'actor', 'template', 'create_at')
    list_display = ('id', 'actor','template','create_at')
    list_per_page = 10

    class user_notification_inline(admin.TabularInline):
        model = models.UserNotification
        fields = ('user', 'is_read')
        # readonly_fields = ('id',)
        autocomplete_fields = ('user',)
        # extra = 1

    inlines = [user_notification_inline]

admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.NotificationTemplate, NotificationTemplateAdmin)
admin.site.register(models.Notification,NotificationAdmin)
