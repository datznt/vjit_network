# Generated by Django 3.0 on 2020-11-11 16:08

import autoslug.fields
import ckeditor.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='approval',
            options={'ordering': ['-id'], 'verbose_name': 'Approval', 'verbose_name_plural': 'Approvals'},
        ),
        migrations.AlterModelOptions(
            name='blockuser',
            options={'verbose_name': 'Block user', 'verbose_name_plural': 'Block users'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'Contact', 'verbose_name_plural': 'Contacts'},
        ),
        migrations.AlterModelOptions(
            name='education',
            options={'verbose_name': 'Education', 'verbose_name_plural': 'Educations'},
        ),
        migrations.AlterModelOptions(
            name='experience',
            options={'ordering': ['the_order'], 'verbose_name': 'Experience', 'verbose_name_plural': 'Experiences'},
        ),
        migrations.AlterModelOptions(
            name='file',
            options={'verbose_name': 'File', 'verbose_name_plural': 'Files'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
        migrations.AlterModelOptions(
            name='industry',
            options={'verbose_name': 'Industry', 'verbose_name_plural': 'Industries'},
        ),
        migrations.AlterModelOptions(
            name='link',
            options={'verbose_name': 'Link', 'verbose_name_plural': 'Links'},
        ),
        migrations.AlterModelOptions(
            name='skill',
            options={'verbose_name': 'Skill', 'verbose_name_plural': 'Skills'},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'verbose_name': 'Student', 'verbose_name_plural': 'Students'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Tag', 'verbose_name_plural': 'Tags'},
        ),
        migrations.AlterModelOptions(
            name='verificationcode',
            options={'verbose_name': 'Verification code', 'verbose_name_plural': 'Verification codes'},
        ),
        migrations.AlterModelOptions(
            name='view',
            options={'verbose_name': 'View', 'verbose_name_plural': 'Views'},
        ),
        migrations.AlterModelOptions(
            name='visitlogger',
            options={'verbose_name': 'Visit logger', 'verbose_name_plural': 'Visit loggers'},
        ),
        migrations.AlterField(
            model_name='approval',
            name='admin_accept',
            field=models.BooleanField(default=False, verbose_name='Admin accept'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='admin_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Admin reason'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='post',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='core.Post', verbose_name='Post'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='user_accept',
            field=models.BooleanField(default=True, verbose_name='User accept'),
        ),
        migrations.AlterField(
            model_name='approval',
            name='user_reason',
            field=models.TextField(blank=True, null=True, verbose_name='User reason'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(('app_label', 'core'), ('model', 'post')), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Content type'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='create_by',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='object_id',
            field=models.BigIntegerField(verbose_name='Object id'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='replies_count',
            field=models.IntegerField(default=0, verbose_name='Replies count'),
        ),
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='company',
            name='banner',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies_banner', to='core.File', verbose_name='Banner'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(choices=[('PC', 'Public Company'), ('SE', 'Selft Employed'), ('GA', 'Goverment Agency'), ('NR', 'NonProfit'), ('PH', 'Privately Held'), ('PR', 'Partnership')], default=None, max_length=2, verbose_name='Company type'),
        ),
        migrations.AlterField(
            model_name='company',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='company',
            name='email',
            field=models.EmailField(default=None, max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='company',
            name='founded',
            field=models.IntegerField(blank=True, default=2020, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2020)], verbose_name='Founded'),
        ),
        migrations.AlterField(
            model_name='company',
            name='industry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Industry', verbose_name='Industry'),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies_logo', to='core.File', verbose_name='Logo'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=140, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='company',
            name='overview',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Overview'),
        ),
        migrations.AlterField(
            model_name='company',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(default=None, max_length=128, region=None, verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='company',
            name='site_url',
            field=models.URLField(blank=True, null=True, verbose_name='Site url'),
        ),
        migrations.AlterField(
            model_name='company',
            name='slogan',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Slogan'),
        ),
        migrations.AlterField(
            model_name='company',
            name='slug',
            field=autoslug.fields.AutoSlugField(blank=True, editable=True, populate_from='name', unique_with=['name'], verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='company',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='education',
            name='class_id',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Class id'),
        ),
        migrations.AlterField(
            model_name='education',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='core.Student', verbose_name='Student'),
        ),
        migrations.AlterField(
            model_name='education',
            name='student_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Student code'),
        ),
        migrations.AlterField(
            model_name='experience',
            name='company_lookup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Company', verbose_name='Company lookup'),
        ),
        migrations.AlterField(
            model_name='experience',
            name='employment_type',
            field=models.CharField(blank=True, choices=[('full_time', 'Full-time'), ('part_time', 'Part-time'), ('contract', 'Contract'), ('temporary', 'Temporary'), ('volunteer', 'Volunteer'), ('internship', 'Internship')], default=None, max_length=10, null=True, verbose_name='Employment type'),
        ),
        migrations.AlterField(
            model_name='experience',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='core.Student', verbose_name='Student'),
        ),
        migrations.AlterField(
            model_name='file',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='group',
            name='banner',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.File', verbose_name='Banner'),
        ),
        migrations.AlterField(
            model_name='group',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='group',
            name='create_by',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='admin_groups', to=settings.AUTH_USER_MODEL, verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='group',
            name='members_count',
            field=models.IntegerField(default=0, verbose_name='Members count'),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(default=None, max_length=200, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='group',
            name='posts_count',
            field=models.IntegerField(default=0, verbose_name='Posts count'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=True, populate_from='name', unique_with=['name'], verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='groupuser',
            name='group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='group_members', to='core.Group', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='groupuser',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='group_members', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='link',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='link',
            name='create_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='link',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='link',
            name='link',
            field=models.URLField(max_length=255, verbose_name='Link url'),
        ),
        migrations.AlterField(
            model_name='link',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Link name'),
        ),
        migrations.AlterField(
            model_name='link',
            name='picture',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='Link picture'),
        ),
        migrations.AlterField(
            model_name='link',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='post',
            name='comments_count',
            field=models.IntegerField(default=0, verbose_name='Comments count'),
        ),
        migrations.AlterField(
            model_name='post',
            name='create_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='core.Group', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='post',
            name='public_code',
            field=models.CharField(choices=[('accept', 'Accept'), ('waiting', 'Awaiting approval'), ('dissent', 'Dissent')], default='waiting', max_length=30, verbose_name='Public code'),
        ),
        migrations.AlterField(
            model_name='post',
            name='views_count',
            field=models.IntegerField(default=0, verbose_name='Views count'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='create_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skills_created', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='student',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Birth date'),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.File', verbose_name='Avatar'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_company',
            field=models.BooleanField(default=False, verbose_name='Is company'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_online',
            field=models.BooleanField(default=False, verbose_name='Is online'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_student',
            field=models.BooleanField(default=False, verbose_name='Is student'),
        ),
        migrations.AlterField(
            model_name='user',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=True, populate_from='username', unique_with=['username'], verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('vi', 'Tiếng Việt'), ('jp', '日本語')], default='vi', max_length=2, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='expired_time',
            field=models.DateTimeField(verbose_name='Expired time'),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='is_enable',
            field=models.BooleanField(default=True, verbose_name='Is enable'),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='view',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create at'),
        ),
        migrations.AlterField(
            model_name='view',
            name='create_by',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='views', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='view',
            name='post',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='views', to='core.Post', verbose_name='Post'),
        ),
    ]