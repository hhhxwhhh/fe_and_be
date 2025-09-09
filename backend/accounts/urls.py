from django.urls import path
from .views import RegisterView,LoginView,UserProfileView,CurrentUserProfileView,FollowView,UnFollowView,UpdateProfileView,hello_world

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('profile/', CurrentUserProfileView.as_view(), name='current-user-profile'),  # 添加当前用户资料路由
    path('<int:pk>/',UserProfileView.as_view(),name='user-profile'),
    path('<int:pk>/posts/',UserProfileView.as_view(),name='user-posts'),
    path('<int:pk>/follow/',FollowView.as_view(),name='follow-user'),
    path('<int:pk>/unfollow/',UnFollowView.as_view(),name='unfollow-user'),
    path('profile/update/',UpdateProfileView.as_view(),name='update-profile'),
    path('hello/', hello_world, name='hello-world'),
]