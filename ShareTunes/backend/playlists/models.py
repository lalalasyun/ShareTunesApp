from django.db import models
from django.contrib.auth.models import User
from tracks.models import Track

class Playlist(models.Model):
    """ユーザープレイリストモデル"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    tracks = models.ManyToManyField(Track, through='PlaylistTrack', related_name='playlists')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'プレイリスト'
        verbose_name_plural = 'プレイリスト'
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class PlaylistTrack(models.Model):
    """プレイリストと楽曲の中間テーブル（順序管理用）"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'プレイリスト楽曲'
        verbose_name_plural = 'プレイリスト楽曲'
        ordering = ['position']
        # 同じプレイリスト内で同じポジションは許可しない
        unique_together = ('playlist', 'position')
        
    def __str__(self):
        return f"{self.playlist.name} - {self.track.name} (位置: {self.position})"