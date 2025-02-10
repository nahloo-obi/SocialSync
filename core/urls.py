from django.urls import path
from . import views
from .views import IndexPage, ProfilePage, Search, SettingsPage, SignupPage, SigninPage


urlpatterns = [
    path('', IndexPage.as_view(), name="index"),
    path('settings', SettingsPage.as_view(), name="settings"),
    path('upload', views.upload, name="upload"),
    path('follow', views.follow, name="follow"),
    path('search', Search.as_view(), name="search"),
    path('profile/<str:pk>', ProfilePage.as_view(), name="profile"),
    path('post/<str:pk>', views.postOverview, name="post"),
    path('sentiment-comments/<str:pk>', views.postCommentSentiment, name="sentiment-comments"),
    path('save-post/<str:pk>', views.save_post, name="save-post"),
    path('like-post', views.like_post, name="like-post"),
    path('display-saved-post', views.display_saved_post, name="display-saved-post"),
    path('signup', SignupPage.as_view(), name='signup'),
    path('signin', SigninPage.as_view(), name='signin'),
    path('logout', views.logout, name='logout'),
    path("about", views.about, name="about"),
    path("contact-us", views.contact_us, name="contact_us"),
    
]
