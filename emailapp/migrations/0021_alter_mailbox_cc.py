# Generated by Django 4.2.13 on 2024-07-08 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0020_profile_createdby'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailbox',
            name='cc',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
