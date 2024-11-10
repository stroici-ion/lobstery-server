from django.db.models import Case, When, Value, IntegerField
from rest_framework.mixins import UpdateModelMixin
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Post, PostComment, PostLike, CommentLike, Audience
from .serializers import PostListSerilaizer, PostCreateSerilaizer, PostLikesInfoSerilaizer
from .serializers import CommentCreateSerilaizer, CommentListSerilaizer, PostLikeSerilaizer
from .serializers import ReplyListSerilaizer, CommentLikeByAuthorSerializer
from .serializers import CommentLikesInfoSerilaizer, CommentLikeSerilaizer, PostPinnedCommentSerilaizer
from .serializers import AudienceCreateUpdateSerilaizer, AudienceListSerilaizer, AudienceRetrieveDestroySerilaizer


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


class PostListAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = PostListSerilaizer
    queryset = Post.objects.all()

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.GET.get('user', '')
        return context

class PostRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PostListSerilaizer
    queryset = Post.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user.id
        return context


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCreateSerilaizer
    queryset = Post.objects.all()


class PostUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = PostCreateSerilaizer
    queryset = Post.objects.all()


class PostDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [OwnerPermission]
    queryset = Post.objects.all()
    serializer_class = PostCreateSerilaizer


class PostPinCommentAPIView(APIView):
    permission_classes = [PostAuthorPermission]

    def post(self, request, pk, format=None):
        comment_id = request.data.get('comment')
        print(comment_id)
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
        # sort_by = self.kwargs.get('sort_by')

        # MOST_RELEVANT = 'most_relevant',
        # NEWEST = 'newest',
        # ALL_COMMENTS = 'all_comments',

        pinned_comment_id = None
        if post.pinned_comment:
            pinned_comment_id = post.pinned_comment.id

        return super().get_queryset().filter(post=post.id, comment=None).annotate(
            custom_order=Case(
                When(id=pinned_comment_id, then=Value(1)),
                output_field=IntegerField(),
            )).order_by('-custom_order')
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.GET.get('user', -1)
        return context


class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentCreateSerilaizer
    queryset = PostComment.objects.all()


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
        print(self.request.GET.get('user', ''))
        context['user'] = self.request.GET.get('user', '')
        return context


'''Audience'''


class AudienceCreateAPIView(generics.CreateAPIView):
    serializer_class = AudienceCreateUpdateSerilaizer
    queryset = Audience.objects.all()


class AudienceUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = AudienceCreateUpdateSerilaizer
    queryset = Audience.objects.all()


class AudienceListAPIView(generics.ListAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = AudienceListSerilaizer
    queryset = Audience.objects.all()
    lookup_field = "user"


class AudienceRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    permission_classes = [OwnerPermission]
    serializer_class = AudienceRetrieveDestroySerilaizer
    queryset = Audience.objects.all()
