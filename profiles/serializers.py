from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from profiles.models import UserProfile


class UserProfileInlineSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    avatar_thumbnail = serializers.ImageField(read_only=True)
    cover = serializers.ImageField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'avatar_thumbnail',
            'cover',
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    profile = UserProfileInlineSerializer(source='userprofile')

    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'first_name',
                  'last_name',
                  'profile',
                  ]

# FULL USER INFO  (FRIENDS COUNT, LAST IMAGES AND OTHERS)


class UserProfileFullInlineSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    avatar_thumbnail = serializers.ImageField(read_only=True)
    cover = serializers.ImageField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'avatar_thumbnail',
            'cover',
            'default_audience',
            'default_custom_audience'
        ]


class UserPublicFullSerializer(serializers.ModelSerializer):
    profile = UserProfileFullInlineSerializer(source='userprofile')

    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'first_name',
                  'last_name',
                  'profile',
                  ]


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        validators=[validate_password],
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(UserRegisterSerializer, self).create(validated_data)

# PROFILE


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, max_length=None,
                                    allow_empty_file=True)
    avatar_thumbnail = serializers.ImageField(read_only=True)
    cover = serializers.ImageField(required=False, max_length=None,
                                   allow_empty_file=True)

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'avatar_thumbnail',
            'cover',
        ]


class UserProfileFriendsInlineSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(
        many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
        ]


class UserProfileFriendsSerializer(serializers.ModelSerializer):
    friends = UserProfileFriendsInlineSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'friends',
        ]

class UserProfileAudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'default_audience',
            'default_custom_audience',
        ]
