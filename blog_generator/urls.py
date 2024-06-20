from django.contrib import admin
from django.urls import path
from blog_generator import views

urlpatterns = [
    path('', views.home, name='home'),
]