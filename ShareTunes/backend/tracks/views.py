from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Track, UserTrackHistory
from .serializers import TrackSerializer, UserTrackHistorySerializer

class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    """楽曲情報を提供するビューセット（読み取り専用）"""
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """クエリパラメータによるフィルタリング"""
        queryset = Track.objects.all()
        
        # 名前による検索
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        # アーティストによる検索
        artist = self.request.query_params.get('artist', None)
        if artist:
            queryset = queryset.filter(artist__icontains=artist)
            
        return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_track_history(request):
    """ユーザーの楽曲再生履歴を取得するAPI"""
    history = UserTrackHistory.objects.filter(user=request.user).select_related('track')
    serializer = UserTrackHistorySerializer(history, many=True)
    return Response(serializer.data)