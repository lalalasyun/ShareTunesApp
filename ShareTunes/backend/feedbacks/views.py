from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Feedback
from .serializers import FeedbackSerializer

class FeedbackViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """フィードバック管理用ビューセット"""
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """ユーザー自身のフィードバックのみアクセス可能"""
        return Feedback.objects.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        """フィードバック作成時にユーザーを自動設定"""
        serializer.save(user=self.request.user)