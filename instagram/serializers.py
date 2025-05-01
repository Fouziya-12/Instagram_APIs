from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=6)
    #The write_only=True makes sure the password is not shown in API responses.
    
    class Meta:
        model = CustomUser
        fields = ['email','username','mobile_number','profile_pic','password']

    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
    