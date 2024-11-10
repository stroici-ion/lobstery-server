from django.urls import path

from . import views

urlpatterns = [
    path('', views.PostListAPIView.as_view()),
    path('<int:pk>/details/', views.PostRetrieveAPIView.as_view()),
    path('create/', views.PostCreateAPIView.as_view()),
    path('<int:pk>/update/', views.PostUpdateAPIView.as_view()),
    path('<int:pk>/delete/', views.PostDestroyAPIView.as_view()),

    path('<int:pk>/likes/', views.PostLikeAPIView.as_view()),
    path('<int:pk>/pin-comment/', views.PostPinCommentAPIView.as_view()),

    path('comments/', views.CommentCreateAPIView.as_view()),
    path('comments/<int:post>/', views.CommentListAPIView.as_view()),
    path('comments/<int:pk>/delete/', views.CommentDestroyAPIView.as_view()),
    path('comments/<int:pk>/update/', views.CommentUpdateAPIView.as_view()),

    path('comments/<int:pk>/like_by_author/',
         views.CommentLikeByAuthorAPIView.as_view()),
    path('comments/<int:pk>/likes/', views.CommentLikeAPIView.as_view()),

    path('replies/<int:comment>/', views.ReplyListAPIView.as_view()),

    path('audience/', views.AudienceCreateAPIView.as_view()),
    path('audience/<int:user>/list/', views.AudienceListAPIView.as_view()),
    path('audience/<int:pk>/update/', views.AudienceUpdateAPIView.as_view()),
    path('audience/<int:pk>/delete/',
         views.AudienceRetrieveDestroyAPIView.as_view()),
    path('audience/<int:pk>/details/',
         views.AudienceRetrieveDestroyAPIView.as_view())
]
