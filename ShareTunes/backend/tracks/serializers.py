from rest_framework import serializers
from .models import Track, UserTrackHistory

class TrackSerializer(serializers.ModelSerializer):
    # 厳格な形式で曲名、アーティスト名、アルバム名を出力する
    name = serializers.CharField()
    artist = serializers.CharField()
    album = serializers.CharField(allow_null=True)
    
    class Meta:
        model = Track
        fields = ('id', 'spotify_id', 'name', 'artist', 'album', 'image_url', 
                 'preview_url', 'created_at', 'updated_at')

class UserTrackHistorySerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    
    class Meta:
        model = UserTrackHistory
        fields = ('id', 'track', 'played_at', 'created_at')