from rest_framework import generics, response, status, permissions
import json

from .models import Image, TaggedFriend
from .serilaizers import ImageCreateSerializer, ImageListSerializer, ImageUpdateSerializer, TaggedFriendsListSerializer

class OwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ImageCreateView(generics.CreateAPIView):
    serializer_class = ImageCreateSerializer
    queryset = Image.objects.all()
    
class ImageUpdateView(generics.UpdateAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = ImageUpdateSerializer
    queryset = Image.objects.all()

class ImageDestroyView(generics.DestroyAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = ImageCreateSerializer
    queryset = Image.objects.all()

class ImageListView(generics.ListAPIView):
    serializer_class = ImageListSerializer
    queryset = Image.objects.all()

class TaggedFriendsListAPIView(generics.ListCreateAPIView):
    serializer_class = TaggedFriendsListSerializer
    queryset = TaggedFriend.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(image=self.kwargs.get('pk'))
