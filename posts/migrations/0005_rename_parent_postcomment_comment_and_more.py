# Generated by Django 5.1.1 on 2024-11-09 18:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_rename_liked_by_author_postcomment_is_liked_by_author'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postcomment',
            old_name='parent',
            new_name='comment',
        ),
        migrations.RenameField(
            model_name='postcomment',
            old_name='reply_to',
            new_name='mentioned_user',
        ),
    ]