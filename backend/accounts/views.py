from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .serializers import UserSeralizers, UserRegistrationSerializer, UserUpdateSerializer

# Create your views here.
User=get_user_model()

class RegisterView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            refresh=RefreshToken.for_user(user)
            return Response({
                'refresh':str(refresh),
                'access':str(refresh.access_token),
                'user':UserSeralizers(user,context={'request':request}).data
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes=[AllowAny]
    
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')

        user=authenticate(request=request,email=email,password=password)
        if user is not None:
            refresh=RefreshToken.for_user(user)
            return Response({
                'refresh':str(refresh),
                'access':str(refresh.access_token),
                'user':UserSeralizers(user,context={'request':request}).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class UserProfileView(APIView):
    def get(self,request,pk):
        try:
            user=User.objects.get(pk=pk)
            serializer=UserSeralizers(user,context={'request':request})
            return Response(serializer.data)
        except user.DoesNotExist:
            return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)
        

class FollowView(APIView):
    def post(self,request,pk):
        try:
            user_to_follow=User.objects.get(pk=pk)
            if user_to_follow==request.user:
                return Response({'error':'You cannot follow yourself'},status=status.HTTP_400_BAD_REQUEST)
            request.user.following.add(user_to_follow)
            return Response({'message': f'You are now following {user_to_follow.username}'})
        except User.DoesNotExist:
            return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)
        
class UnFollowView(APIView):
    def post(self,request,pk):
        try:
            user_to_unfollow=User.objects.get(pk=pk)
            request.user.following.remove(user_to_unfollow)
            return Response({'message': f'You are no longer following {user_to_unfollow.username}'})
        except User.DoesNotExist:
            return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)
        
class UpdateProfileView(APIView):
    def put(self,request):
        serializer=UserUpdateSerializer(request.user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSeralizers(request.user,context={'request':request}).data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def hello_world(request):
    return Response({
        'message':'hello from django backend',
        'status':'success'
    })