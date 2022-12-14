# Generated by Django 4.1.3 on 2022-12-04 08:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_appe', '0008_alter_comment_created_on_alter_post_created_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='upload/post_pictures'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 4, 8, 5, 29, 890332, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='post',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 4, 8, 5, 29, 888338, tzinfo=datetime.timezone.utc)),
        ),
    ]
