from rest_framework import serializers
from .models import CustomUser,Post,Like,Follow
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