from ast import Pass
from http.client import HTTPResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Profiles, Post, LikePost, FollowerCount, Comment, SavePost
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
from django.db.models import Q
from .forms import CommentForm


from transformers import AutoTokenizer, AutoModelForSequenceClassification
import threading
import torch

tokenizer_distilbert = AutoTokenizer.from_pretrained('distilbert-base-uncased')
distilbertmodel = AutoModelForSequenceClassification.from_pretrained("core/models/models_directory")


class IndexPage(LoginRequiredMixin, ListView):
    login_url = '/signin'
    template_name = 'blog/index2.html'
    context_object_name = 'Profile'
    
    def get_queryset(self):
        try:
            user_object = User.objects.get(username=self.request.user.username)
            user_profile = Profiles.objects.get(user=user_object)

        
        except Profiles.DoesNotExist:
            user_profile= None
        return user_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        liked = LikePost.objects.filter(username=self.request.user.username)
        liked_post_list = []
        
        for likedpost in liked:
            liked_post_list.append(likedpost.post_id)    
        
        posts = Post.objects.all()
        user_following_list= []
        feed = []
        user_following = FollowerCount.objects.filter(follower=self.request.user.username) # where the user is the follower
        for users in user_following:
            user_following_list.append(users.user)  #get the followed people
            
        for usernames in user_following_list:
            feed_lists = Post.objects.filter(user=usernames)
            feed.append(feed_lists)
            
        feed_list = list(chain(*feed))
        
          #user suggestions
        all_users = User.objects.all()
        user_following_all = []
        
        for user in user_following:
            user_list = User.objects.get(username=user.user)
            user_following_all.append(user_list)
            
            
        new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
        current_user = User.objects.filter(username=self.request.user.username)
        final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
        random.shuffle(final_suggestions_list)
        
        username_profile = []
        username_profile_list = []
        
        for users in final_suggestions_list:
            username_profile.append(users.id)
        for ids in username_profile:
            profile_lists = Profiles.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        suggestions_username_profile_list = list(chain(*username_profile_list))

        sentiment_counts_per_post = {}

        for post in feed_list:
            post_comment = post.post_comment.all().count()
            positive_sentiment_count = post.post_comment.filter(sentiment=1).count()
            negative_sentiment_count = post.post_comment.filter(sentiment=0).count()

            if post_comment > 0:
                if positive_sentiment_count > negative_sentiment_count:
                    sentiment_counts_per_post[post.user] = "Content fosters positive engagement!!"  
                elif negative_sentiment_count > positive_sentiment_count:
                    sentiment_counts_per_post[post.user] = "Engagement skewed towards Negativity!!" 
                else:
                    sentiment_counts_per_post[post.user] = "Engagement showcases diverse perspectives!!" 
                        
                        
                context['sentiment_counts_per_post'] = sentiment_counts_per_post
                
       # context["user_profile"] = self.user_profile
        context["posts"]= feed_list
        context['suggestions_username_profile_list']= suggestions_username_profile_list[:4]
        context['liked'] = liked_post_list
        
        return context
    

class Search(LoginRequiredMixin, View):
    login_url = '/signin'

    def post(self, *args, **kwargs):
        user_object = User.objects.get(username=self.request.user.username)
        user_profile = Profiles.objects.get(user=user_object)
        context = {}
        
        username = self.request.POST['username']
        username_object = User.objects.filter(Q(username__icontains=username))
        
        username_profile = []
        username_profile_list=[]
        
        for users in username_object:
            
            username_profile.append(users.id)
        
        for ids in username_profile:
            profile_list = Profiles.objects.filter(id_user=ids)
            username_profile_list.append(profile_list)
            
            
        username_profile_list = list(chain(*username_profile_list))
        context['user_profile']=user_profile
        context['username_profile_list'] = username_profile_list
        
        return render(self.request, 'blog/search.html', context)  
        
    
    

@login_required(login_url='signin')    
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    
    post = Post.objects.get(id=post_id)
    
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')
    
def save_post(request, pk):
    username = request.user.username        
    savepost_filter = SavePost.objects.filter(post_id=pk, username=username).first()
    if savepost_filter == None:
        new_savedpost = SavePost.objects.create(post_id=pk, username=username)
        new_savedpost.save()
        return redirect('/')
    else:
        savepost_filter.delete()
        return redirect('/')
    
def display_saved_post(request):
    saved_post = SavePost.objects.filter(username=request.user.username)
    savedpost_list_id = []
    saved_post_list=[]
    
    
    for post_id in saved_post:
        savedpost_list_id.append(post_id.post_id)
    for postID in savedpost_list_id:
        savedpost_feed = Post.objects.filter(id=postID)
        saved_post_list.append(savedpost_feed)
        
    savedfeed_list = list(chain(*saved_post_list))
    
    context = {
        "post": savedfeed_list
    }
    
    return render(request, 'blog/savedpostpage.html', context)
        
    
    
class ProfilePage(LoginRequiredMixin, DetailView):
    login_url = '/signin'

    template_name = 'blog/profile.html'
    
    
    def get_object(self, queryset=None):
        user_object = User.objects.get(username=self.kwargs['pk'])
        user_profile = Profiles.objects.get(user=user_object)
        return user_profile
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_object = User.objects.get(username=self.kwargs['pk'])
        user_profile = Profiles.objects.get(user=user_object)
        user_posts = Post.objects.filter(user=self.kwargs['pk'])
        user_post_length = len(user_posts)
        
        follower = self.request.user.username
        user = self.kwargs['pk']
        if FollowerCount.objects.filter(follower=follower, user=user).first():
            button_text = 'Unfollow'
        else:
            button_text = 'Follow'
            
        user_followers = len(FollowerCount.objects.filter(user=self.kwargs['pk']))
        user_following = len(FollowerCount.objects.filter(follower=self.kwargs['pk']))
        
        context['user_object'] =user_object
        context['user_profile'] =user_profile
        context['user_post'] =user_posts
        context['user_post_length'] =user_post_length
        context['button_text'] =button_text
        context['user_followers'] =user_followers
        context['user_following'] =user_following
        
        return context
    
    


class SettingsPage(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            user_profile = Profiles.objects.get(user=self.request.user)
        except Profiles.DoesNotExist:
            user_profile = None
            
        return render(self.request, 'blog/setting.html', {'user_profile': user_profile})

    
    
    def post(self, *args, **kwargs):
        try:
            user_profile = Profiles.objects.get(user=self.request.user)
            if self.request.FILES.get('image')==None:
                    image = user_profile.profileimg
                    bio = self.request.POST['bio']
                    location = self.request.POST['location']
                    
                    user_profile.profileimg = image
                    user_profile.bio = bio
                    user_profile.location = location
                    user_profile.save()
                    
            if self.request.FILES.get('image') != None:
                image = self.request.FILES.get('image')
                bio = self.request.POST['bio']
                location = self.request.POST['location']
                
                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
                
            return redirect("settings")
        except Profiles.DoesNotExist:
            user_profile = None
            return redirect("settings")
        
    
    
class SignupPage(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'blog/signup.html')
        
        
    def post(self, *args, **kwargs):
        username = self.request.POST['username']  #from html form name
        email = self.request.POST['email']
        password = self.request.POST['password']
        password2 = self.request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(self.request, "Email Taken")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(self.request, "Username taken")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                user_login = auth.authenticate(username=username, password=password)
                auth.login(self.request, user_login)
                
                user_model = User.objects.get(username=username)
                new_profile = Profiles.objects.create(
                    user=user_model,
                    id_user= user_model.id
                )
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(self.request, "password doesnt match")
            return redirect('signup')


class SigninPage(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'blog/signin.html')
        
    def post(self, *args, **kwargs):
        username = self.request.POST['username']
        password = self.request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(self.request, user)
            return redirect('/')
        else:
            messages.info(self.request, "Invalid Credentials")
            return redirect('signin')
            

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin') 
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']
        
        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    
    else:
        return redirect("/")
    
    
@login_required(login_url='signin')
def upload(request):
    if request.method=="POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect("/")
    

def checkCommentSentiment(comment, post):
    text = comment.content
    #tokenized the comments 
    tokenized_texts = tokenizer_distilbert(text, padding=True, truncation=True, return_tensors='pt')

    with torch.no_grad():
        #feed the tokenizex text to the distilbert model for inference
        outputs = distilbertmodel(**tokenized_texts)
        #get predictions
        predictions = torch.argmax(outputs.logits, dim=1)

    sentiment = 1 if predictions.item() == 1 else 0
    #save sentiment value to the database
    if sentiment == 1:
        comment.sentiment = sentiment
        comment.save()
    
    if sentiment == 0 :
        comment.sentiment = sentiment
        comment.save()
        
def postOverview(request, pk, sentimentContext={}, swap = {}):
    form = CommentForm()
    post = Post.objects.get(id=pk)
    comment = Comment.objects.filter(post=pk)
    comment_count = Comment.objects.filter(post=pk).count()
    context = {
        "form": form,
        "post": post,
        "posts_comments" : comment,
        'posts_comments_count': comment_count,
        }

    if request.method=='POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = Comment(
                user= request.user,
                content = request.POST['content'],
                post = post         
            )
            comment.save()
            #perform the concurrent operation
            threading.Thread(target=checkCommentSentiment, args=(comment, 6)).start()
            return redirect(request.path + '#comments_path')
    if swap:
        context['sentiment_redirect'] = True 
        context.update(sentimentContext)
        return render(request, 'blog/post.html', context)

    context.update(sentimentContext)
    return render(request, 'blog/post.html', context)
    

def postCommentSentiment(request, pk):
    post_id = pk
    optionValue = request.GET.get('comments_value')

    #option for positive comments
    if int(optionValue) == 1:
        comment = Comment.objects.filter(post=post_id, sentiment=1)
        context = {"posts_comments" : comment}
    
    #option for negative comments
    if int(optionValue) == 0:
        comment = Comment.objects.filter(post=post_id, sentiment=0)
        context = {"posts_comments" : comment} 
    
    #option for all comments
    if int(optionValue) == 2:
        comment = Comment.objects.filter(post=post_id)
        context = {"posts_comments" : comment}

    swap = {"redirecting" : True}
    
    response = postOverview(request,post_id,context, swap)
    
    return response


