from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # JWT認証用エンドポイント
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Spotify認証（末尾スラッシュあり・なしの両方に対応）
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/login', views.spotify_login, name='spotify_login_no_slash'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('spotify/callback', views.spotify_callback, name='spotify_callback_no_slash'),
    # ユーザープロフィール
    path('profile/', views.get_user_profile, name='user_profile'),
    path('profile', views.get_user_profile, name='user_profile_no_slash'),
    # Spotifyトークン更新
    path('spotify/refresh-token/', views.refresh_spotify_token, name='refresh_spotify_token'),
    path('spotify/refresh-token', views.refresh_spotify_token, name='refresh_spotify_token_no_slash'),
]