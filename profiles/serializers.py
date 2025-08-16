from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from profiles.models import UserProfile
from rest_framework.validators import UniqueValidator


class UserProfileInlineSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    avatar_thumbnail = serializers.ImageField(read_only=True)
    cover = serializers.ImageField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "avatar_thumbnail",
            "cover",
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    profile = UserProfileInlineSerializer(source="userprofile")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "profile",
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        validators=[validate_password],
        write_only=True,
        required=True,
    )

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="This email is already taken."
            )
        ],
    )

    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name", "email")

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super(UserRegisterSerializer, self).create(validated_data)


# PROFILE
# FOR CREATE AND UPDATE
class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(
        required=False, max_length=None, allow_empty_file=True
    )
    avatar_thumbnail = serializers.ImageField(read_only=True)
    cover = serializers.ImageField(
        required=False, max_length=None, allow_empty_file=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "avatar_thumbnail",
            "cover",
        ]


# FOR FRIENDS
class UserProfileFriendsInlineSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
        ]


# FRIENDS
class UserProfileFriendsSerializer(serializers.ModelSerializer):
    friends = UserProfileFriendsInlineSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "friends",
        ]


# FOR DEFAULT AUDIENCE FETCHING
class UserProfileAudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "default_audience",
            "default_custom_audience",
        ]


# FOR MY PROFILE
class MyProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    friends = UserProfileFriendsInlineSerializer(many=True, read_only=True)
    friends_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "default_audience",
            "default_custom_audience",
            "friends",
            "friends_count",
        ]

    def get_friends_count(self, obj):
        return obj.friends.count()


class UserProfileDetailsSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer()
    friends = UserProfileFriendsInlineSerializer(many=True, read_only=True)
    friends_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "friends",
            "friends_count",
        ]

    def get_friends_count(self, obj):
        return obj.friends.count()
