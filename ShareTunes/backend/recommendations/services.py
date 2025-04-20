import json
import requests
import os
from django.conf import settings
from django.utils import timezone
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import google.generativeai as genai

from users.models import UserProfile

class RecommendationService:
    """LLMを活用した音楽推薦サービス"""
    
    def __init__(self, user):
        self.user = user
        try:
            self.user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            self.user_profile = None
            
        self.spotify_client = None
        if settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET:
            self.spotify_client = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=settings.SPOTIFY_CLIENT_ID,
                    client_secret=settings.SPOTIFY_CLIENT_SECRET
                )
            )
    
    def get_spotify_user_data(self):
        """Spotifyから最近の再生履歴とお気に入りアーティストを取得"""
        if not self.user_profile or not self.user_profile.spotify_access_token:
            return None
            
        if self.user_profile.spotify_token_expires_at and self.user_profile.spotify_token_expires_at < timezone.now():
            # Tokenが期限切れ
            return None
            
        # Spotifyクライアント初期化
        sp = spotipy.Spotify(auth=self.user_profile.spotify_access_token)
        
        try:
            # 最近再生した20曲を取得
            recent_tracks_raw = sp.current_user_recently_played(limit=20)
            # トップアーティスト10組を取得
            top_artists_raw = sp.current_user_top_artists(limit=10, time_range='medium_term')
            # トップトラック10曲を取得
            top_tracks_raw = sp.current_user_top_tracks(limit=10, time_range='medium_term')

            # 必要なデータのみ抽出して軽量化
            recent_tracks = {
                'items': [
                    {
                        'track': {
                            'id': item['track']['id'],
                            'name': item['track']['name'],
                            'artists': [{'id': artist['id'], 'name': artist['name']} for artist in item['track']['artists']],
                            'album': {
                                'id': item['track']['album']['id'],
                                'name': item['track']['album']['name'],
                                'images': item['track']['album']['images'][:1]  # 一番大きい画像のみ保存
                            }
                        },
                        'played_at': item['played_at']
                    } for item in recent_tracks_raw['items'][:10]  # 最新10曲に制限
                ]
            }
            
            top_artists = {
                'items': [
                    {
                        'id': artist['id'],
                        'name': artist['name'],
                        'genres': artist['genres'][:3],  # 代表的なジャンルのみ
                        'images': artist['images'][:1] if 'images' in artist and artist['images'] else [],
                        'popularity': artist.get('popularity', 0)
                    } for artist in top_artists_raw['items']
                ]
            }
            
            top_tracks = {
                'items': [
                    {
                        'id': track['id'],
                        'name': track['name'],
                        'artists': [{'id': artist['id'], 'name': artist['name']} for artist in track['artists']],
                        'album': {
                            'id': track['album']['id'],
                            'name': track['album']['name'],
                            'images': track['album']['images'][:1] if 'images' in track['album'] else []
                        }
                    } for track in top_tracks_raw['items']
                ]
            }
            
            return {
                'recent_tracks': recent_tracks,
                'top_artists': top_artists,
                'top_tracks': top_tracks
            }
        except Exception as e:
            print(f"Spotify API error: {str(e)}")
            return None
    
    def generate_llm_prompt(self, context=None):
        """LLM用のプロンプトを生成"""
        spotify_data = self.get_spotify_user_data()
        
        # 基本プロンプトテンプレート
        prompt = """あなたは音楽の専門家として、以下の情報からユーザーに合った楽曲を推薦してください。
推薦する楽曲は5曲とし、それぞれの楽曲について以下の情報を含めてください：
- 曲名
- アーティスト名
- 収録アルバム名
- この曲を推薦する理由（ユーザーの好みに合っている点など）

回答は以下のJSON形式で返してください：
{
  "recommendations": [
    {
      "track_name": "曲名",
      "artist_name": "アーティスト名",
      "album_name": "アルバム名",
      "explanation": "推薦理由の説明"
    },
    ... (残りの曲も同様)
  ]
}

回答は上記のJSON形式のみを含め、余計な説明や装飾は不要です。"""

        # Spotifyデータがある場合は追加
        if spotify_data:
            recent_tracks = []
            for item in spotify_data['recent_tracks']['items'][:10]:  # 最新10曲のみ
                track = item['track']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                recent_tracks.append(f"- {track['name']} by {artists}")
                
            top_artists = []
            for artist in spotify_data['top_artists']['items']:
                top_artists.append(f"- {artist['name']} ({', '.join(artist['genres'][:3])})")
                
            top_tracks = []
            for track in spotify_data['top_tracks']['items']:
                artists = ", ".join([artist['name'] for artist in track['artists']])
                top_tracks.append(f"- {track['name']} by {artists}")
                
            prompt += f"""
            
## ユーザーの音楽履歴
### 最近再生した曲（最新10曲）：
{chr(10).join(recent_tracks)}

### お気に入りアーティスト：
{chr(10).join(top_artists)}

### よく聴く曲：
{chr(10).join(top_tracks)}"""

        # コンテキスト情報（気分、状況など）があれば追加
        if context:
            prompt += f"""

## ユーザーの現在の状況/気分：
{context}"""
            
        return prompt
        
    def call_deepseek_api(self, prompt):
        """DeepSeek LLM APIを呼び出し"""
        api_key = settings.DEEPSEEK_API_KEY
        api_url = settings.DEEPSEEK_API_URL
        model = settings.DEEPSEEK_MODEL
        
        if not api_key or not api_url:
            raise ValueError("DeepSeek API設定が不正です")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "あなたは音楽の専門家として、ユーザーの好みに合った音楽を推薦します。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # タイムアウト設定を追加（30秒）
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    def call_openai_api(self, prompt):
        """OpenAI APIを呼び出し"""
        api_key = settings.OPENAI_API_KEY
        api_url = settings.OPENAI_API_URL
        model = settings.OPENAI_MODEL
        
        if not api_key or not api_url:
            raise ValueError("OpenAI API設定が不正です")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "あなたは音楽の専門家として、ユーザーの好みに合った音楽を推薦します。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # タイムアウト設定を追加（30秒）
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
        
    def call_gemini_api(self, prompt):
        """Gemini APIを呼び出し"""
        api_key = settings.GEMINI_API_KEY
        model = settings.GEMINI_MODEL
        
        if not api_key:
            raise ValueError("Gemini API設定が不正です")
            
        # API設定を初期化
        genai.configure(api_key=api_key)
        
        # モデル設定
        model = genai.GenerativeModel(model)
        
        try:
            # システムメッセージとユーザーメッセージを設定
            chat = model.start_chat(history=[])
            system_message = "あなたは音楽の専門家として、ユーザーの好みに合った音楽を推薦します。"
            messages = [
                {"role": "system", "parts": [system_message]},
                {"role": "user", "parts": [prompt]}
            ]
            
            # 会話形式でプロンプトを送信
            response = chat.send_message(f"{system_message}\n\n{prompt}")
            
            # レスポンス形式をOpenAI/Deepseek形式に合わせる
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.text,
                            "role": "assistant"
                        }
                    }
                ]
            }
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            raise
        
    def call_llm_api(self, prompt):
        """LLM APIを呼び出し、推薦結果を取得"""
        # LLMプロバイダーの優先順位に基づいて試行
        errors = []
        
        for provider in settings.LLM_PROVIDERS:
            try:
                if provider == 'deepseek':
                    return self.call_deepseek_api(prompt)
                elif provider == 'openai':
                    return self.call_openai_api(prompt)
                elif provider == 'gemini':
                    return self.call_gemini_api(prompt)
            except Exception as e:
                error_msg = f"{provider} API呼び出しエラー: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue
        
        # すべてのプロバイダーが失敗した場合
        raise Exception(f"すべてのLLMプロバイダーでエラーが発生しました: {', '.join(errors)}")
            
    def parse_llm_response(self, llm_response):
        """LLMレスポンスをパース"""
        try:
            content = llm_response['choices'][0]['message']['content']
            
            # JSONを抽出（余分なテキストがあるかもしれないため）
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                data = json.loads(json_content)
                return data
            else:
                raise ValueError("JSONデータが見つかりませんでした")
                
        except Exception as e:
            print(f"LLM response parsing error: {str(e)}")
            print(f"Response content: {llm_response}")
            raise
            
    def enrich_track_data(self, track_data):
        """Spotify APIを使用して楽曲データを豊かにする"""
        if not self.spotify_client:
            return track_data
            
        try:
            enriched_tracks = []
            
            for i, track in enumerate(track_data):
                # 曲名とアーティストで検索
                query = f"track:{track['track_name']} artist:{track['artist_name']}"
                results = self.spotify_client.search(q=query, type='track', limit=1)
                
                if results['tracks']['items']:
                    spotify_track = results['tracks']['items'][0]
                    
                    # SpotifyデータでTrack情報を充実
                    track['spotify_id'] = spotify_track['id']
                    track['preview_url'] = spotify_track['preview_url']
                    
                    # アルバム画像
                    if spotify_track['album']['images']:
                        track['image_url'] = spotify_track['album']['images'][0]['url']
                        
                    # アルバム名が無い場合は追加
                    if not track.get('album_name'):
                        track['album_name'] = spotify_track['album']['name']
                        
                    # 位置情報を追加
                    track['position'] = i
                    
                enriched_tracks.append(track)
                
            return enriched_tracks
        except Exception as e:
            print(f"Spotify enrichment error: {str(e)}")
            return track_data  # エラー時は元のデータを返す
    
    def get_recommendations(self, context=None):
        """ユーザーに合った音楽推薦を生成"""
        # プロンプト生成
        prompt = self.generate_llm_prompt(context)
        
        # LLM API呼び出し
        llm_response = self.call_llm_api(prompt)
        
        # レスポンスパース
        parsed_data = self.parse_llm_response(llm_response)

        if 'recommendations' not in parsed_data:
            raise ValueError("推薦データが含まれていません")
        
        # 楽曲データを充実
        enriched_tracks = self.enrich_track_data(parsed_data['recommendations'])
        
        return {
            'prompt': prompt,
            'llm_response': llm_response,
            'tracks': enriched_tracks,
            'context': context
        }