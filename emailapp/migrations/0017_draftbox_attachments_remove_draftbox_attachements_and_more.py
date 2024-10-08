# Generated by Django 4.2.13 on 2024-07-01 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0016_alter_sentbox_in_reply_to'),
    ]

    operations = [
        migrations.CreateModel(
            name='draftBox_attachments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='draftAttachments/')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('filename', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='draftbox',
            name='attachements',
        ),
        migrations.AlterField(
            model_name='draftbox',
            name='in_reply_to',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='draftbox',
            name='attachements',
            field=models.ManyToManyField(blank=True, to='emailapp.draftbox_attachments'),
        ),
    ]
