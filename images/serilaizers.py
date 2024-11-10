import json
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Image, TaggedFriend
from posts.models import Post
from profiles.serializers import UserPublicSerializer


class TaggedFriendsCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=False, required=True)
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(), many=False, required=True)

    class Meta:
        model = TaggedFriend
        fields = [
            'user',
            'top',
            'left',
            'image'
        ]


class TaggedFriendsListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer()

    class Meta:
        model = TaggedFriend
        fields = [
            'user',
            'top',
            'left'
        ]
        read_only_fields = [
            'user',
            'top',
            'left'
        ]


class ImageCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    video = serializers.FileField(required=False)
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), many=False)
    tagged_friends = serializers.CharField(required=False)

    class Meta:
        model = Image
        fields = [
            'caption',
            'order_id',
            'post',
            'image',
            'video',
            'tagged_friends'
        ]

    def create(self, validated_data):
        tagged_friends = json.loads(validated_data.pop('tagged_friends'))
        user_id = self.context['request'].user.id
        image = Image.objects.create(**validated_data, user_id=user_id)
        for tagged_friend in tagged_friends:
            TaggedFriend.objects.create(
                image=image, user_id=tagged_friend['user'], top=tagged_friend['top'], left=tagged_friend['left'])
        return image


class ImageUpdateSerializer(serializers.ModelSerializer):
    tagged_friends = serializers.CharField(required=False)

    class Meta:
        model = Image
        fields = [
            'caption',
            'tagged_friends',
        ]

    def update(self, instance, validated_data):
        tagged_friends = json.loads(validated_data.pop('tagged_friends'))
        delete_tagged_friends = TaggedFriend.objects.filter(image=instance)
        delete_tagged_friends.delete()
        for tagged_friend in tagged_friends:
            TaggedFriend.objects.create(
                image=instance, user_id=tagged_friend['user'], top=tagged_friend['top'], left=tagged_friend['left'])
        return super().update(instance, validated_data)


class ImageListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    tagged_friends = TaggedFriendsListSerializer(many=True)

    class Meta:
        model = Image
        fields = [
            'id',
            'order_id',
            'caption',
            'image',
            'image_thumbnail',
            'user',
            'aspect_ratio',
            'thumbnail_width',
            'thumbnail_height',
            'video',
            'is_video_file',
            'tagged_friends'
        ]
