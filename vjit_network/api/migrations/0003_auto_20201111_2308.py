# Generated by Django 3.0 on 2020-11-11 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20201109_2250'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'verbose_name': 'Devices', 'verbose_name_plural': 'Devices'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications'},
        ),
        migrations.AlterModelOptions(
            name='notificationsetting',
            options={'verbose_name': 'Notification setting', 'verbose_name_plural': 'Notification settings'},
        ),
        migrations.AlterModelOptions(
            name='notificationtemplate',
            options={'verbose_name': 'Notification template', 'verbose_name_plural': 'Notification templates'},
        ),
        migrations.AlterModelOptions(
            name='notificationtemplatelocalization',
            options={'verbose_name': 'Notification template localization', 'verbose_name_plural': 'Notification template localizations'},
        ),
        migrations.AlterField(
            model_name='notificationtemplatelocalization',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('vi', 'Tiếng Việt'), ('jp', '日本語')], default='vi', max_length=2, verbose_name='Language'),
        ),
    ]