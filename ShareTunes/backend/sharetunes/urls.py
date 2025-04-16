from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# 単純なヘルスチェックエンドポイント - JsonResponseを使う単純な実装
def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'API server is running'})

urlpatterns = [
    path('admin/', admin.site.urls),
    # ヘルスチェックエンドポイント
    path('api/health/', health_check, name='health_check'),
    # API エンドポイント
    path('api/auth/', include('users.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/tracks/', include('tracks.urls')),
    path('api/playlists/', include('playlists.urls')),
    path('api/feedback/', include('feedbacks.urls')),
]