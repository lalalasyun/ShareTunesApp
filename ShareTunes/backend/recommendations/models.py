from django.db import models
from django.contrib.auth.models import User

class Recommendation(models.Model):
    """音楽推薦モデル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    prompt_text = models.TextField(help_text="LLMに送られたプロンプトテキスト")
    llm_response = models.TextField(help_text="LLMからの生のレスポンス")
    context_description = models.CharField(max_length=255, blank=True, null=True, help_text="推薦コンテキスト(気分、状況など)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '楽曲推薦'
        verbose_name_plural = '楽曲推薦'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}への推薦 ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class RecommendedTrack(models.Model):
    """推薦された楽曲モデル"""
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name='tracks')
    spotify_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    preview_url = models.URLField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True, help_text="この曲が推薦された理由の説明")
    position = models.PositiveIntegerField(default=0, help_text="推薦リスト内での位置")
    
    class Meta:
        verbose_name = '推薦楽曲'
        verbose_name_plural = '推薦楽曲'
        ordering = ['position']
        
    def __str__(self):
        return f"{self.name} by {self.artist}"