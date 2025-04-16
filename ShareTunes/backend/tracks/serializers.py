from rest_framework import serializers
from .models import Track, UserTrackHistory

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'spotify_id', 'name', 'artist', 'album', 'image_url', 
                 'preview_url', 'created_at', 'updated_at')

class UserTrackHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    
    class Meta:
        model = UserTrackHistory
        fields = ('id', 'track', 'played_at', 'created_at')