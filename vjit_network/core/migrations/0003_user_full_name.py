# Generated by Django 3.0 on 2020-11-13 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20201111_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='full_name',
            field=models.CharField(blank=True, max_length=131, null=True, verbose_name='Full name'),
        ),
    ]
