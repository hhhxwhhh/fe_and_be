from django.urls import path
from .views import PostListView,PostDetailView,CommentView,LikeView,UserPostsView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/comments/', CommentView.as_view(), name='post-comments'),
    path('<int:pk>/like/', LikeView.as_view(), name='post-like'),
    path('user/<int:pk>/', UserPostsView.as_view(), name='user-posts'),
]
