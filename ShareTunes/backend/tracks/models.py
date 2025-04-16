from django.db import models
from django.contrib.auth.models import User

class Track(models.Model):
    """楽曲モデル"""
    spotify_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    preview_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '楽曲'
        verbose_name_plural = '楽曲'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} by {self.artist}"

class UserTrackHistory(models.Model):
    """ユーザーの楽曲再生履歴"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='track_history')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='user_history')
    played_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '楽曲再生履歴'
        verbose_name_plural = '楽曲再生履歴'
        ordering = ['-played_at']

    def __str__(self):
        return f"{self.user.username} - {self.track.name} ({self.played_at})"