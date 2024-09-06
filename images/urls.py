from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.ImageCreateView.as_view()),
    path('', views.ImageListView.as_view()),
    path('<int:pk>/update/', views.ImageUpdateView.as_view()),
    path('<int:pk>/delete/', views.ImageDestroyView.as_view()),
    # path('tagged-friends/', views.TaggedFriendsCreateAPIView.as_view()),
    path('tagged-friends/<int:pk>/', views.TaggedFriendsListAPIView.as_view()),
]
