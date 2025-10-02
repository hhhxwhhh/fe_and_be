import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from posts.models import Post, Comment
from interactions.models import Like, Notification
from messaging.models import Message, GroupChat, GroupMessage
from faker import Faker
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = '生成测试数据'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20, help='要创建的用户数量')
        parser.add_argument('--posts-per-user', type=int, default=5, help='每个用户创建的帖子数量')
        parser.add_argument('--comments-per-post', type=int, default=3, help='每个帖子的评论数量')
        parser.add_argument('--likes-per-post', type=int, default=5, help='每个帖子的点赞数量')
        parser.add_argument('--messages-per-user', type=int, default=3, help='每个用户发送的消息数量')
        parser.add_argument('--groups', type=int, default=5, help='要创建的群组数量')
        parser.add_argument('--messages-per-group', type=int, default=10, help='每个群组的消息数量')

    def handle(self, *args, **options):
        fake = Faker(['zh_CN'])
        user_count = options['users']
        posts_per_user = options['posts_per_user']
        comments_per_post = options['comments_per_post']
        likes_per_post = options['likes_per_post']
        messages_per_user = options['messages_per_user']
        group_count = options['groups']
        messages_per_group = options['messages_per_group']

        self.stdout.write('开始生成测试数据...')

        # 1. 创建用户
        users = self.create_users(fake, user_count)
        
        # 2. 创建关注关系
        self.create_following_relationships(users)
        
        # 3. 创建帖子
        posts = self.create_posts(fake, users, posts_per_user)
        
        # 4. 创建评论
        comments = self.create_comments(fake, users, posts, comments_per_post)
        
        # 5. 创建点赞
        likes = self.create_likes(users, posts, likes_per_post)
        
        # 6. 创建私信
        messages = self.create_messages(fake, users, messages_per_user)
        
        # 7. 创建群组
        groups = self.create_groups(fake, users, group_count)
        
        # 8. 创建群组消息
        group_messages = self.create_group_messages(fake, users, groups, messages_per_group)
        
        # 9. 创建通知
        notifications = self.create_notifications(users, posts, comments, likes)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功生成测试数据:\n'
                f'- 用户: {len(users)}\n'
                f'- 帖子: {len(posts)}\n'
                f'- 评论: {len(comments)}\n'
                f'- 点赞: {len(likes)}\n'
                f'- 私信: {len(messages)}\n'
                f'- 群组: {len(groups)}\n'
                f'- 群组消息: {len(group_messages)}\n'
                f'- 通知: {len(notifications)}'
            )
        )

    def create_users(self, fake, count):
        users = []
        self.stdout.write(f'正在创建 {count} 个用户...')
        
        for i in range(count):
            username = fake.user_name()
            # 确保用户名唯一
            while User.objects.filter(username=username).exists():
                username = fake.user_name() + str(random.randint(1, 999))
                
            email = fake.email()
            # 确保邮箱唯一
            while User.objects.filter(email=email).exists():
                email = fake.email()
                
            user = User.objects.create_user(
                username=username,
                email=email,
                password='test123456',
                bio=fake.text(max_nb_chars=200),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80)
            )
            users.append(user)
            
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(users)} 个用户'))
        return users

    def create_following_relationships(self, users):
        self.stdout.write('正在创建关注关系...')
        follow_count = 0
        
        for user in users:
            # 每个用户关注随机5-15个其他用户
            follow_count_for_user = random.randint(5, min(15, len(users)-1))
            potential_follows = [u for u in users if u != user]
            follows = random.sample(potential_follows, follow_count_for_user)
            
            for follow in follows:
                user.following.add(follow)
                follow_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'成功创建 {follow_count} 个关注关系'))

    def create_posts(self, fake, users, posts_per_user):
        posts = []
        self.stdout.write(f'正在创建帖子...')
        
        for user in users:
            for _ in range(posts_per_user):
                post = Post.objects.create(
                    author=user,
                    content=fake.text(max_nb_chars=300)
                )
                posts.append(post)
                
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(posts)} 个帖子'))
        return posts

    def create_comments(self, fake, users, posts, comments_per_post):
        comments = []
        self.stdout.write(f'正在创建评论...')
        
        for post in posts:
            commenters = random.sample(users, min(comments_per_post, len(users)))
            
            for user in commenters:
                comment = Comment.objects.create(
                    post=post,
                    author=user,
                    content=fake.sentence(nb_words=10)
                )
                comments.append(comment)
                
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(comments)} 个评论'))
        return comments

    def create_likes(self, users, posts, likes_per_post):
        likes = []
        self.stdout.write(f'正在创建点赞...')
        
        for post in posts:
            likers = random.sample(users, min(likes_per_post, len(users)))
            
            for user in likers:
                # 避免重复点赞
                if not Like.objects.filter(user=user, post=post).exists():
                    like = Like.objects.create(
                        user=user,
                        post=post
                    )
                    likes.append(like)
                    
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(likes)} 个点赞'))
        return likes

    def create_messages(self, fake, users, messages_per_user):
        messages = []
        self.stdout.write(f'正在创建私信...')
        
        for sender in users:
            recipients = random.sample(users, min(messages_per_user, len(users)))
            
            for recipient in recipients:
                if sender != recipient:  # 不给自己发消息
                    # 每对用户之间发送1-3条消息
                    message_count = random.randint(1, 3)
                    for _ in range(message_count):
                        message = Message.objects.create(
                            sender=sender,
                            recipient=recipient,
                            content=fake.sentence(nb_words=15)
                        )
                        messages.append(message)
                        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(messages)} 条私信'))
        return messages

    def create_groups(self, fake, users, group_count):
        groups = []
        self.stdout.write(f'正在创建群组...')
        
        for i in range(group_count):
            creator = random.choice(users)
            group = GroupChat.objects.create(
                name=fake.company() + '群聊',
                description=fake.text(max_nb_chars=100),
                created_by=creator
            )
            
            # 添加3-10个成员到群组
            member_count = random.randint(3, min(10, len(users)))
            members = random.sample(users, member_count)
            group.members.set(members)
            groups.append(group)
            
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(groups)} 个群组'))
        return groups

    def create_group_messages(self, fake, users, groups, messages_per_group):
        group_messages = []
        self.stdout.write(f'正在创建群组消息...')
        
        for group in groups:
            members = list(group.members.all())
            if not members:
                continue
                
            for _ in range(messages_per_group):
                sender = random.choice(members)
                group_message = GroupMessage.objects.create(
                    group=group,
                    sender=sender,
                    content=fake.sentence(nb_words=12)
                )
                group_messages.append(group_message)
                
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(group_messages)} 条群组消息'))
        return group_messages

    def create_notifications(self, users, posts, comments, likes):
        notifications = []
        self.stdout.write(f'正在创建通知...')
        
        # 为评论创建通知
        for comment in comments:
            if comment.author != comment.post.author:
                notification = Notification.objects.create(
                    recipient=comment.post.author,
                    actor=comment.author,
                    notification_type='comment',
                    post=comment.post,
                    comment=comment.content
                )
                notifications.append(notification)
        
        # 为点赞创建通知
        for like in likes:
            if like.user != like.post.author:
                notification = Notification.objects.create(
                    recipient=like.post.author,
                    actor=like.user,
                    notification_type='like',
                    post=like.post
                )
                notifications.append(notification)
                
        for user in users[:10]:  
            followers = user.followers.all()[:5]  # 最多5个关注者
            for follower in followers:
                if follower != user:
                    notification = Notification.objects.create(
                        recipient=user,
                        actor=follower,
                        notification_type='follow'
                    )
                    notifications.append(notification)
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(notifications)} 条通知'))
        return notifications