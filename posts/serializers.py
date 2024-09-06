from rest_framework import serializers
from django.contrib.auth.models import User
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

from images.serilaizers import ImageListSerilaizer
from profiles.serializers import UserPublicSerializer

from .models import Audience, Post, PostComment, PostLike, CommentLike


# COMMENTS


class CommentListSerilaizer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()
    is_replied_by_author = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(
        source='postcomment_set.count',
        read_only=True,
    )
    is_pinned_by_author = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = [
            'id',
            'text',
            'user',
            'post',
            'liked_by_author',
            'created_at',
            'updated_at',
            'likes_count',
            'dislikes_count',
            'liked',
            'disliked',
            'replies_count',
            'is_replied_by_author',
            'is_pinned_by_author',
        ]

    def get_likes_count(self, comment):
        count = CommentLike.objects.filter(like=True, comment=comment).count()
        return count

    def get_dislikes_count(self, comment):
        count = CommentLike.objects.filter(like=False, comment=comment).count()
        return count

    def get_liked(self, comment):
        user = self.context.get('request').user
        liked = CommentLike.objects.filter(
            like=True, comment=comment, user=user).count() > 0
        return liked

    def get_disliked(self, comment):
        user = self.context.get('request').user
        disliked = CommentLike.objects.filter(
            like=False, comment=comment, user=user).count() > 0
        return disliked

    def get_is_replied_by_author(self, comment):
        is_replied_by_author = PostComment.objects.filter(
            parent=comment, user=comment.post.user).count() > 0
        return is_replied_by_author

    def get_is_pinned_by_author(self, comment):
        print(comment.post.pinned_comment, comment)
        return comment.post.pinned_comment == comment


class CommentCreateSerilaizer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False)
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), many=False)

    parent = serializers.PrimaryKeyRelatedField(
        queryset=PostComment.objects.all(), many=False, required=False)
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False, required=False)

    class Meta:
        model = PostComment
        fields = [
            'id',
            'text',
            'user',
            'post',
            'parent',
            'reply_to',
            'created_at',
            'updated_at'
        ]

# POSTS


class PostPinnedCommentSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'pinned_comment'
        ]


class PostListSerilaizer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    image_set = ImageListSerilaizer(many=True, read_only=True)
    user = UserPublicSerializer(many=False, read_only=True)
    tagged_friends = UserPublicSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    comments_count = serializers.IntegerField(
        source='postcomment_set.count',
        read_only=True,
    )
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()
    # pinned_comment = CommentListSerilaizer(many=False)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'text',
            'feeling',
            'image_set',
            'tagged_friends',
            'user',
            'created_at',
            'updated_at',
            'tags',
            'comments_count',
            'likes_count',
            'dislikes_count',
            'liked',
            'disliked',
            'audience',
            'custom_audience'

        ]

    def get_likes_count(self, post):
        count = PostLike.objects.filter(like=True, post=post).count()
        return count

    def get_dislikes_count(self, post):
        count = PostLike.objects.filter(like=False, post=post).count()
        return count

    def get_liked(self, post):
        user = self.context.get('request').user
        liked = PostLike.objects.filter(
            like=True, post=post, user=user).count() > 0
        return liked

    def get_disliked(self, post):
        user = self.context.get('request').user
        disliked = PostLike.objects.filter(
            like=False, post=post, user=user).count() > 0
        return disliked


class PostCreateSerilaizer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'audience',
            'text',
            'feeling',
            'tags',
            'tagged_friends',
        ]

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        if user_id:
            validated_data['user_id'] = user_id
            return super().create(validated_data)
# LIKES


class PostLikeSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = '__all__'


class CommentLikeSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = '__all__'


class PostLikesInfoSerilaizer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    class Meta:
        model = CommentLike
        fields = [
            'likes_count',
            'dislikes_count',
            'liked',
            'disliked',
        ]

    def get_likes_count(self, post):
        count = PostLike.objects.filter(like=True, post=post).count()
        return count

    def get_dislikes_count(self, post):
        count = PostLike.objects.filter(like=False, post=post).count()
        return count

    def get_liked(self, post):
        user = self.context.get('request').user
        liked = PostLike.objects.filter(
            like=True, post=post, user=user).count() > 0
        return liked

    def get_disliked(self, post):
        user = self.context.get('request').user
        disliked = PostLike.objects.filter(
            like=False, post=post, user=user).count() > 0
        return disliked


class CommentLikesInfoSerilaizer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    class Meta:
        model = CommentLike
        fields = [
            'likes_count',
            'dislikes_count',
            'liked',
            'disliked',
        ]

    def get_likes_count(self, comment):
        count = CommentLike.objects.filter(like=True, comment=comment).count()
        return count

    def get_dislikes_count(self, comment):
        count = CommentLike.objects.filter(like=False, comment=comment).count()
        return count

    def get_liked(self, comment):
        user = self.context.get('request').user
        liked = CommentLike.objects.filter(
            like=True, comment=comment, user=user).count() > 0
        return liked

    def get_disliked(self, comment):
        user = self.context.get('request').user
        disliked = CommentLike.objects.filter(
            like=False, comment=comment, user=user).count() > 0
        return disliked


class CommentLikeByAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = [
            'liked_by_author',
        ]

# REPLIES


class ReplyListSerilaizer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    reply_to = UserPublicSerializer()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = [
            'id',
            'text',
            'user',
            'post',
            'parent',
            'reply_to',
            'liked_by_author',
            'created_at',
            'updated_at',
            'likes_count',
            'dislikes_count',
            'liked',
            'disliked',
        ]

    def get_likes_count(self, comment):
        count = CommentLike.objects.filter(like=True, comment=comment).count()
        return count

    def get_dislikes_count(self, comment):
        count = CommentLike.objects.filter(like=False, comment=comment).count()
        return count

    def get_liked(self, comment):
        user = self.context.get('request').user
        liked = CommentLike.objects.filter(
            like=True, comment=comment, user=user).count() > 0
        return liked

    def get_disliked(self, comment):
        user = self.context.get('request').user
        disliked = CommentLike.objects.filter(
            like=False, comment=comment, user=user).count() > 0
        return disliked


class AudienceCreateUpdateSerilaizer(serializers.ModelSerializer):
    audience = serializers.IntegerField()
    users_list = UserPublicSerializer(
        source='audience_list', many=True, read_only=True)
    audience_list = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True)

    class Meta:
        model = Audience
        fields = [
            'id',
            'title',
            'audience',
            'audience_list',
            'users_list'
        ]

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        if user_id:
            validated_data['user_id'] = user_id
            return super().create(validated_data)


class AudienceListSerilaizer(serializers.ModelSerializer):
    audience_list = UserPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Audience
        fields = [
            'id',
            'title',
            'audience',
            'audience_list'
        ]


class AudienceRetrieveDestroySerilaizer(serializers.ModelSerializer):
    audience_list = UserPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Audience
        fields = [
            'id',
            'title',
            'user',
            'audience',
            'audience_list'
        ]
