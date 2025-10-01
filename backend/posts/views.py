from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Comment
from interactions.models import Like, Notification
from .serializers import PostSeralizers, CommentSeralizers
from interactions.models import Like
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.parsers import MultiPartParser, FormParser
from interactions.services import NotificationService

# Create your views here.
User = get_user_model()


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        search_type = request.query_params.get("type", "all")  # all, posts, users

        if not query:
            return Response({"results": {"posts": [], "users": []}})

        results = {"posts": [], "users": []}

        if search_type in ["all", "posts"]:
            # 搜索帖子
            post_queryset = Post.objects.filter(
                models.Q(content__icontains=query)
                | models.Q(author__username__icontains=query)
            ).distinct()
            post_serializer = PostSeralizers(
                post_queryset, many=True, context={"request": request}
            )
            results["posts"] = post_serializer.data

        if search_type in ["all", "users"]:
            # 搜索用户
            user_queryset = User.objects.filter(
                models.Q(username__icontains=query) | models.Q(bio__icontains=query)
            ).distinct()
            from accounts.serializers import UserSeralizers

            user_serializer = UserSeralizers(
                user_queryset, many=True, context={"request": request}
            )
            results["users"] = user_serializer.data

        return Response({"results": results, "query": query})


class PostListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # 添加解析器以处理文件上传

    def get(self, request):
        show_all = request.query_params.get("all", "false").lower() == "true"
        if show_all:
            posts = Post.objects.all()
        elif request.user.is_authenticated:
            following = request.user.following.all()
            posts = Post.objects.filter(
                models.Q(author__in=following) | models.Q(author=request.user)
            ).distinct()
        else:
            posts = Post.objects.all()

        serializer = PostSeralizers(posts, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSeralizers(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSeralizers(post, context={"request": request})
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            if post.author != request.user:
                return Response(
                    {"error": "You do not have permission to edit this post"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = PostSeralizers(
                post, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            if post.author != request.user:
                return Response(
                    {"error": "You do not have permission to delete this post"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            post.delete()
            return Response({"message": "Post deleted successfully"})
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            # 检查是否至少提供了内容或图片
            content = request.data.get("content", "").strip()
            image = request.FILES.get("image")

            if not content and not image:
                return Response(
                    {"content": "评论内容或图片不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CommentSeralizers(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                comment = serializer.save(author=request.user, post=post)
                if post.author != request.user:
                    NotificationService.create_comment_notification(comment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk, comment_pk):
        try:
            post = Post.objects.get(pk=pk)
            comment = Comment.objects.get(pk=comment_pk)
            if comment.author != request.user:
                return Response(
                    {"error": "You do not have permission to delete this comment"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            comment.delete()
            return Response({"message": "Comment deleted successfully"})
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )


class LikeView(APIView):
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.delete()
                liked = False
            else:
                liked = True
                if post.author != request.user:
                    NotificationService.create_like_notification(like)
            # 返回当前点赞状态和数量
            likes_count = post.likes.count()
            return Response(
                {
                    "message": "Liked" if liked else "Unliked",
                    "liked": liked,
                    "likes_count": likes_count,
                }
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            like = Like.objects.filter(user=request.user, post=post)
            if like.exists():
                like.delete()
                liked = False
            else:
                liked = False
            # 返回当前点赞状态和数量
            likes_count = post.likes.count()
            return Response(
                {"message": "Unliked", "liked": liked, "likes_count": likes_count}
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UserPostsView(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            posts = Post.objects.filter(author=user)
            serializer = PostSeralizers(posts, many=True, context={"request": request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
