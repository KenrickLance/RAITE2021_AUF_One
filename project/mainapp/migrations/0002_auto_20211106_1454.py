# Generated by Django 3.2.9 on 2021-11-06 06:54

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peoplemodel',
            name='role',
        ),
        migrations.AlterField(
            model_name='genericmodelmain',
            name='termination_date',
            field=models.DateField(default=datetime.datetime(2024, 11, 5, 6, 54, 34, 664743, tzinfo=utc), verbose_name='Termination date'),
        ),
        migrations.CreateModel(
            name='RoleModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, default='', max_length=40, null=True)),
                ('user_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_info_role', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
