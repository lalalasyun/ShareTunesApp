from rest_framework import serializers
from .models import Recommendation, RecommendedTrack

class RecommendedTrackSerializer(serializers.ModelSerializer):
    # 厳格な形式で曲名、アーティスト名、アルバム名を出力する
    name = serializers.CharField()
    artist = serializers.CharField()
    album = serializers.CharField(allow_null=True)
    
    class Meta:
        model = RecommendedTrack
        fields = ('id', 'spotify_id', 'name', 'artist', 'album', 'image_url', 
                 'preview_url', 'explanation', 'position')

class RecommendationSerializer(serializers.ModelSerializer):
    tracks = RecommendedTrackSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ('id', 'context_description', 'created_at', 'tracks')
        
class RecommendationDetailSerializer(serializers.ModelSerializer):
    tracks = RecommendedTrackSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ('id', 'prompt_text', 'llm_response', 'context_description', 
                 'created_at', 'tracks')