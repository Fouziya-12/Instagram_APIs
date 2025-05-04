from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,LoginSerializer,PostSerializer,UserGetPostSerializer,AllUserGetPostSerializer,LikeSerializer,FollowSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Post,Like,Follow
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
    
class AllUserGetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        posts = Post.objects.all()
        serializer = AllUserGetPostSerializer(posts,many=True)
        return Response(serializer.data)
    
class DeleteUserPostView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,post_id):
        try:
            post = Post.objects.get(id=post_id,user=request.user)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'},status=status.HTTP_404_NOT_FOUND)
        
        post.delete()
        return Response({'message':'Post deleted successfully'},status=status.HTTP_204_NO_CONTENT)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'},status=status.HTTP_404_NOT_FOUND)
     
        # Check if the user has already liked the post
        if Like.objects.filter(user=request.user,post=post).exists():
            return Response({'error':'You have already liked this post'},status=status.HTTP_400_BAD_REQUEST)  
        
        # create the like
        Like.objects.create(user=request.user,post=post)
        return Response({'message':'Post liked successfully'},status=status.HTTP_201_CREATED)
       
class UnLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'},status=status.HTTP_404_NOT_FOUND)    
        
        try:
            like = Like.objects.get(user=request.user,post=post)
            like.delete()
            return Response({'message':'Post unliked successfully'},status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'error':'You have not liked this post yet'},status=status.HTTP_400_BAD_REQUEST)

class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,user_id):
        if request.user.id == user_id:
            return Response({'error':'You cannot follow yourself'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            followed_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)
        
        if Follow.objects.filter(user=request.user,followed_user=followed_user).exists():
            return Response({'error':'You are already following this user'},status=status.HTTP_400_BAD_REQUEST)
        
        Follow.objects.create(user=request.user,followed_user=followed_user)
        return Response({'message':'successfully followed the user'},status=status.HTTP_201_CREATED)




