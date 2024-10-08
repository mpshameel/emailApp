# Generated by Django 4.0.6 on 2024-06-22 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='mailBox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=100, null=True)),
                ('fromMail', models.CharField(blank=True, max_length=100, null=True)),
                ('date', models.CharField(blank=True, max_length=100, null=True)),
                ('attachements', models.ImageField(blank=True, null=True, upload_to='deals/deals_pic')),
                ('status', models.CharField(default='open', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='deals',
        ),
    ]
