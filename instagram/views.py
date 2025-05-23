from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404



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


class GetAllPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_posts = Post.objects.select_related('user').all()
        serializer = GetAllPostSerializer(all_posts, many=True, context={'request': request})
        return Response({
            'post_total_count': all_posts.count(),
            'posts': serializer.data
        })


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


class UnFollowView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,user_id):
        if request.user.id == user_id:
            return Response({'error':'You cannot follow yourself'},status=status.HTTP_400_BAD_REQUEST)
        try:
            followed_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow = Follow.objects.get(user=request.user,followed_user=followed_user)
            follow.delete()
            return Response({'message':'Sucessfully unfollowed the user'},status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            return Response({'error':'You are not following the user'},status=status.HTTP_400_BAD_REQUEST)
   

class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request):
        user = request.user
        serializer = EditProfileSerializer(user,data=request.data,partial=True) # partial=True allows updating some fields
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Profile updated successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class DeleteProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self,request):
        user = request.user
        username = user.username 
        user.delete()
        return Response({'message':f'User {username} profile deleted successfully'},status=status.HTTP_204_NO_CONTENT)


class CreateStoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        serializer = CreateStorySerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
           serializer.save(user=request.user)
           return Response({'message':'Story created successfully','story':serializer.data},status=status.HTTP_201_CREATED) 
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class GetStoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        stories = Story.objects.filter(user=request.user,created_at__gte=twenty_four_hours_ago).order_by('-created_at')

        # if not stories.exists():
        #     return Response({"error":"Story not found or expired"},status=status.HTTP_404_NOT_FOUND)
        
        # for story in stories:
        #     if story.user  != request.user:
        #         StoryView.objects.get_or_create(user=request.user,story=story)

        serializer = CreateStorySerializer(stories,many=True,context={'request':request})
        return Response({'stories':serializer.data},status=status.HTTP_200_OK)
    
   
class GetUserStoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,user_id):
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        stories = Story.objects.filter(user_id=user_id,created_at__gte=twenty_four_hours_ago).order_by('-created_at')

        if not stories.exists():
            return Response({"error": "Story not found or expired."}, status=status.HTTP_404_NOT_FOUND)
        
        for story in stories:
            if story.user != request.user:
                StoryView.objects.get_or_create(user=request.user, story=story)

        serializer = CreateStorySerializer(stories,many=True,context={'request':request})
        return Response({'stories':serializer.data},status=status.HTTP_200_OK)


class GetStorybySid(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,story_id):
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        try:
            story = Story.objects.get(id=story_id,created_at__gte=twenty_four_hours_ago)
        except Story.DoesNotExist:
            return Response({"error":"Story not found or expired."},status=status.HTTP_404_NOT_FOUND)

        # if not story.exists():
        #     return Response({"error": "Story not found or expired."}, status=status.HTTP_404_NOT_FOUND)
        
        # story = stories.first()

        if story.user != request.user:
            StoryView.objects.get_or_create(user=request.user,story=story)

        serializer = CreateStorySerializer(story,context={'request':request})
        return Response({'story':serializer.data},status=status.HTTP_200_OK)


class StoryLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, story_id):
        try:
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return Response({'error': 'Story not found or expired'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent user from liking their own story
        if story.user == request.user:
            return Response({'error': 'You cannot like your own story'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already liked the story
        if StoryLike.objects.filter(user=request.user, story=story).exists():
            return Response({'error': 'You have already liked this story'}, status=status.HTTP_400_BAD_REQUEST)

        # Like the story
        StoryLike.objects.create(user=request.user, story=story)
        return Response({'message': 'Story liked successfully'}, status=status.HTTP_201_CREATED)

class StoryUnLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,story_id):
        try:
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return Response({'error':'Story not found or expired'},status=status.HTTP_404_NOT_FOUND)
        
        try:
            like = StoryLike.objects.get(user=request.user,story=story)
            like.delete()
            return Response({'message':'Story unliked successfully'},status=status.HTTP_200_OK)
        except StoryLike.DoesNotExist:
            return Response({'error':'You have not liked this story yet'},status=status.HTTP_400_BAD_REQUEST)


class DeleteStory(APIView):
    permission_classes = [IsAuthenticated]
    # def delete(self, request, story_id):
    #     try:
    #         story = Story.objects.get(id=story_id)
    #     except Story.DoesNotExist:
    #         return Response({'error': 'Story not found'}, status=status.HTTP_404_NOT_FOUND)

    # this is the shortcut of the above code
    def delete(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)  # Get story regardless of owner

        if story.user != request.user:
            return Response(
                {'error': 'You are not allowed to delete this story'},
                status=status.HTTP_403_FORBIDDEN
            )

        story.delete()
        return Response({'message': 'Story deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,post_id):
        post = get_object_or_404(Post,id=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user,post=post)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,comment_id):
        comment = get_object_or_404(Comment,id=comment_id)

        if CommentLike.objects.filter(user=request.user,comment=comment).exists():
            return Response({'error':'You have already liked this comment'},status=status.HTTP_400_BAD_REQUEST)
        
        CommentLike.objects.create(user=request.user,comment=comment)
        return Response({'message':'Comment liked successfully'},status=status.HTTP_201_CREATED)
    
class CommentUnlikeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request,comment_id):
        comment = get_object_or_404(Comment,id=comment_id)

        try:
            like = CommentLike.objects.get(user=request.user,comment=comment)
            like.delete()
            return Response({'message':'Comment unliked successfully'},status=status.HTTP_200_OK)
        except CommentLike.DoesNotExist:
            return Response({'error':'You have not liked this comment yet'},status=status.HTTP_400_BAD_REQUEST)




