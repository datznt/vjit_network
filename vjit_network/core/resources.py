from vjit_network.core import models
from import_export import resources, fields, widgets, instance_loaders

GROUP_IMPORT_EXPORT_FIELDS = ('id', 'create_at', 'name', 'slug',
                              'description', 'create_by')

STUDENT_IMPORT_EXPORT_FIELDS = ('user', 'username', 'password', 'last_name', 'first_name',
                                'birth_date', 'phone', 'email', 'school_name', 'class_id', 'student_code', 'field_of_study', 'start_year', 'end_year')


class GroupResource(resources.ModelResource):
    class Meta:
        model = models.Group
        fields = GROUP_IMPORT_EXPORT_FIELDS
        export_order = GROUP_IMPORT_EXPORT_FIELDS

    def before_import_row(self, row, **kwargs):
        row['create_by'] = kwargs.get('user').id


class StudentResource(resources.ModelResource):
    username = fields.Field(
        attribute='user',
        column_name='username',
        widget=widgets.ForeignKeyWidget(
            models.User, 'pk')
    )
    first_name = fields.Field(
        attribute='user',
        column_name='first_name',
        widget=widgets.ForeignKeyWidget(
            models.User, 'pk')
    )
    last_name = fields.Field(
        attribute='user',
        column_name='last_name',
        widget=widgets.ForeignKeyWidget(
            models.User, 'pk')
    )
    email = fields.Field(
        attribute='user',
        column_name='email',
        widget=widgets.ForeignKeyWidget(
            models.User, 'pk')
    )
    password = fields.Field(
        attribute='password',
        column_name='password',
        widget=widgets.CharWidget()
    )
    school_name = fields.Field(
        attribute='educations',
        column_name='school_name',
        widget=widgets.ManyToManyWidget(
            models.Education, ';', 'school_name')
    )
    class_id = fields.Field(
        attribute='educations',
        column_name='class_id',
        widget=widgets.ManyToManyWidget(
            models.Education, ';', 'class_id')
    )
    student_code = fields.Field(
        attribute='educations',
        column_name='student_code',
        widget=widgets.ManyToManyWidget(
            models.Education, ';', 'student_code')
    )
    field_of_study = fields.Field(
        attribute='educations',
        column_name='field_of_study',
        widget=widgets.ManyToManyWidget(
            models.Education, ';', 'field_of_study')
    )
    start_year = fields.Field(
        attribute='educations',
        column_name='start_year',
        widget=widgets.ManyToManyWidget(
            models.Education, ';', 'start_year')
    )
    end_year = fields.Field(
        attribute='educations',
        column_name='end_year',
        widget=widgets.ManyToManyWidget(
            models.Education, ';', 'end_year')
    )

    class Meta:
        model = models.Student
        fields = STUDENT_IMPORT_EXPORT_FIELDS
        export_order = STUDENT_IMPORT_EXPORT_FIELDS
        import_id_fields = ('user',)

    def init_instance(self, row,):
        instance = super().init_instance(row)
        user = row.get('user')
        if not user:
            username = row.get('username')
            password = row.get('password')
            first_name = row.get('first_name')
            last_name = row.get('last_name')
            user_email = row.get('email')
            if not password:
                password = username
            user = models.User.objects.create(
                username=username,
                password=password,
                email=user_email, 
                last_name=last_name,
                first_name=first_name,
                is_student=True
            )
            row['user'] = user.id
            instance.user = user
        return instance
