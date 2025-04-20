'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import RecommendationList from '@/components/RecommendationList';
import { recommendationService, authService } from '@/services/api'; // 正しいインポートパス

export default function Dashboard() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [context, setContext] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // 認証確認とユーザープロファイル取得
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('accessToken');
      
      if (!token) {
        console.log('アクセストークンがありません。ログインページにリダイレクトします。');
        router.push('/');
        return;
      }
      
      try {
        // ユーザープロファイル取得を試みて認証の有効性を確認
        try {
          console.log('ユーザープロファイルを取得して認証を確認しています...');
          const profile = await authService.getUserProfile();
          console.log('認証確認成功:', profile);
          setUserProfile(profile);
          
          // 過去の推薦を取得
          try {
            console.log('推薦リストを取得しています...');
            const recommendations = await recommendationService.getRecommendations();
            setRecommendations(Array.isArray(recommendations) ? recommendations : []);
          } catch (error) {
            console.error('推薦リスト取得エラー:', error);
            // 推薦リストの取得に失敗してもログアウトはしない
          }
          
          // ロード完了
          setIsLoading(false);
        } catch (error: any) {
          console.error('プロファイル取得または認証エラー:', error);
          
          // エラーメッセージがある場合は表示する
          if (error.response && error.response.data) {
            setAuthError(error.response.data.detail || '認証エラーが発生しました');
          } else {
            setAuthError('認証エラーが発生しました');
          }
          
          // トークンを削除してホームにリダイレクト
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          
          // 少し遅延を入れてからリダイレクト
          setTimeout(() => {
            router.push('/');
          }, 2000);
        }
      } catch (error) {
        console.error('認証確認中の予期せぬエラー:', error);
        setAuthError('認証処理中にエラーが発生しました');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        
        // 少し遅延を入れてからリダイレクト
        setTimeout(() => {
          router.push('/');
        }, 2000);
      }
    };
    
    checkAuth();
  }, [router]);
  
  // 新しい推薦を生成
  const generateRecommendation = async () => {
    setIsGenerating(true);
    
    try {
      console.log('推薦生成を開始します...');
      // 直接fetchではなくAPIサービスを使用
      const newRecommendation = await recommendationService.generateRecommendation(context);
      console.log('推薦データ:', newRecommendation);
      
      // 推薦リストの先頭に新しい推薦を追加
      setRecommendations([newRecommendation, ...recommendations]);
      
      // コンテキスト入力をクリア
      setContext('');
    } catch (error) {
      console.error('Recommendation error', error);
      // より詳細なエラーメッセージをユーザーに表示
      const errorMessage = error instanceof Error 
        ? error.message 
        : '推薦の生成中にエラーが発生しました';
      alert(`推薦生成エラー: ${errorMessage}`);
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-spotify-green"></div>
      </div>
    );
  }

  if (authError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{authError}</p>
        </div>
        <p className="mt-4 text-gray-600">ホームページにリダイレクトします...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">音楽を推薦してもらう</h2>
          <div className="mb-4">
            <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-1">
              現在の気分や状況を教えてください（オプション）
            </label>
            <textarea
              id="context"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-spotify-green focus:border-spotify-green"
              rows={3}
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="例: 今日は雨の日でゆったりと勉強したい気分です"
              disabled={isGenerating}
            />
          </div>
          <button
            onClick={generateRecommendation}
            disabled={isGenerating}
            className={`bg-spotify-green text-white font-bold py-2 px-6 rounded-full ${
              isGenerating ? 'opacity-70 cursor-not-allowed' : 'hover:bg-green-600'
            }`}
          >
            {isGenerating ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                生成中...
              </span>
            ) : (
              '楽曲推薦を生成'
            )}
          </button>
        </div>
        
        <div>
          <h2 className="text-2xl font-bold mb-4">推薦リスト</h2>
          {recommendations.length > 0 ? (
            <RecommendationList recommendations={recommendations} />
          ) : (
            <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
              まだ推薦がありません。上のフォームから生成してみましょう！
            </div>
          )}
        </div>
      </main>
    </div>
  );
}