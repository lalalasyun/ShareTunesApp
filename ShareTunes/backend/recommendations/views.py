import traceback
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets

from .models import Recommendation, RecommendedTrack
from .serializers import RecommendationSerializer, RecommendationDetailSerializer
from .services import RecommendationService

class RecommendationViewSet(viewsets.ModelViewSet):
    """推薦リストのCRUD操作用ViewSet"""
    serializer_class = RecommendationSerializer
    # テスト用に一時的にパーミッションを緩和
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # 認証されていない場合は空のクエリセットを返す
        if not self.request.user.is_authenticated:
            return Recommendation.objects.none()
        return Recommendation.objects.filter(user=self.request.user)
        
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecommendationDetailSerializer
        return RecommendationSerializer

def execute_with_timeout(func, args=None, kwargs=None, timeout=60):
    """指定された関数をタイムアウト付きで実行する"""
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
        
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            # タイムアウト時の処理
            raise TimeoutError(f"処理がタイムアウトしました（{timeout}秒）")

@api_view(['POST'])
@permission_classes([AllowAny])  # テスト用に一時的にパーミッションを緩和
def generate_recommendation(request):
    """LLMを使用して新しい音楽推薦を生成するAPI"""
    start_time = time.time()
    print('==== 推薦生成リクエスト受信 ====')
    print(f'リクエストデータ: {request.data}')
    print(f'認証ヘッダー: {request.headers.get("Authorization", "なし")}')
    
    context = request.data.get('context', None)
    print(f'コンテキスト: {context}')
    
    try:
        # テスト用に認証チェックを追加
        if not request.user.is_authenticated:
            print('未認証ユーザー - デモモードで応答')
            # デモ用の応答を返す（実際のアプリでは認証が必要）
            return Response({
                "message": "デモモード: 実際の推薦を生成するには認証が必要です",
                "demo": True,
                "id": 0,
                "prompt_text": context or "ユーザーの好みに基づいた音楽推薦",
                "context_description": context,
                "created_at": "2025-04-17T00:00:00Z",
                "tracks": [
                    {
                        "id": 0,
                        "track_name": "デモトラック1",
                        "artist_name": "テストアーティスト",
                        "album_name": "テストアルバム",
                        "explanation": "これはデモ応答です。実際の推薦を取得するにはログインしてください。",
                        "spotify_id": "",
                        "image_url": "",
                        "preview_url": "",
                        "position": 0
                    }
                ]
            })
            
        # 認証済みユーザー向けのフル機能
        print(f'認証ユーザー: {request.user.username}')
        
        # 推薦サービス初期化
        try:
            service = RecommendationService(request.user)
            print('RecommendationServiceの初期化成功')
        except Exception as service_init_error:
            print(f'サービス初期化エラー: {str(service_init_error)}')
            traceback.print_exc()
            return Response(
                {"error": f"推薦サービスの初期化に失敗しました: {str(service_init_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 推薦生成（タイムアウト付き実行）
        try:
            # 最大90秒のタイムアウト
            result = execute_with_timeout(
                service.get_recommendations, 
                kwargs={"context": context}, 
                timeout=90
            )
            print(f'推薦生成成功（所要時間: {time.time() - start_time:.2f}秒）')
        except TimeoutError as timeout_err:
            print(f'推薦生成がタイムアウトしました: {str(timeout_err)}')
            return Response(
                {"error": f"推薦生成に時間がかかりすぎています。しばらく経ってからもう一度お試しください。"}, 
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as rec_error:
            print(f'推薦生成エラー: {str(rec_error)}')
            traceback.print_exc()
            return Response(
                {"error": f"推薦生成中にエラーが発生しました: {str(rec_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # データベースに保存
        try:
            recommendation = Recommendation.objects.create(
                user=request.user,
                prompt_text=result['prompt'],
                llm_response=result['llm_response'],
                context_description=result['context']
            )
            
            # 各トラックを保存
            for track_data in result['tracks']:
                RecommendedTrack.objects.create(
                    recommendation=recommendation,
                    spotify_id=track_data.get('spotify_id', ''),
                    name=track_data['track_name'],
                    artist=track_data['artist_name'],
                    album=track_data.get('album_name', ''),
                    image_url=track_data.get('image_url', ''),
                    preview_url=track_data.get('preview_url', ''),
                    explanation=track_data['explanation'],
                    position=track_data.get('position', 0)
                )
            
            # レスポンス形式にシリアライズ
            serializer = RecommendationDetailSerializer(recommendation)
            print(f'全処理完了（所要時間: {time.time() - start_time:.2f}秒）')
            return Response(serializer.data)
        except Exception as db_error:
            print(f'データベース保存エラー: {str(db_error)}')
            traceback.print_exc()
            return Response(
                {"error": f"推薦結果のデータベース保存中にエラーが発生しました: {str(db_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        print(f'全体エラー: {str(e)}')
        traceback.print_exc()
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )