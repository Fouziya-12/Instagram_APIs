from django.urls import path
from .views import RegisterView,LoginView,CreatePostView,UserGetPostView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('create-post/',CreatePostView.as_view(),name='create-post'),
    path('user/',UserGetPostView.as_view(),name='user'),
]
