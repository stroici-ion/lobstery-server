from rest_framework import serializers
from django.contrib.auth.models import User
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

from images.serilaizers import ImageListSerializer
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
        source='replies.count',
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
            'is_liked_by_author',
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
        user = self.context.get('user')
        if user:
            liked = CommentLike.objects.filter(
                like=True, comment=comment, user=user).exists()
            return liked
        return False

    def get_disliked(self, comment):
        user = self.context.get('user')
        if user:
            disliked = CommentLike.objects.filter(
                like=False, comment=comment, user=user).exists()
            return disliked
        return False

    def get_is_replied_by_author(self, comment):
        is_replied_by_author = PostComment.objects.filter(
            comment=comment, user=comment.post.user).exists()
        return is_replied_by_author
    
    def get_is_pinned_by_author(self, comment):
        return comment.post.pinned_comment == comment


class CommentCreateSerilaizer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), many=False)

    comment = serializers.PrimaryKeyRelatedField(
        queryset=PostComment.objects.all(), many=False, required=False)
    mentioned_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False, required=False)

    class Meta:
        model = PostComment
        fields = [
            'id',
            'text',
            'user',
            'post',
            'comment',
            'mentioned_user',
            'created_at',
            'updated_at'
        ]
        
    def create(self, validated_data):
        user_id = self.context['request'].user.id
        if user_id:
            validated_data['user_id'] = user_id
            return super().create(validated_data)


class PostPinnedCommentSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'pinned_comment'
        ]


class PostListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    image_set = ImageListSerializer(many=True, read_only=True)
    user = UserPublicSerializer(many=False, read_only=True)
    tagged_friends = UserPublicSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    comments_count = serializers.IntegerField(read_only=True)  # Annotated
    likes_count = serializers.IntegerField(read_only=True)  # Annotated
    dislikes_count = serializers.IntegerField(read_only=True)  # Annotated
    favorite = serializers.BooleanField() # Annotated
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()
    audience = serializers.SerializerMethodField()
    custom_audience = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'images_count',
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
            'custom_audience',
            'images_layout',
            'favorite'
        ]

    def get_liked(self, post):
        user_id = self.context.get('user')
        if user_id:
            return PostLike.objects.filter(like=True, post=post, user_id=user_id).exists()
        return False

    def get_disliked(self, post):
        user_id = self.context.get('user')
        if user_id:
            return PostLike.objects.filter(like=False, post=post, user_id=user_id).exists()
        return False

    def get_audience(self, post):
        user_id = self.context.get('user')
        if user_id and int(user_id) == post.user.id:
            return post.audience
        return None

    def get_custom_audience(self, post):
        user_id = self.context.get('user')
        if user_id and int(user_id) == post.user.id and post.audience == 4:
            return post.custom_audience.id if post.custom_audience else None
        return None
    

class PostCreateSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    custom_audience = serializers.PrimaryKeyRelatedField(
        queryset=Audience.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'audience',
            'custom_audience',
            'text',
            'feeling',
            'tags',
            'tagged_friends',
            'images_layout'
        ]

    def validate(self, attrs):
        audience = attrs.get('audience')
        custom_audience = attrs.get('custom_audience')

        # Enforce custom_audience only for audience = 4
        if audience == 4:
            if not custom_audience:
                raise serializers.ValidationError({
                    'custom_audience': 'This field is required when audience is set to 4.'
                })
        else:
            # Remove custom_audience if audience is not 4
            attrs.pop('custom_audience', None)

        return attrs

    def create(self, validated_data):
        # Remove custom_audience if audience is not 4
        if validated_data.get('audience') != 4:
            validated_data.pop('custom_audience', None)
        user_id = self.context['request'].user.id
        validated_data['user_id'] = user_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Remove custom_audience if audience is not 4
        if validated_data.get('audience') != 4:
            validated_data.pop('custom_audience', None)
        return super().update(instance, validated_data)
    
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
            'is_liked_by_author',
        ]

# REPLIES


class ReplyListSerilaizer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    mentioned_user = UserPublicSerializer()
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
            'comment',
            'mentioned_user',
            'is_liked_by_author',
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
        user = self.context.get('user')
        if user:
            liked = CommentLike.objects.filter(
                like=True, comment=comment, user=user).exists()
            return liked
        return False
        
    def get_disliked(self, comment):
        user = self.context.get('user')
        if user:
            disliked = CommentLike.objects.filter(
                like=False, comment=comment, user=user).exists()
            return disliked
        return False



class AudienceCreateSerializer(serializers.ModelSerializer):
    users = UserPublicSerializer(many=True, read_only=True)
    user_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
        )
    
    class Meta:
        model = Audience
        fields = [
            'id',
            'title',
            'audience', 
            'users',
            'user_ids'
        ]

    def create(self, validated_data):
        user_id = self.context['request'].user.id    
        if user_id:
            users = validated_data.pop('user_ids', [])
            audience = super().create(validated_data)
            audience.users.set(users)
            return audience
        
    def update(self, instance, validated_data):
        user_id = self.context['request'].user.id    
        if user_id:
            users = validated_data.pop('user_ids', None)
            instance = super().update(instance, validated_data)
            if users is not None:
                instance.users.set(users)
            return instance


class AudienceListSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = Audience
        fields = [
            'id',
            'title',
            'audience',
        ]


# class AudienceRetrieveDestroySerilaizer(serializers.ModelSerializer):
#     users = UserPublicSerializer(many=True, read_only=True)

#     class Meta:
#         model = Audience
#         fields = [
#             'id',
#             'title',
#             'user',
#             'audience',
#             'users',
#         ]


class FavoritePostSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        if not Post.objects.filter(id=value).exists():
            raise serializers.ValidationError("Post with this ID does not exist.")
        return value