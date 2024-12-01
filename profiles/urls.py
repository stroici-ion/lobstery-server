from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    path('register/', views.UserCreateView.as_view()),
    path('profiles/<int:user_id>/', views.MyUserProfileRetrieveView.as_view()),
    path('profiles/user/<int:user_id>/', views.UserProfileRetrieveView.as_view()),
    path('profiles/friends/<int:user>/', views.FriendsListView.as_view()),
    path('profiles/<int:user>/audience/', views.AudienceUpdateRetrieveAPIView.as_view()),
]
