from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Playlist, PlaylistTrack
from tracks.models import Track
from .serializers import PlaylistSerializer, PlaylistDetailSerializer, PlaylistTrackSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    """プレイリスト管理用ビューセット"""
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """ユーザー自身のプレイリストと公開プレイリストを取得"""
        user = self.request.user
        return Playlist.objects.filter(user=user) | Playlist.objects.filter(is_public=True)
    
    def get_serializer_class(self):
        """detailビューではPlaylistDetailSerializerを使用"""
        if self.action == 'retrieve':
            return PlaylistDetailSerializer
        return PlaylistSerializer
    
    def perform_create(self, serializer):
        """プレイリスト作成時にユーザーを自動設定"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_track(self, request, pk=None):
        """プレイリストに楽曲を追加"""
        playlist = self.get_object()
        
        # 自分のプレイリストのみ編集可能
        if playlist.user != request.user:
            return Response(
                {"detail": "このプレイリストを編集する権限がありません。"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        track_id = request.data.get('track')
        position = request.data.get('position')
        
        if not track_id:
            return Response(
                {"track": "楽曲IDは必須です。"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            track = Track.objects.get(pk=track_id)
        except Track.DoesNotExist:
            return Response(
                {"track": "指定された楽曲が見つかりません。"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 位置が指定されていない場合は最後に追加
        if position is None:
            last_position = PlaylistTrack.objects.filter(playlist=playlist).order_by('-position').first()
            position = 0 if last_position is None else last_position.position + 1
        
        # 既に同じ曲が含まれている場合は追加しない
        if PlaylistTrack.objects.filter(playlist=playlist, track=track).exists():
            return Response(
                {"detail": "この曲は既にプレイリストに含まれています。"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 同じpositionの曲があれば、それ以降の曲の位置をずらす
        with transaction.atomic():
            PlaylistTrack.objects.filter(
                playlist=playlist, 
                position__gte=position
            ).update(position=models.F('position') + 1)
            
            playlist_track = PlaylistTrack.objects.create(
                playlist=playlist,
                track=track,
                position=position
            )
        
        serializer = PlaylistTrackSerializer(playlist_track)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_track(self, request, pk=None):
        """プレイリストから楽曲を削除"""
        playlist = self.get_object()
        
        # 自分のプレイリストのみ編集可能
        if playlist.user != request.user:
            return Response(
                {"detail": "このプレイリストを編集する権限がありません。"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        track_id = request.data.get('track')
        
        if not track_id:
            return Response(
                {"track": "楽曲IDは必須です。"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            playlist_track = PlaylistTrack.objects.get(playlist=playlist, track_id=track_id)
        except PlaylistTrack.DoesNotExist:
            return Response(
                {"detail": "指定された楽曲はプレイリストに含まれていません。"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        removed_position = playlist_track.position
        
        with transaction.atomic():
            # 削除する曲の情報を保存
            playlist_track.delete()
            
            # 削除した曲より後の曲の位置を詰める
            PlaylistTrack.objects.filter(
                playlist=playlist, 
                position__gt=removed_position
            ).update(position=models.F('position') - 1)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['put'])
    def reorder_tracks(self, request, pk=None):
        """プレイリスト内の楽曲順序を変更"""
        playlist = self.get_object()
        
        # 自分のプレイリストのみ編集可能
        if playlist.user != request.user:
            return Response(
                {"detail": "このプレイリストを編集する権限がありません。"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        track_orders = request.data.get('track_orders', [])
        
        if not isinstance(track_orders, list):
            return Response(
                {"track_orders": "トラック順序のリストが必要です。"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            for order in track_orders:
                track_id = order.get('track')
                new_position = order.get('position')
                
                if not track_id or new_position is None:
                    return Response(
                        {"detail": "各エントリには'track'と'position'が必要です。"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    playlist_track = PlaylistTrack.objects.get(playlist=playlist, track_id=track_id)
                    playlist_track.position = new_position
                    playlist_track.save()
                except PlaylistTrack.DoesNotExist:
                    return Response(
                        {"detail": f"トラックID {track_id} はプレイリストに存在しません。"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        # 更新後のプレイリストを返す
        serializer = PlaylistDetailSerializer(playlist)
        return Response(serializer.data)