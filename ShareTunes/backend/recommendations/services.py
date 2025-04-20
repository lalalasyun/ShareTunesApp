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
        """
        Spotifyから最近の再生履歴とお気に入りアーティスト情報を取得し、必要なデータのみを抽出
        
        Returns:
            dict: 以下のキーを含む辞書、または取得失敗時はNone
                - recent_tracks: 最近再生した10曲の情報
                - top_artists: お気に入りアーティスト10組の情報
                - top_tracks: よく聴く曲10曲の情報
        """
        if not self.user_profile or not self.user_profile.spotify_access_token:
            return None
            
        if self.user_profile.spotify_token_expires_at and self.user_profile.spotify_token_expires_at < timezone.now():
            # Tokenが期限切れ
            return None
            
        # Spotifyクライアント初期化
        sp = spotipy.Spotify(auth=self.user_profile.spotify_access_token)
        
        try:
            # データ取得
            recent_tracks_raw = sp.current_user_recently_played(limit=20)
            top_artists_raw = sp.current_user_top_artists(limit=10, time_range='medium_term')
            top_tracks_raw = sp.current_user_top_tracks(limit=10, time_range='medium_term')

            # データ抽出・変換
            recent_tracks = self._extract_recent_tracks(recent_tracks_raw)
            top_artists = self._extract_top_artists(top_artists_raw)
            top_tracks = self._extract_top_tracks(top_tracks_raw)
            
            return {
                'recent_tracks': recent_tracks,
                'top_artists': top_artists,
                'top_tracks': top_tracks
            }
        except Exception as e:
            print(f"Spotify API error: {str(e)}")
            return None
    
    def _extract_recent_tracks(self, recent_tracks_raw):
        """
        最近再生した楽曲データから必要なデータのみを抽出
        
        Args:
            recent_tracks_raw (dict): Spotify APIから取得した再生履歴データ
            
        Returns:
            dict: 整形された再生履歴データ
        """
        if not recent_tracks_raw or 'items' not in recent_tracks_raw:
            return {'items': []}
            
        return {
            'items': [
                {
                    'track': {
                        'id': item.get('track', {}).get('id', ''),
                        'name': item.get('track', {}).get('name', ''),
                        'artists': [
                            {
                                'id': artist.get('id', ''),
                                'name': artist.get('name', '')
                            } 
                            for artist in item.get('track', {}).get('artists', [])
                        ],
                        'album': {
                            'id': item.get('track', {}).get('album', {}).get('id', ''),
                            'name': item.get('track', {}).get('album', {}).get('name', ''),
                            'images': (item.get('track', {}).get('album', {}).get('images', [])[:1] 
                                      if item.get('track', {}).get('album', {}).get('images') else [])
                        }
                    },
                    'played_at': item.get('played_at', '')
                } 
                for item in recent_tracks_raw.get('items', [])[:10]  # 最新10曲に制限
            ]
        }
    
    def _extract_top_artists(self, top_artists_raw):
        """
        トップアーティストデータから必要なデータのみを抽出
        
        Args:
            top_artists_raw (dict): Spotify APIから取得したトップアーティストデータ
            
        Returns:
            dict: 整形されたトップアーティストデータ
        """
        if not top_artists_raw or 'items' not in top_artists_raw:
            return {'items': []}
            
        return {
            'items': [
                {
                    'id': artist.get('id', ''),
                    'name': artist.get('name', ''),
                    'genres': artist.get('genres', [])[:3],  # 代表的なジャンルのみ
                    'images': artist.get('images', [])[:1],
                    'popularity': artist.get('popularity', 0)
                } 
                for artist in top_artists_raw.get('items', [])
            ]
        }
    
    def _extract_top_tracks(self, top_tracks_raw):
        """
        トップトラックデータから必要なデータのみを抽出
        
        Args:
            top_tracks_raw (dict): Spotify APIから取得したトップトラックデータ
            
        Returns:
            dict: 整形されたトップトラックデータ
        """
        if not top_tracks_raw or 'items' not in top_tracks_raw:
            return {'items': []}
            
        return {
            'items': [
                {
                    'id': track.get('id', ''),
                    'name': track.get('name', ''),
                    'artists': [
                        {
                            'id': artist.get('id', ''),
                            'name': artist.get('name', '')
                        } 
                        for artist in track.get('artists', [])
                    ],
                    'album': {
                        'id': track.get('album', {}).get('id', ''),
                        'name': track.get('album', {}).get('name', ''),
                        'images': (track.get('album', {}).get('images', [])[:1] 
                                  if track.get('album', {}).get('images') else [])
                    }
                } 
                for track in top_tracks_raw.get('items', [])
            ]
        }
    
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
        """
        LLM APIを呼び出し、推薦結果を取得
        
        設定された優先順位に基づいてLLMプロバイダーに問い合わせを行います。
        ひとつのプロバイダーが失敗した場合、次のプロバイダーを試します。
        
        Args:
            prompt (str): LLMに送信するプロンプト
            
        Returns:
            dict: LLM APIからのレスポンス
            
        Raises:
            Exception: すべてのLLMプロバイダーが失敗した場合
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # LLMプロバイダーの優先順位に基づいて試行
        errors = []
        providers_tried = 0
        
        for provider in settings.LLM_PROVIDERS:
            providers_tried += 1
            try:
                logger.info(f"プロバイダー '{provider}' を使用して推薦を取得しています...")
                if provider == 'deepseek':
                    return self.call_deepseek_api(prompt)
                elif provider == 'openai':
                    return self.call_openai_api(prompt)
                elif provider == 'gemini':
                    return self.call_gemini_api(prompt)
                else:
                    logger.warning(f"未知のプロバイダー: {provider} - スキップします")
                    continue
            except requests.exceptions.RequestException as e:
                # ネットワーク関連のエラー
                error_msg = f"{provider} API接続エラー: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
            except ValueError as e:
                # 設定や構成に関するエラー
                error_msg = f"{provider} API設定エラー: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
            except Exception as e:
                # その他のエラー
                error_msg = f"{provider} API呼び出しエラー: {str(e.__class__.__name__)}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # すべてのプロバイダーが失敗した場合
        if providers_tried == 0:
            raise Exception("有効なLLMプロバイダーがありません。設定を確認してください。")
        else:
            error_details = "\n- ".join(errors)
            error_message = f"すべてのLLMプロバイダー({len(errors)}個)でエラーが発生しました:\n- {error_details}"
            logger.critical(error_message)
            raise Exception(error_message)
            
    def parse_llm_response(self, llm_response):
        """
        LLMレスポンスをパースしてJSON形式に変換
        
        Args:
            llm_response (dict): LLM APIからのレスポンス
            
        Returns:
            dict: パースされたJSONデータ
            
        Raises:
            ValueError: JSONデータが見つからないか、解析できない場合
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # レスポンス検証
            if not llm_response or 'choices' not in llm_response or not llm_response['choices']:
                raise ValueError("有効なLLMレスポンスではありません")
            
            content = llm_response['choices'][0].get('message', {}).get('content', '')
            if not content:
                raise ValueError("レスポンスにコンテンツがありません")
                
            # JSONを抽出（余分なテキストがあるかもしれないため）
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start < 0 or json_end <= json_start:
                # JSON形式でない場合のフォールバック処理
                logger.warning("JSONフォーマットが検出できません。全体をパースしようとします。")
                try:
                    # コンテンツ全体を試してみる
                    data = json.loads(content)
                    return data
                except:
                    # マークダウンコードブロックからJSONを抽出する試み
                    import re
                    json_blocks = re.findall(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
                    if json_blocks:
                        for block in json_blocks:
                            try:
                                data = json.loads(block.strip())
                                return data
                            except:
                                continue
                    raise ValueError("JSONデータが見つかりませんでした")
            
            # JSON部分を抽出してパース
            json_content = content[json_start:json_end]
            data = json.loads(json_content)
            
            # 必須キーの検証
            if 'recommendations' not in data:
                logger.warning("レスポンスに'recommendations'キーがありません")
                # 意図したフォーマットでない場合、推測を試みる
                if isinstance(data, list) and len(data) > 0 and all(isinstance(item, dict) for item in data):
                    logger.info("トップレベルの配列を'recommendations'キーの値として使用します")
                    return {'recommendations': data}
            
            return data
                
        except json.JSONDecodeError as e:
            logger.error(f"JSONパースエラー: {str(e)}")
            logger.debug(f"パース失敗したコンテンツ: {content}")
            raise ValueError(f"JSONデータの解析に失敗しました: {str(e)}")
        except Exception as e:
            logger.error(f"LLMレスポンス処理エラー: {str(e)}")
            logger.debug(f"問題のあるレスポンス: {llm_response}")
            raise ValueError(f"LLMレスポンスの処理でエラーが発生しました: {str(e)}")
            
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
        """
        ユーザーに合った音楽推薦を生成
        
        Args:
            context (str, optional): 推薦の文脈情報（気分、状況など）
            
        Returns:
            dict: 推薦結果を含む辞書
        
        Raises:
            Exception: 推薦生成プロセスでエラーが発生した場合
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # プロンプト生成
            prompt = self.generate_llm_prompt(context)
            logger.info("推薦用プロンプトを生成しました")
            
            # LLM API呼び出し
            logger.info("LLM APIを呼び出します")
            llm_response = self.call_llm_api(prompt)
            
            # レスポンスパース
            logger.info("LLMレスポンスをパースします")
            parsed_data = self.parse_llm_response(llm_response)

            if 'recommendations' not in parsed_data:
                raise ValueError("推薦データが含まれていません")
            
            if not parsed_data['recommendations'] or len(parsed_data['recommendations']) == 0:
                raise ValueError("推薦トラックが0件です")
                
            # 楽曲データを充実
            logger.info(f"{len(parsed_data['recommendations'])}件の推薦トラックデータを充実させます")
            enriched_tracks = self.enrich_track_data(parsed_data['recommendations'])
            
            return {
                'prompt': prompt,
                'llm_response': llm_response,
                'tracks': enriched_tracks,
                'context': context
            }
        except Exception as e:
            logger.error(f"推薦生成エラー: {str(e)}")
            raise