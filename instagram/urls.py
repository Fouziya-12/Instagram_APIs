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
    path('story/<int:user_id>/',GetUserStoryView.as_view(),name='get-user-story'),
    path('story-id/<int:story_id>/', GetStorybySid.as_view(), name='get-story-by-sid'),
    path('story-like/<int:story_id>/', StoryLikeView.as_view(), name='story-like'),
    path('story-unlike/<int:story_id>/',StoryUnLikeView.as_view(),name='story-unlike'),
   

]
 