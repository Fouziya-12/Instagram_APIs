from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,LoginSerializer,PostSerializer,UserGetPostSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Post
from rest_framework.permissions import IsAuthenticated


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
 
        
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful',
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'mobile_number': user.mobile_number,
                    'profile_pic': user.profile_pic,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  #set logged-in user
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserGetPostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        user_posts = Post.objects.filter(user=request.user)
        serializer = UserGetPostSerializer(user_posts,many=True)
        return Response(serializer.data)