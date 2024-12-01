from django.db.models import Case, When, Value, IntegerField, Count, Q, F, BooleanField, Exists, OuterRef
from rest_framework.mixins import UpdateModelMixin
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from profiles.models import UserProfile
from profiles.serializers import UserProfileAudienceSerializer
from .models import Post, PostComment, PostLike, CommentLike, Audience
from .serializers import AudienceCreateSerializer, PostListSerializer, PostCreateSerializer, PostLikesInfoSerilaizer
from .serializers import CommentCreateSerilaizer, CommentListSerilaizer, PostLikeSerilaizer
from .serializers import ReplyListSerilaizer, CommentLikeByAuthorSerializer
from .serializers import CommentLikesInfoSerilaizer, CommentLikeSerilaizer, PostPinnedCommentSerilaizer
from .serializers import AudienceListSerilaizer, FavoritePostSerializer


class OwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PostAuthorPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.post.user == request.user


'''POST'''


# class ProfilePostsListAPIView(generics.ListAPIView):
#     authentication_classes = []
#     permission_classes = [permissions.AllowAny]
#     serializer_class = PostListSerializer
#     queryset = Post.objects.all()
    
#     def get_queryset(self):
#         user = self.kwargs.get('user')  # Get 'user_id' from the URL
#         return Post.objects.filter(user_id=user)  # Filter posts by 'user_id'
    
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['user'] = self.request.GET.get('user', '')
#         return context
    
class PostListAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = PostListSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        user_id = self.request.GET.get('user')
        filter_by = self.request.GET.get('filterBy')

        # Ensure user is passed
        if not user_id:
            return Post.objects.none()

        # Annotate favorite status
        queryset = super().get_queryset().annotate(
            favorite=Exists(
                UserProfile.objects.filter(
                    user_id=user_id,
                    favorite_posts=OuterRef('pk')  # Check if the post exists in favorite_posts
                )
            ),
            likes_count=Count('postlike', filter=Q(postlike__like=True), distinct=True),
            dislikes_count=Count('postlike', filter=Q(postlike__like=False), distinct=True),
            comments_count=Count('comments', filter=Q(comments__comment=None), distinct=True)
        )

        # Apply filters
        if filter_by == 'all':
            queryset = queryset.filter(Q(user_id=user_id) | Q(tagged_friends=user_id)).distinct()
        elif filter_by == 'my':
            queryset = queryset.filter(user_id=user_id)
        elif filter_by == 'favorites': 
            queryset = queryset.filter(favorite=True)
        elif filter_by == 'liked':  
            queryset = queryset.filter(postlike__user_id=user_id, postlike__like=True).distinct()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.GET.get('user', '')
        return context

class PostRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    
    def get_queryset(self):
        # Annotate the queryset
        queryset = super().get_queryset().annotate(
            comments_count=Count('comments', filter=Q(comments__comment=None)),
            likes_count=Count('postlike', filter=Q(postlike__like=True)),
            dislikes_count=Count('postlike', filter=Q(postlike__like=False)),
            favorite=Case(
                When(user__userprofile__favorite_posts__id__exact=F('id'), then=True),
                default=False,
                output_field=BooleanField()
            )
        )

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user.id
        return context


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()


class PostUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()


class PostDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [OwnerPermission]
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer


class PostPinCommentAPIView(APIView):
    permission_classes = [PostAuthorPermission]

    def post(self, request, pk, format=None):
        comment_id = request.data.get('comment')
        try:
            post_candidate = Post.objects.get(pk=pk)
        except:
            post_candidate = None

        if post_candidate:
            if post_candidate.pinned_comment_id == comment_id:
                post_candidate.pinned_comment_id = None
                post_candidate.save()
            else:
                post_candidate.pinned_comment_id = comment_id
                post_candidate.save()
            return Response(PostPinnedCommentSerilaizer(post_candidate).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


'''COMMENT'''

class CommentListAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = CommentListSerilaizer
    queryset = PostComment.objects.all()

    
    def get_queryset(self):
        post = Post.objects.get(pk=self.kwargs.get('post'))
        sort_by = self.request.GET.get('sort_by', 'top_comments') 

        pinned_comment_id = post.pinned_comment.id if hasattr(post, 'pinned_comment') and post.pinned_comment else None

        queryset = super().get_queryset().filter(post=post.id, comment=None)

        queryset = queryset.annotate(
            like_count=Count('commentlike', filter=Q(commentlike__like=True)),
            is_top_comment=Case(
                When(is_liked_by_author=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            custom_order=Case(
                When(id=pinned_comment_id, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )

        if sort_by == 'top_comments':
            queryset = queryset.order_by(
                '-custom_order', '-is_top_comment', '-like_count', '-created_at'
            )
        elif sort_by == 'newest_first':
            queryset = queryset.order_by('-custom_order', '-created_at')
        else:
            queryset = queryset.order_by('-custom_order', '-created_at')

        return queryset
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.GET.get('user', -1)
        return context


class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentCreateSerilaizer
    queryset = PostComment.objects.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user.id
        return context
    
    def post(self, request, *args, **kwargs):
        create_serializer = CommentCreateSerilaizer(data=request.data, context={'request': request})
        create_serializer.is_valid(raise_exception=True)
        comment = create_serializer.save()
        list_serializer = CommentListSerilaizer(comment, context={'request': request, 'user': request.user})
        return Response(list_serializer.data, status=status.HTTP_201_CREATED)


class CommentDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [PostAuthorPermission | OwnerPermission]
    queryset = PostComment.objects.all()
    serializer_class = CommentCreateSerilaizer


class CommentUpdateAPIView(
        generics.GenericAPIView, UpdateModelMixin):
    permission_classes = [OwnerPermission]
    queryset = PostComment.objects.all()
    serializer_class = CommentCreateSerilaizer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


'''Likes'''


class PostLikeAPIView(APIView):
    def post(self, request, pk, format=None):
        post = Post.objects.get(pk=pk)
        user = request.user
        like = request.data.get('like')
        data = {
            'user': request.user.id,
            'post': pk,
            'like': like
        }
        try:
            like_candidate = PostLike.objects.get(post=post, user=user)
        except:
            like_candidate = None

        if like_candidate:
            if like_candidate.like == like:
                like_candidate.delete()
                serializer = PostLikesInfoSerilaizer(
                    post, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                like_candidate.like = like
                like_candidate.save()
                serializer = PostLikesInfoSerilaizer(
                    post, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = PostLikeSerilaizer(data=data)
            if serializer.is_valid():
                serializer.save()
                serializer = PostLikesInfoSerilaizer(
                    post, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeAPIView(APIView):
    def post(self, request, pk, format=None):
        comment = PostComment.objects.get(pk=pk)
        user = request.user
        like = request.data.get('like')
        data = {
            'user': request.user.id,
            'comment': pk,
            'like': like
        }
        try:
            like_candidate = CommentLike.objects.get(
                comment=comment, user=user)
        except:
            like_candidate = None

        if like_candidate:
            if like_candidate.like == like:
                like_candidate.delete()
                serializer = CommentLikesInfoSerilaizer(
                    comment, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                like_candidate.like = like
                like_candidate.save()
                serializer = CommentLikesInfoSerilaizer(
                    comment, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = CommentLikeSerilaizer(data=data)
            if serializer.is_valid():
                serializer.save()
                serializer = CommentLikesInfoSerilaizer(
                    comment, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeByAuthorAPIView(APIView):
    permission_classes = [PostAuthorPermission]

    def post(self, request, pk, format=None):
        try:
            comment_candidate = PostComment.objects.get(pk=pk)
        except:
            comment_candidate = None

        if comment_candidate:
            comment_candidate.is_liked_by_author = not comment_candidate.is_liked_by_author
            comment_candidate.save()
            return Response(CommentLikeByAuthorSerializer(comment_candidate).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


'''Replies'''


class ReplyListAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = ReplyListSerilaizer
    queryset = PostComment.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(comment=self.kwargs.get('comment'))
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.GET.get('user', '')
        return context


'''Audience'''


class AudienceCreateAPIView(generics.CreateAPIView):
    serializer_class = AudienceCreateSerializer
    queryset = Audience.objects.all()


class AudienceUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = AudienceCreateSerializer
    queryset = Audience.objects.all()


class AudienceListAPIView(generics.ListAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = AudienceListSerilaizer
  
    def get_queryset(self):
        user_id = self.kwargs.get('user')
        return Audience.objects.filter(user_id=user_id)
        

class AudienceRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    permission_classes = [OwnerPermission]
    queryset = Audience.objects.all()
    serializer_class = AudienceCreateSerializer
    
    def delete(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(user=self.request.user.id)
        audience = Audience.objects.get(id=pk)
        audience.delete()
        
        if profile.default_audience == 4:
            custom_audience_candidate = Audience.objects.filter(user=self.request.user.id).first()
            
            if custom_audience_candidate:
                profile.default_custom_audience = custom_audience_candidate
                profile.save()
                serialized_data = UserProfileAudienceSerializer(profile)
                return Response(serialized_data.data, status=status.HTTP_200_OK)
            else:
                profile.default_audience = 1
                profile.default_custom_audience = None
                profile.save()
                serialized_data = UserProfileAudienceSerializer(profile)
                return Response(serialized_data.data, status=status.HTTP_200_OK)
            
        return Response(status=status.HTTP_200_OK)
    
    
# FAVORITE POST

class FavoritePostView(APIView):

    def post(self, request):
        serializer = FavoritePostSerializer(data=request.data)
        if serializer.is_valid():
            post_id = serializer.validated_data['post_id']
            user_profile = request.user.userprofile  # Access UserProfile via the related name
            post = Post.objects.get(id=post_id)

            if post in user_profile.favorite_posts.all():
                user_profile.favorite_posts.remove(post)  # Remove from favorites
                return Response({"id": post_id, "favorite": False}, status=status.HTTP_200_OK)
            else:
                user_profile.favorite_posts.add(post)  # Add to favorites
                return Response({"id": post_id, "favorite": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)