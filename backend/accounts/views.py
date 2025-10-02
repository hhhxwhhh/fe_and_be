import os
from django.shortcuts import render
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from django.http import JsonResponse
from .models import User
from .serializers import (
    UserSeralizers,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from posts.models import Post
from posts.serializers import PostSeralizers
from interactions.models import Notification
from interactions.services import NotificationService
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSeralizers
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "profile__bio", "profile__name"]
    ordering_fields = ["date_joined", "last_login"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        queryset = super().get_queryset()
        # 可以添加额外的过滤逻辑
        return queryset


# 添加用户列表视图
class UserListView(generics.ListAPIView):
    serializer_class = UserSeralizers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 排除当前用户自己
        return User.objects.exclude(id=self.request.user.id)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSeralizers(user, context={"request": request}).data,
                },
                status=status.HTTP_201_CREATED,
            )
        # 返回详细的错误信息
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request=request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSeralizers(user, context={"request": request}).data,
                }
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSeralizers(user, context={"request": request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class FollowView(APIView):
    def post(self, request, pk):
        try:
            user_to_follow = User.objects.get(pk=pk)
            if user_to_follow == request.user:
                return Response(
                    {"error": "You cannot follow yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.following.add(user_to_follow)
            NotificationService.create_follow_notification(request.user, user_to_follow)
            return Response(
                {"message": f"You are now following {user_to_follow.username}"}
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UnFollowView(APIView):
    def post(self, request, pk):
        try:
            user_to_unfollow = User.objects.get(pk=pk)
            request.user.following.remove(user_to_unfollow)
            return Response(
                {"message": f"You are no longer following {user_to_unfollow.username}"}
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                UserSeralizers(request.user, context={"request": request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserSeralizers(request.user, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                UserSeralizers(request.user, context={"request": request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSeralizers
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'bio']

    def get_queryset(self):
        # 排除当前用户自己
        return User.objects.exclude(id=self.request.user.id)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def hello_world(request):
    return Response({"message": "hello from django backend", "status": "success"})
