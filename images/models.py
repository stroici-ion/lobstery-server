from io import BytesIO
from PIL import Image as ImageTool
from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from posts.models import Post

User = settings.AUTH_USER_MODEL


class Image(models.Model):
    caption = models.CharField(
        default='', max_length=500, null=True, blank=True)
    image = models.ImageField(
        upload_to='images', blank=True, null=True, max_length=255, width_field='image_width', height_field='image_height')
    image_thumbnail = models.ImageField(upload_to='images_tumbnails', width_field='thumbnail_width', height_field='thumbnail_height', blank=True, null=True,
                                        verbose_name='image_thumbnail')
    user = models.ForeignKey(User, null=True,
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True,
                             on_delete=models.CASCADE)
    image_width = models.IntegerField(default=0)
    image_height = models.IntegerField(default=0)
    thumbnail_width = models.IntegerField(default=0)
    thumbnail_height = models.IntegerField(default=0)
    video = models.FileField(upload_to='video', blank=True, null=True)
    order_id = models.IntegerField(default=-1)

    @property
    def aspect_ratio(self):
        return self.image_width/self.image_height

    @property
    def is_video_file(self):
        return bool(self.video)

    def save(self, **kwargs):
        if self.image:
            output_size_long_horizontal = (9999, 400)
            output_size_horizontal = (750, 9999)
            output_size_square = (9999, 400)
            output_size_vertical = (400, 9999)
            output_thumb = BytesIO()
            img = ImageTool.open(self.image)
            img_name = self.image.name.split('.')[0]
            aspect_ratio = img.width / img.height
            if aspect_ratio > 1.8:
                img.thumbnail(output_size_long_horizontal,
                              resample=ImageTool.LANCZOS)
            if aspect_ratio > 1.2 and aspect_ratio <= 1.8:
                img.thumbnail(output_size_horizontal,
                              resample=ImageTool.LANCZOS)
            if aspect_ratio <= 1.2 and aspect_ratio >= 0.8:
                img.thumbnail(output_size_square, resample=ImageTool.LANCZOS)
            if aspect_ratio < 0.8:
                img.thumbnail(output_size_vertical, resample=ImageTool.LANCZOS)
            img.save(output_thumb, format='WEBP')

            self.image_thumbnail = InMemoryUploadedFile(
                output_thumb, 'ImageField', f"{img_name}_thumb.webp", 'image/webp', sys.getsizeof(output_thumb), None)

        super(Image, self).save()


class TaggedFriend(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    image = models.ForeignKey(
        Image, default=1, on_delete=models.CASCADE, related_name='tagged_friends')
    top = models.IntegerField(default=0)
    left = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'image',)
