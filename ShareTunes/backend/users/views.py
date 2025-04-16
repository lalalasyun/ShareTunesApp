import os
import requests
import json
import base64
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import UserProfileSerializer

@api_view(['GET'])
@permission_classes([AllowAny])  # 認証なしで必ずアクセス可能であることを明示
def spotify_login(request):
    """Spotifyログイン用URLを生成"""
    scope = "user-read-private user-read-email user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative"
    
    # Spotify認証URLを構築
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": scope,
        "show_dialog": True
    }
    
    # URLクエリパラメータを生成
    query_params = "&".join([f"{key}={val}" for key, val in params.items()])
    auth_url = f"{auth_url}?{query_params}"
    
    # デバッグ情報を出力
    print(f"認証URL生成: {auth_url}")
    
    return Response({"auth_url": auth_url})

@api_view(['GET'])
@permission_classes([AllowAny])  # 認証なしで必ずアクセス可能であることを明示
def spotify_callback(request):
    """Spotifyコールバック処理"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    # デバッグ情報出力
    print(f"Spotifyコールバック受信: code={code}, error={error}")
    
    # エラーがある場合は処理中断
    if error:
        print(f"Spotifyエラー: {error}")
        # フロントエンドにエラーメッセージ付きでリダイレクト
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        error_url = f"{frontend_url}/?error={error}"
        return redirect(error_url)
    
    # コードが存在しない場合もエラー
    if not code:
        print("認証コードがありません")
        # フロントエンドにエラーメッセージ付きでリダイレクト
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        error_url = f"{frontend_url}/?error=認証コードが受信できませんでした"
        return redirect(error_url)
    
    try:
        # アクセストークンのリクエスト
        auth_token = base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()
        
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI
        }
        
        # デバッグ情報
        print(f"Spotifyトークンリクエスト: redirect_uri={settings.SPOTIFY_REDIRECT_URI}")
        
        # トークンリクエスト
        res = requests.post(token_url, headers=headers, data=data)
        
        if res.status_code != 200:
            print(f"トークン取得エラー: {res.status_code}, {res.text}")
            # フロントエンドにエラーメッセージ付きでリダイレクト
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            error_url = f"{frontend_url}/?error=トークン取得に失敗しました: {res.status_code}"
            return redirect(error_url)
        
        token_data = res.json()
        print("トークン取得成功")
        
        # ユーザー情報の取得
        user_url = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        
        user_res = requests.get(user_url, headers=headers)
        
        if user_res.status_code != 200:
            print(f"ユーザー情報取得エラー: {user_res.status_code}, {user_res.text}")
            # フロントエンドにエラーメッセージ付きでリダイレクト
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            error_url = f"{frontend_url}/?error=ユーザー情報の取得に失敗しました"
            return redirect(error_url)
        
        spotify_user = user_res.json()
        print(f"Spotifyユーザー情報取得成功: {spotify_user.get('display_name')}")
        
        # プロフィール画像URLの取得
        profile_image_url = None
        if 'images' in spotify_user and spotify_user['images']:
            # 最も高解像度の画像を選択（通常は配列の最初のもの）
            profile_image_url = spotify_user['images'][0]['url']
            print(f"プロフィール画像URL: {profile_image_url}")
        
        # ユーザー名として表示名を使用
        display_name = spotify_user.get('display_name', '')
        # 表示名がない場合はSpotify IDを使用
        if not display_name:
            username = spotify_user['id']
        else:
            # スペースを除去してユーザー名に適した形に
            base_username = ''.join(display_name.split())
            # 既存のユーザー名と衝突しないようにする
            username = base_username
            counter = 1
            # 同じユーザー名が存在する場合は番号を付ける
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        
        print(f"ユーザー名として使用: {username}")
        
        # ユーザー作成または取得（Spotify IDで検索、存在しなければ新規作成）
        user = None
        try:
            # まずSpotify IDでプロフィールを検索
            profile = UserProfile.objects.get(spotify_id=spotify_user['id'])
            user = profile.user
            # ユーザーが見つかった場合、ユーザー名を更新
            user.first_name = spotify_user.get('display_name', '').split(' ')[0] if spotify_user.get('display_name') else ''
            user.last_name = ' '.join(spotify_user.get('display_name', '').split(' ')[1:]) if spotify_user.get('display_name') and len(spotify_user.get('display_name', '').split(' ')) > 1 else ''
            user.email = spotify_user.get('email', user.email)
            user.save()
            print(f"既存ユーザーを更新: {user.username}")
        except UserProfile.DoesNotExist:
            # 新規ユーザーの作成
            user = User.objects.create(
                username=username,
                email=spotify_user.get('email', ''),
                first_name=spotify_user.get('display_name', '').split(' ')[0] if spotify_user.get('display_name') else '',
                last_name=' '.join(spotify_user.get('display_name', '').split(' ')[1:]) if spotify_user.get('display_name') and len(spotify_user.get('display_name', '').split(' ')) > 1 else '',
            )
            print(f"新規ユーザーを作成: {user.username}")
        
        # プロフィール更新または作成
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.spotify_id = spotify_user['id']
        profile.spotify_access_token = token_data['access_token']
        profile.spotify_refresh_token = token_data['refresh_token']
        profile.spotify_token_expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
        
        # プロフィール画像URLを外部URL（Spotify）から直接保存
        if profile_image_url:
            profile.external_profile_image_url = profile_image_url
        
        profile.save()
        
        # JWTトークン生成
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        print(f"認証成功: ユーザー {spotify_user['id']}")
        
        # フロントエンドにリダイレクト（トークン付き）
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        redirect_url = f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
        
        return redirect(redirect_url)
        
    except Exception as e:
        print(f"認証処理中の予期せぬエラー: {str(e)}")
        # フロントエンドにエラーメッセージ付きでリダイレクト
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        error_url = f"{frontend_url}/?error=認証処理中にエラーが発生しました"
        return redirect(error_url)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """ユーザープロフィール取得"""
    print('===== ユーザープロファイル取得リクエスト =====')
    print(f'認証ヘッダー: {request.headers.get("Authorization", "なし")}')
    print(f'ユーザー情報: {request.user}')
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        data = serializer.data
        
        # プロフィール画像の処理
        # 1. ローカルにアップロードされた画像があればその完全なURLを構築
        if profile.profile_image:
            request_base = f"{request.scheme}://{request.get_host()}"
            data['profile_image'] = request_base + profile.profile_image.url
            
        # 2. Spotifyの外部プロフィール画像URLがあれば、それをAPIレスポンスのprofile_imageフィールドにセット
        if profile.external_profile_image_url:
            # 外部URLがある場合は、それを優先してprofile_imageフィールドに設定
            data['profile_image'] = profile.external_profile_image_url
        
        print('プロファイル取得成功')
        return Response(data)
    except UserProfile.DoesNotExist:
        print('プロファイルが見つかりません')
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'予期せぬエラー: {str(e)}')
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def refresh_spotify_token(request):
    """Spotifyトークンの更新"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        # トークンの有効期限確認
        if profile.spotify_token_expires_at and profile.spotify_token_expires_at > timezone.now():
            return Response({"message": "Token still valid", "expires_at": profile.spotify_token_expires_at})
        
        if not profile.spotify_refresh_token:
            return Response({"error": "No refresh token available"}, status=status.HTTP_400_BAD_REQUEST)
        
        # リフレッシュトークンでアクセストークン更新
        auth_token = base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": profile.spotify_refresh_token
        }
        
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        
        if res.status_code != 200:
            return Response({"error": "Failed to refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_data = res.json()
        
        # トークン情報更新
        profile.spotify_access_token = token_data['access_token']
        if 'refresh_token' in token_data:
            profile.spotify_refresh_token = token_data['refresh_token']
        
        profile.spotify_token_expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
        profile.save()
        
        return Response({
            "message": "Token refreshed successfully", 
            "access_token": token_data['access_token'],
            "expires_at": profile.spotify_token_expires_at
        })
        
    except UserProfile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)