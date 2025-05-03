from django.urls import path
from .views import RegisterView,LoginView,CreatePostView,UserGetPostView,AllUserGetView,DeleteUserPostView,LikeView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('create-post/',CreatePostView.as_view(),name='create-post'),
    path('user/',UserGetPostView.as_view(),name='user'),
    path('all-users/',AllUserGetView.as_view(),name='all-users'),
    path('delete-post/<int:post_id>/',DeleteUserPostView.as_view(),name='delete-post'),
    path('like-post/<int:post_id>/',LikeView.as_view(),name='like-post'),
]
