from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager

User = settings.AUTH_USER_MODEL


class Audience(models.Model):
    title = models.CharField(default='', max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 0-private list will be black, 1-public, 2-friends, 3-friends and friends of friends
    audience = models.IntegerField(default=1)
    audience_list = models.ManyToManyField(User, related_name='audience_list')


class Post(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False)
    title = models.CharField(default='', null=True,
                             blank=True, max_length=100)
    text = models.TextField(default='', null=True, blank=True,)
    feeling = models.CharField(null=True, blank=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager()
    pinned_comment = models.ForeignKey(
        'PostComment', null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name='post_pinned')
    tagged_friends = models.ManyToManyField(
        User, related_name='post_tagged_friends', blank=True)
    # 0-private, 1-public, 2-friends, 3-friends and friends of friends, 4-custom
    audience = models.IntegerField(default=1)
    custom_audience = models.ForeignKey(
        Audience, null=True, blank=True, on_delete=models.SET_NULL)


class PostComment(models.Model):
    text = models.TextField(default='')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        User, null=True, default=None, on_delete=models.SET_NULL, related_name='reply_reply')
    liked_by_author = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False)


class PostLike(models.Model):
    like = models.BooleanField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('post', 'user',)


class CommentLike(models.Model):
    like = models.BooleanField()
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('comment', 'user',)
