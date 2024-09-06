from rest_framework import generics, permissions

from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserRegisterSerializer, UserPublicFullSerializer
from .serializers import UserProfileSerializer, UserProfileFriendsSerializer
from .serializers import UserProfileAudienceSerializer
from rest_framework.permissions import AllowAny

class OwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicFullSerializer
    permission_classes = [AllowAny]


class UserProfileCreateView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    lookup_field = "user"


class FriendsListView(generics.RetrieveAPIView):
    serializer_class = UserProfileFriendsSerializer
    queryset = UserProfile.objects.all()
    lookup_field = "user"

# class AudienceUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
#     # permission_classes = [OwnerPermission]
#     serializer_class = UserProfileAudienceSerializer
#     queryset = UserProfile.objects.all()
#     lookup_field = "user"

class AudienceUpdateRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [OwnerPermission]
    serializer_class = UserProfileAudienceSerializer
    queryset = UserProfile.objects.all()
    lookup_field = "user"
