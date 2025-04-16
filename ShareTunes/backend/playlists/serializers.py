from rest_framework import serializers
from .models import Playlist, PlaylistTrack
from tracks.serializers import TrackSerializer

class PlaylistTrackSerializer(serializers.ModelSerializer):
    track_details = TrackSerializer(source='track', read_only=True)
    
    class Meta:
        model = PlaylistTrack
        fields = ('id', 'track', 'track_details', 'position', 'added_at')
        read_only_fields = ('added_at',)

class PlaylistSerializer(serializers.ModelSerializer):
    track_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ('id', 'name', 'description', 'is_public', 'track_count', 
                 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_track_count(self, obj):
        return obj.tracks.count()

class PlaylistDetailSerializer(serializers.ModelSerializer):
    playlist_tracks = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ('id', 'name', 'description', 'is_public', 'owner',
                 'playlist_tracks', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
        
    def get_playlist_tracks(self, obj):
        playlist_tracks = PlaylistTrack.objects.filter(playlist=obj).order_by('position')
        return PlaylistTrackSerializer(playlist_tracks, many=True).data
        
    def get_owner(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
        }