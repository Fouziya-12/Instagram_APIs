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

class AllUserGetPostSerializer(serializers.ModelSerializer):
   username = serializers.CharField(source='user.username',read_only=True)
   email = serializers.EmailField(source='user.email',read_only=True)
    
   class Meta:
        model = Post
        fields = ['username','email','user','post_url','content','created_at']

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
            'password':{'write_only':True,'required':False},
            'email':{'read_only':True},
        }
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance