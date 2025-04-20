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
    # ユーザープロフィール（GET/PUTの両方に対応）
    path('profile/', views.user_profile, name='user_profile'),
    path('profile', views.user_profile, name='user_profile_no_slash'),
    # プロフィール画像アップロード用エンドポイント
    path('profile/picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/picture', views.upload_profile_picture, name='upload_profile_picture_no_slash'),
    # プロフィール設定（GET/PUTの両方に対応）
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/settings', views.profile_settings, name='profile_settings_no_slash'),
    # Spotifyトークン更新
    path('spotify/refresh-token/', views.refresh_spotify_token, name='refresh_spotify_token'),
    path('spotify/refresh-token', views.refresh_spotify_token, name='refresh_spotify_token_no_slash'),
]