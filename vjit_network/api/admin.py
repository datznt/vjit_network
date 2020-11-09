from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django.contrib.contenttypes.models import ContentType
from vjit_network.api.models import Notification, NotificationSetting, UserNotification, NotificationTemplate, NotificationTemplateLocalization, Device
# Register your models here.


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'device',)
    search_fields = ('user', 'device', 'country_code')

    class notification_setting_inline(admin.StackedInline):
        model = NotificationSetting
        readonly_fields = ('id',)
        extra = 1

    inlines = [notification_setting_inline]
    list_per_page = 10


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    # date_hierarchy = 'create_at'
    search_fields = ('id', 'name',)

    class notification_template_localization_inline(admin.StackedInline):
        model = NotificationTemplateLocalization
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
        model = UserNotification
        fields = ('user', 'is_read')
        # readonly_fields = ('id',)
        autocomplete_fields = ('user',)
        # extra = 1

    inlines = [user_notification_inline]

admin.site.register(Device, DeviceAdmin)
admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
admin.site.register(Notification,NotificationAdmin)
