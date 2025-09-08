from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    email=models.EmailField(unique=True)
    bio=models.TextField(max_length=500,null=True)
    birth_date=models.DateField(null=True,blank=True)
    avatar=models.ImageField(null=True,blank=True,upload_to='avatars/')
    following=models.ManyToManyField('self',related_name='followers',blank=True,symmetrical=False)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username
    def get_followers_count(self):
        return self.followers.count()
    def get_following_count(self):
        return self.following.count()