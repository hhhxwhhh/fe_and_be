# backend/accounts/views.py

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
# --- 核心修改 1: 修正导入 ---
from .serializers import (
    UserDetailSerializer, 
    UserRegistrationSerializer,
    UserUpdateSerializer,
    UserSerializer 
)
from posts.serializers import PostSerializer # 修正拼写
# --- 修改结束 ---
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from posts.models import Post
from interactions.models import Notification
from interactions.services import NotificationService
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # --- 核心修改 2: 修正序列化器引用 ---
    serializer_class = UserDetailSerializer # 使用详细版
    # --- 修改结束 ---
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "bio"] # 假设 User 模型有 bio 字段
    ordering_fields = ["date_joined", "last_login"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class UserListView(generics.ListAPIView):
    # --- 核心修改 3: 使用基础版 UserSerializer ---
    serializer_class = UserSerializer # 列表不需要帖子的详细信息，用基础版更高效
    # --- 修改结束 ---
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
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
                    # --- 核心修改 4: 使用详细版 ---
                    "user": UserDetailSerializer(user, context={"request": request}).data,
                    # --- 修改结束 ---
                },
                status=status.HTTP_201_CREATED,
            )
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
                    # --- 核心修改 5: 使用详细版 ---
                    "user": UserDetailSerializer(user, context={"request": request}).data,
                    # --- 修改结束 ---
                }
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            # --- 核心修改 6: 使用详细版 ---
            serializer = UserDetailSerializer(user, context={"request": request})
            # --- 修改结束 ---
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class FollowView(APIView):
    permission_classes = [IsAuthenticated] # 添加权限
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
    permission_classes = [IsAuthenticated] # 添加权限
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
            # --- 核心修改 7: 使用详细版 ---
            return Response(
                UserDetailSerializer(request.user, context={"request": request}).data
            )
            # --- 修改结束 ---
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        # --- 核心修改 8: 使用详细版 ---
        serializer = UserDetailSerializer(request.user, context={"request": request})
        # --- 修改结束 ---
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # --- 核心修改 9: 使用详细版 ---
            return Response(
                UserDetailSerializer(request.user, context={"request": request}).data
            )
            # --- 修改结束 ---
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(generics.ListAPIView):
    # --- 核心修改 10: 使用基础版 ---
    serializer_class = UserSerializer
    # --- 修改结束 ---
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'bio']

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def hello_world(request):
    return Response({"message": "hello from django backend", "status": "success"})