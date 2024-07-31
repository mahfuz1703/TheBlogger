from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('singin', views.signin, name='singin'),
    path('signup', views.signup, name='singup'),
    path('signout', views.signout, name='signout'),
    path('all_blogs', views.all_saved_blog, name='all_blogs'),
    path('blog_details', views.blog_details, name='blog_details'),
    path('generate-blog', views.generate_blog, name='generate-blog'),
]