from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

# User Manager - handles creating user
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) 
        user.save()
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self.create_user(email,password,**extra_fields)
    
# This is the custom user model
class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15,unique=True)
    profile_pic = models.URLField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','mobile_number']  # These will be asked when using createsuperuser

    def __str__(self):
        return self.email
    
# for  Post 
class Post(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    post_url = models.URLField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

class Like(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user','post')  # To prevent the same user from liking the same post twice

class Follow(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='follower')
    followed_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='following')
    followed_at = models.DateTimeField(auto_now_add=True)

class Story(models.Model):
    STORY_TYPE_CHOICES = [('photo','photo'),('video','video')]
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    content = models.TextField()
    story_type = models.CharField(max_length=10,choices=STORY_TYPE_CHOICES)
    duration = models.IntegerField(default=30)
    story_url = models.FileField(upload_to='stories/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Story by{self.user.username} at {self.created_at}"
    
class StoryLike(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    story = models.ForeignKey(Story,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','story') 

class StoryView(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    story = models.ForeignKey(Story,on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','story')

class Comment(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"

class CommentLike(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','comment')   