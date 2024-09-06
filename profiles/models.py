from io import BytesIO
from PIL import Image
from django.db import models
from django.conf import settings
from posts.models import Audience

from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True,
                                on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='avatars', blank=True, null=True, max_length=255)
    cover = models.ImageField(
        upload_to='covers', blank=True, null=True, max_length=255)
    avatar_thumbnail = models.ImageField(
        upload_to='avatars_tumbnails', blank=True, null=True, max_length=255)
    friends = models.ManyToManyField("self",  blank=True)
    default_audience = models.IntegerField(default=1)
    default_custom_audience = models.ForeignKey(Audience, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, **kwargs):
        if (self.avatar):
            output_size = (100, 100)
            output_thumb = BytesIO()
            img = Image.open(self.avatar)
            img_name = self.avatar.name.split('.')[0]

            if img.height > 100 or img.width > 100:
                img.thumbnail(output_size)
                img.save(output_thumb, format='PNG', quality=90)

            self.avatar_thumbnail = InMemoryUploadedFile(
                output_thumb, 'ImageField', f"{img_name}_thumb.jpg", 'image/jpeg', sys.getsizeof(output_thumb), None)
        super(UserProfile, self).save()
