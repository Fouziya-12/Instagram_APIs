from django.urls import path
from .views import *

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('create-post/',CreatePostView.as_view(),name='create-post'),
    path('get-user-post/',UserGetPostView.as_view(),name='get-user-post'),
    path('get-all-posts/',GetAllPostsView.as_view(),name='get-all-posts'),
    path('delete-post/<int:post_id>/',DeleteUserPostView.as_view(),name='delete-post'),
    path('like-post/<int:post_id>/',LikeView.as_view(),name='like-post'),
    path('unlike-post/<int:post_id>/',UnLikeView.as_view(),name='unlike-post'),
    path('follow-user/<int:user_id>/',FollowView.as_view(),name='follow-user'),
    path('unfollow-user/<int:user_id>/',UnFollowView.as_view(),name='unfollow-user'),
    path('edit-profile/',EditProfileView.as_view(),name='edit-profile'),
    path('delete-profile/',DeleteProfileView.as_view(),name='delete-profile'),
    path('create-story/',CreateStoryView.as_view(),name='create-story'),
    path('get-stories/',GetStoriesView.as_view(),name='get-stories'),

]
