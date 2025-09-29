from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from posts.models import Post
from interactions.models import Like
from messaging.models import Message
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@staff_member_required
def statistics_view(request):
    # 统计数据
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_likes = Like.objects.count()
    total_messages = Message.objects.count()
    
    # 最近注册用户
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # 用户增长趋势（最近7天）
    week_ago = timezone.now() - timedelta(days=7)
    user_growth_data = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = User.objects.filter(
            date_joined__gte=day,
            date_joined__lt=next_day
        ).count()
        user_growth_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_messages': total_messages,
        'recent_users': recent_users,
        'user_growth_data': user_growth_data,
    }
    return render(request, 'admin/statistics.html', context)