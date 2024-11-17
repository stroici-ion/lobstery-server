from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.contrib.auth.models import User
from posts.models import Audience
from .models import UserProfile
from .serializers import UserRegisterSerializer, UserPublicFullSerializer
from .serializers import UserProfileSerializer, UserProfileFriendsSerializer
from .serializers import UserProfileAudienceSerializer

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
    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileFriendsSerializer(profile, context={'request': request})
        return Response(serializer.data)    


class AudienceUpdateRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = UserProfileAudienceSerializer
    queryset = UserProfile.objects.all()
    lookup_field = "user"
    
    def put(self, request, *args, **kwargs):
        default_audience = request.data.get('default_audience')
        print(request.data)
        if default_audience == 4:
            default_custom_audience = request.data.get('default_custom_audience')
            if not default_custom_audience:
                audience_candidate = Audience.objects.filter(user=request.user.id).first()
                print(audience_candidate)
                if audience_candidate:
                    request.data['default_custom_audience'] = audience_candidate.id
                else:
                    return Response({'message': 'No custom audience to set as default'}, status=status.HTTP_400_BAD_REQUEST)
                    
        return super().put(request, *args, **kwargs)