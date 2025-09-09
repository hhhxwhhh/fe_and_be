from django.urls import path
from .views import RegisterView,LoginView,UserProfileView,FollowView,UnFollowView,UpdateProfileView,hello_world

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('<int:pk>/',UserProfileView.as_view(),name='user-profile'),
    path('<int:pk>/follow/',FollowView.as_view(),name='follow-user'),
    path('<int:pk>/unfollow/',UnFollowView.as_view(),name='unfollow-user'),
    path('profile/update/',UpdateProfileView.as_view(),name='update-profile'),
    path('hello/',hello_world,name='hello-world'),
]
