from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Comment
from .serializers import PostSeralizers, CommentSeralizers
from interactions.models import Like
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
User=get_user_model()

class PostListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # 添加解析器以处理文件上传
    
    def get(self,request):
        show_all=request.query_params.get('all','false').lower()=='true'
        if show_all:
            posts=Post.objects.all()
        elif request.user.is_authenticated:
            following=request.user.following.all()
            posts=Post.objects.filter(
                models.Q(author__in=following) | models.Q(author=request.user)
            ).distinct()
        else:
            posts=Post.objects.all()

        serializer=PostSeralizers(posts,many=True,context={'request':request})
        return Response(serializer.data)
        
    def post(self,request):
        serializer=PostSeralizers(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSeralizers(post, context={'request': request})
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            if post.author != request.user:
                return Response({'error': 'You do not have permission to edit this post'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            serializer = PostSeralizers(post, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            if post.author != request.user:
                return Response({'error': 'You do not have permission to delete this post'}, 
                              status=status.HTTP_403_FORBIDDEN)
            post.delete()
            return Response({'message': 'Post deleted successfully'})
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
class CommentView(APIView):
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = CommentSeralizers(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class LikeView(APIView):
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.delete()
                return Response({'message': 'Unliked', 'liked': False})
            return Response({'message': 'Liked', 'liked': True})
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
class UserPostsView(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            posts = Post.objects.filter(author=user)
            serializer = PostSeralizers(posts, many=True, context={'request': request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)