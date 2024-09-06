# Generated by Django 5.0 on 2024-01-01 23:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, max_length=255, null=True, upload_to='avatars')),
                ('cover', models.ImageField(blank=True, max_length=255, null=True, upload_to='covers')),
                ('avatar_thumbnail', models.ImageField(blank=True, max_length=255, null=True, upload_to='avatars_tumbnails')),
                ('default_audience', models.IntegerField(default=1)),
                ('default_custom_audience', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.audience')),
                ('friends', models.ManyToManyField(blank=True, to='profiles.userprofile')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
