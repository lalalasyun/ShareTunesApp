from django.db import models
from django.contrib.auth.models import User
from recommendations.models import RecommendedTrack

class Feedback(models.Model):
    """推薦楽曲に対するフィードバックモデル"""
    FEEDBACK_CHOICES = (
        ('like', '👍 Like'),
        ('dislike', '👎 Dislike'),
        ('neutral', '😐 Neutral'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    track = models.ForeignKey(RecommendedTrack, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_CHOICES, default='neutral')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'フィードバック'
        verbose_name_plural = 'フィードバック'
        # 1ユーザーが1トラックに対して1つのフィードバックのみ
        unique_together = ('user', 'track')
        
    def __str__(self):
        return f"{self.user.username} - {self.track.name} ({self.get_feedback_type_display()})"