from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.conf import settings
from vjit_network.api.models import Notification, NotificationSetting, UserNotification, NotificationTemplate, NotificationTemplateLocalization, Device
from vjit_network.api.forms import NotificationForm
# Register your models here.

ADMIN_SYSTEM_USER_ID = getattr(settings, 'ADMIN_SYSTEM_USER_ID' , 1)

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
    readonly_fields = ('is_system',)
    search_fields = ('id', 'name',)

    class notification_template_localization_inline(admin.StackedInline):
        model = NotificationTemplateLocalization
        fields = ('id', 'language', 'title_html',
                  'title_plantext', 'content_html', 'content_plantext')
        readonly_fields = ('id',)
        extra = 1

    inlines = [notification_template_localization_inline]
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request=request)
        if request.user.pk != ADMIN_SYSTEM_USER_ID:
            qs = qs.filter(is_system=False)
        return qs

    def save_model(self, request, obj : NotificationTemplate, form, change):
        obj.is_system = False
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj : NotificationTemplate):
        if obj.is_system:
            raise PermissionDenied("You don't permission to action")
        super().delete_model(request, obj)


class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('id', 'actor', 'template', 'create_at')
    list_display = ('id', 'actor','template','create_at')
    list_per_page = 10
    autocomplete_fields = ('actor', )
    filter_horizontal = ('recipients',)
    form = NotificationForm

admin.site.register(Device, DeviceAdmin)
admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
admin.site.register(Notification,NotificationAdmin)
