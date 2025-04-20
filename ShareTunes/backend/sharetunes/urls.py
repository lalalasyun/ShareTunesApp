from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static

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

# 開発環境でのメディアファイルの提供設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)