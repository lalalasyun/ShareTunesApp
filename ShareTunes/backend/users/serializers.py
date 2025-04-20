from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'spotify_id', 'profile_image', 'external_profile_image_url', 
                 'bio', 'display_name', 'favorite_genres', 'preferences', 'created_at', 'updated_at')
        read_only_fields = ('spotify_access_token', 'spotify_refresh_token', 'spotify_token_expires_at')