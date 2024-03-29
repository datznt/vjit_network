from django.utils.safestring import mark_safe
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django import forms
from django.utils.timezone import datetime
from django.urls import path
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from grappelli.dashboard import modules, Dashboard
from import_export.admin import ImportMixin, ImportExportActionModelAdmin
from rest_framework.authtoken.models import Token

from vjit_network.core import utils, customfields, resources, business, forms
from vjit_network.core.models import Post, File, Company, Comment, View, Industry, Tag, Skill, Link, User, Student, Group, GroupUser, Contact, get_type, UserSetting, AttachPost, Approval, Experience, Education
from vjit_network.common.utils import truncate_string, reverse

from io import BytesIO
import pandas as pd
import json

# Register your models here
EXCEL_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class ModelAdmin(admin.ModelAdmin):
    list_per_page = 10

    class Media:
        css = {
            "all": ("core/css/grappelli.css",)
        }


class CustomImportExportActionModelAdmin(ImportExportActionModelAdmin):
    import_template_name = 'core/import_export/import.html'


class MyDashboard(Dashboard):
    template = 'core/dashboard/dashboard.html'

    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)

        self.children.append(modules.Group(
            title=_("System maintenance"),
            column=1,
            collapsible=True,
            children=[
                modules.ModelList(
                    title=_('User types'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.core.models.User',
                        'vjit_network.core.models.Student',
                        'vjit_network.core.models.Company',
                    ],
                ),
                modules.ModelList(
                    title=_('Social'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.core.models.Post',
                        'vjit_network.core.models.View',
                        'vjit_network.core.models.Comment',
                        'vjit_network.core.models.Link',
                    ],
                ),
                modules.ModelList(
                    title=_('Media'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.core.models.File',
                    ],
                ),
                modules.ModelList(
                    title=_('Group'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.core.models.Group',
                        'vjit_network.core.models.GroupUser',
                    ],
                ),
                modules.ModelList(
                    title=_('Contact'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.core.models.Contact',
                    ],
                )
            ]
        ))

        self.children.append(modules.Group(
            title=_("System API"),
            column=1,
            collapsible=True,
            children=[
                modules.ModelList(
                    title=_('User devices'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.api.models.Device',
                    ],
                ),
                modules.ModelList(
                    title=_('Notification'),
                    column=1,
                    collapsible=True,
                    models=[
                        'vjit_network.api.models.NotificationTemplate',
                        'vjit_network.api.models.Notification',
                    ],
                ),
            ]
        ))

        # append a recent actions module
        self.children.append(modules.AppList(
            title=_('Administration'),
            column=2,
            collapsible=True,
            models=('django.contrib.*',),
        ))

        self.children.append(modules.RecentActions(
            title=_('Recent actions'),
            column=2,
            collapsible=True,
            limit=10,
        ))

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.min.css',
            ),
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.min.js',
            'core/js/dashboard.js',
        )


class industry_inline(admin.TabularInline):
    model = Industry
    fields = ('id', 'name')


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'last_name', 'email', 'avatar', 'gender',)}),
        (_('User type'), {
            'fields': ('is_student', 'is_company', 'is_staff',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'full_name',
                    'is_staff', 'is_student', 'is_company',)
    list_filter = ('is_company', 'is_student', 'is_staff',
                   'is_superuser', 'is_active')
    list_per_page = 10
    date_hierarchy = 'date_joined'
    exclude = ('is_online',)

    class user_setting_inline(admin.StackedInline):
        model = UserSetting
        fields = ('language',)

    class group_user_inline(admin.TabularInline):
        search_fields = ('group__name',)
        model = GroupUser
        fields = ('group', 'is_active',)
        autocomplete_fields = ('group',)

    inlines = [group_user_inline, user_setting_inline]


class GroupAdmin(CustomImportExportActionModelAdmin, ModelAdmin):
    list_display = ('name', 'slug', 'create_at', 'view_all_member',)
    date_hierarchy = 'create_at'
    search_fields = ('name', 'create_at')
    filter_horizontal = ('users',)
    readonly_fields = ('members_count', 'posts_count', 'create_by')
    resource_class = resources.GroupResource

    class group_user_inline(admin.TabularInline):
        model = GroupUser
        fields = ('user', 'is_active',)
        autocomplete_fields = ('user',)

        # filter_vertical = ('user',)

    inlines = [group_user_inline]
    list_per_page = 10

    def view_all_member(self, instance):
        ct = get_type(GroupUser)
        link = reverse('admin:{0}_{1}_{2}'.format(ct.app_label, ct.model, 'changelist'), query_kwargs={
            'group__id': instance.id
        })
        # print(link)
        return mark_safe(
            '<a href="{0}">{1} - members</a>'.format(
                link, instance.members_count)
        )

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)

    view_all_member.allow_tags = True


class PostAdmin(ModelAdmin):
    list_display = ('id', 'create_by', 'public_code', 'group', 'create_at')
    date_hierarchy = 'create_at'
    search_fields = ('id', 'create_by__username', 'content', 'create_at')
    list_filter = ('via_type', 'public_code')
    exclude = ('extra',)
    autocomplete_lookup_fields = {
        'generic': [['via_type', 'via_id'], ],
    }

    class attach_post_inline(admin.TabularInline):
        model = AttachPost
        extra = 1
        related_lookup_fields = {
            'generic': [['content_type', 'object_id'], ],
        }

    class approval_inline(admin.TabularInline):
        model = Approval
        readonly_fields = ('user_reason', 'user_accept', 'create_at')
        extra = 0
        ordering = ['id']

    autocomplete_fields = ('group', 'create_by',)
    inlines = [attach_post_inline, approval_inline]
    readonly_fields = ('create_at', 'comments_count',
                       'views_count', 'public_code', 'via_type', 'via_id', 'create_by')
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        via_type, via_id = None, None
        req_user: User = request.user
        if req_user.is_staff:
            via_type = get_type(User)
            via_id = req_user.pk
        elif req_user.is_student:
            via_type = get_type(Student)
            via_id = req_user.student.pk
        elif req_user.is_company:
            via_type = get_type(Company)
            via_id = req_user.company.pk
        if via_id is None:
            raise Exception('you need update the profile')
        obj.via_type = via_type
        obj.via_id = via_id
        obj.create_by = req_user
        super().save_model(request, obj, form, change)


class FileAdmin(ModelAdmin):
    list_display = ('id', 'name', 'mimetype', 'create_at')
    readonly_fields = ('create_at', 'name', 'size',
                       'mimetype', 'create_by', 'thumbnails')
    date_hierarchy = 'create_at'
    search_fields = ('id', 'name')
    list_filter = ('mimetype', 'create_at')
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(create_by=request.user)

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)


class LinkAdmin(ModelAdmin):
    list_display = ('id', 'create_by', 'create_at', 'name',)
    readonly_fields = ('create_by',)
    search_fields = ('id', 'title',)
    list_filter = ('name', 'link')
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)


class CompanyAdmin(ModelAdmin):
    # list_display = ('owner',  'name', )
    date_hierarchy = 'create_at'
    search_fields = ('name',)
    list_per_page = 10


class CommentAdmin(ModelAdmin):
    list_display = ('id', 'parent', 'create_by', 'create_at', 'short_content')
    search_fields = ('id', 'create_by', 'content', 'create_at')
    list_filter = ('content_type',)
    date_hierarchy = 'create_at'
    list_per_page = 10
    readonly_fields = ('replies_count', 'create_by')

    class reply_inline(GenericTabularInline):
        model = Comment
        verbose_name = _('Reply comment')
        verbose_name_plural = _('Replies comment')
        readonly_fields = ('replies_count',)
        extra = 1

    inlines = [reply_inline]

    def short_content(self, obj):
        return truncate_string(obj.content)

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)


class ContentTypeAdmin(ModelAdmin):
    list_display = ('id', 'app_label', 'model')
    readonly_fields = ('app_label', 'model',)
    actions = None

    def get_queryset(self, request):
        qs = super(ContentTypeAdmin, self).get_queryset(request)
        return qs.filter(app_label='core')


class ViewAdmin(ModelAdmin):
    list_display = ('id', 'create_by', 'post', 'create_at')
    date_hierarchy = "create_at"
    list_per_page = 10
    readonly_fields = ('create_by',)

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)


class GroupUserAdmin(ModelAdmin):
    search_fields = ('user__username', 'user__full_name',
                     'user__email', 'group__name')
    list_display = ('group', 'user', 'is_active')
    autocomplete_fields = ('group', 'user',)
    # readonly_fields = ('create_by',)

    class group_name_filter(customfields.InputFilter):
        title = _('group name')
        parameter_name = 'group__name'

        def queryset(self, request, queryset):
            value = self.value()
            if value is not None:
                return queryset.filter(group__name=value)

    class group_id_filter(customfields.InputFilter):
        title = _('group id')
        parameter_name = 'group__id'

        def queryset(self, request, queryset):
            value = self.value()
            if value is not None:
                return queryset.filter(group__id=value)

    list_filter = ('is_active', group_name_filter, group_id_filter,)

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)


class StudentAdmin(ModelAdmin):
    search_fields = ('user__username', 'user__full_name', 'user__email',)
    # list_filter = ('gender',)
    autocomplete_fields = ('user',)
    list_display = ('username', 'full_name', 'email', 'phone')
    filter_horizontal = ('skills', 'industries')
    actions = ('export_as_xlsx',)
    date_hierarchy = 'user__date_joined'

    change_list_template = 'core/students/change_list.html'
    student_import_template = "core/students/import.html"

    class experience_inlines(admin.StackedInline):
        model = Experience
        autocomplete_fields = ('company_lookup',)
        extra = 1

    class education_inlines(admin.StackedInline):
        model = Education
        extra = 1
        exclude = ('activities', 'description',)

    inlines = [experience_inlines, education_inlines, ]

    def username(self, instance):
        return instance.user.username

    username.admin_order_field = 'user__username'

    def email(self, instance):
        return instance.user.email

    email.admin_order_field = 'user__email'

    def full_name(self, instance):
        return instance.user.full_name

    full_name.admin_order_field = 'user__full_name'

    def export_as_xlsx(self, request, queryset):
        results = business.dump_student_to_xlsx(queryset)
        with BytesIO() as io:
            # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(io, engine='xlsxwriter')
            results.to_excel(writer, sheet_name='Student', index=False)
            writer.save()
            response = HttpResponse(
                io.getvalue(), content_type=EXCEL_MIME_TYPE)
            filename = int(datetime.now().timestamp())
            response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
            return response

    export_as_xlsx.short_description = _("Export Selected")

    def get_urls(self):
        urls = super().get_urls()
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        my_urls = [
            path('import/',
                 self.admin_site.admin_view(self.import_student),
                 name='{0}_{1}_{2}'.format(app_label, model_name, 'import')),
        ]
        return my_urls + urls

    def import_student(self, request):
        validated_data = []
        if request.method == 'POST':
            form = forms.StudentUploadForm(
                data=request.POST, files=request.FILES)
            if form.is_valid():
                validated_data = form.get_validated()
        else:
            form = forms.StudentUploadForm()
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            title='Import Students',
            form=form,
            validated_data=json.dumps(validated_data, cls=DjangoJSONEncoder)
        )
        return render(request, self.student_import_template, context)


class ContactAdmin(ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'phone', 'email', 'create_at')
    date_hierarchy = "create_at"


admin.site.unregister(Site)
admin.site.unregister(Token)
admin.site.register(Post, PostAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Industry)
admin.site.register(Tag)
admin.site.register(Skill)
admin.site.register(Link, LinkAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupUser, GroupUserAdmin)
admin.site.register(Contact, ContactAdmin)
