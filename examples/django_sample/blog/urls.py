"""URL configuration for blog app."""

from django.urls import path
from blog.views import post_list, post_detail, create_post

urlpatterns = [
    path('', post_list, name='post_list'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('create/', create_post, name='create_post'),
]
