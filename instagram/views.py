from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

class RegisterView(APIView):
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message':'User registered successfully',
                'user':{
                    'email':user.email,
                    'username':user.username,
                    'mobile_number':user.mobile_number,
                    'profile_pic':request.build_absolute_uri(user.profile_pic.url) if user.profile_pic else None,
                },
            'tokens':{
                'refresh' : str(refresh),
                'access' : str(refresh.access_token)
            }
            },status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        