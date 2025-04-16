from rest_framework import serializers
from .models import Feedback
from recommendations.serializers import RecommendedTrackSerializer

class FeedbackSerializer(serializers.ModelSerializer):
    track_details = RecommendedTrackSerializer(source='track', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ('id', 'track', 'track_details', 'feedback_type', 'comment', 'created_at')
        read_only_fields = ('created_at',)