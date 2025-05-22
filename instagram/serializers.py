from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=6)
    #The write_only=True makes sure the password is not shown in API responses.
    
    class Meta:
        model = CustomUser
        fields = ['email','username','mobile_number','profile_pic','password']

    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User is deactivated")

        data['user'] = user
        return data
    
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','user','post_url','content','created_at']
        read_only_fields = ['user','created_at']

class UserGetPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    email = serializers.EmailField(source='user.email',read_only=True)
    
    class Meta:
        model = Post
        fields = ['username','email','user','post_url','content','created_at']



class GetAllPostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    post_url = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()
    is_liked = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_is_liked(self, post):
        request = self.context.get('request')
        return Like.objects.filter(user=request.user, post=post).exists()

    def get_is_followed(self, post):
        request = self.context.get('request')
        return Follow.objects.filter(user=request.user, followed_user=post.user).exists()

    def get_user(self, post):
        user = post.user
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.mobile_number,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['user','followed_user','followed_at']
        read_only_fields = ['user','followed_at']

class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','email','mobile_number','profile_pic','password']
        extra_kwargs ={
            'password':{'read_only':True},
            'email':{'required':True},
        }
    def update(self, instance, validated_data):
        # Update all fields except password (read_only)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class CreateStorySerializer(serializers.ModelSerializer):
    story_type = serializers.ChoiceField(choices=[('photo', 'photo'), ('video', 'video')])
    duration = serializers.IntegerField(default=30, read_only=True)
    story_url = serializers.SerializerMethodField()  
    uploaded_file = serializers.FileField(write_only=True, required=True) 
    view_count= serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'user', 'content', 'story_type', 'uploaded_file', 'story_url', 'duration', 'created_at','view_count','is_liked','is_viewed']
        read_only_fields = ['id', 'user', 'duration', 'created_at','view_count','is_liked','is_viewed']

    def get_story_url(self, obj):
        request = self.context.get('request')
        if obj.story_url and hasattr(obj.story_url, 'url'):
            return request.build_absolute_uri(obj.story_url.url)
        return None
    
    def get_view_count(self,obj):
        request = self.context.get('request')
        if request.user == obj.user:
            return obj.storyview_set.count()
        return None
    
    def get_is_liked(self,obj):
        request = self.context.get('request')
        if request.user != obj.user:
            return obj.storylike_set.filter(user=request.user).exists()
        return None #Hide from story owner
    
    def get_is_viewed(self,obj):
        request = self.context.get('request')
        if request.user != obj.user and not request.user.is_staff:
            return obj.storyview_set.filter(user=request.user).exists()
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request.user == instance.user or request.user.is_staff:
            # Admin/Owner: only keep view_count
            representation.pop('is_liked', None)
            representation.pop('is_viewed', None)
        else:
            # Viewer: only keep is_liked, is_viewed
            representation.pop('view_count', None)
        return representation
    
    def create(self, validated_data):
        file = validated_data.pop('uploaded_file')
        return Story.objects.create(story_url=file, **validated_data)
      
    

class StoryLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryLike
        fields = ['user','story','created_at']
        read_only_fields = ['user','created_at']
