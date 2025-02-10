from email.policy import default
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime


User = get_user_model()


class Profiles(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account_user")
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='book-icon.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
    

    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)  # replaces django pk,  any time u use uuid use primarykey
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes= models.IntegerField(default=0)
    
    def __str__(self):
        return self.user
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="post_comment")
    content = models.TextField()
    sentiment = models.IntegerField(default=None, blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
    
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username
    
class SavePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username
    
class FollowerCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user
    
class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=11)
    text = models.TextField()

    
    def __str__(self):
        return self.name