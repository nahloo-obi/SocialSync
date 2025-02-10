from django.contrib import admin
from .models import Profiles, Post, LikePost, FollowerCount, Comment, SavePost, ContactUs

# Register your models here.
admin.site.register(Profiles)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowerCount)
admin.site.register(Comment)
admin.site.register(SavePost)
admin.site.register(ContactUs)