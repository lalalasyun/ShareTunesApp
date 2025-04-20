'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { authService } from '../services/api';
import axios from 'axios';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testStatus, setTestStatus] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ページ読み込み時に認証状態をチェック
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('accessToken');
      setIsAuthenticated(!!token);
      
      // 認証済みの場合は5秒後にダッシュボードに自動リダイレクト
      if (token) {
        console.log('認証済みユーザーを検出しました。ダッシュボードにリダイレクトします...');
        setTimeout(() => {
          router.push('/dashboard');
        }, 1000);
      }
    };
    
    checkAuth();
  }, [router]);

  // Spotify認証URLを取得する関数
  const handleSpotifyLogin = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Spotifyログイン処理を開始します');
      // 直接fetchの代わりにauthServiceを使用
      const data = await authService.getSpotifyAuthUrl();
      console.log('認証URL取得成功:', data);
      
      if (data.auth_url) {
        console.log('リダイレクト先:', data.auth_url);
        window.location.href = data.auth_url;
      } else {
        console.error('認証URLが見つかりません:', data);
        setError('認証URLの取得に失敗しました');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('ログイン処理中にエラーが発生しました:', error);
      setError('サーバー接続エラー。バックエンドサーバーが起動しているか確認してください');
      setIsLoading(false);
    }
  };

  // サーバー接続テスト関数
  const testServerConnection = async () => {
    setTestStatus('テスト中...');
    try {
      // 1. 新しいヘルスチェックエンドポイントを使用
      try {
        const response = await axios.get('/api/health/');
        setTestStatus(`Djangoサーバーに接続できました！ステータス: ${response.status}, メッセージ: ${response.data.message}`);
        return;
      } catch (error: any) {
        console.log('ヘルスチェックエンドポイントへの接続に失敗:', error);
        if (error.response) {
          console.log('エラーレスポンス:', error.response.status, error.response.data);
        }
      }

      // 2. 直接Djangoサーバーにアクセスしてテスト
      try {
        const response = await axios.get('http://localhost:8000/api/health/', { timeout: 3000 });
        setTestStatus(`Djangoサーバーに直接接続できました！ステータス: ${response.status}, メッセージ: ${response.data.message}`);
        return;
      } catch (error: any) {
        console.log('直接接続にも失敗:', error);
        if (error.response) {
          console.log('エラーレスポンス:', error.response.status, error.response.data);
        }
      }

      setTestStatus('バックエンドサーバーに接続できません。サーバーが起動しているか確認してください。');
    } catch (error: any) {
      setTestStatus(`接続テスト中にエラーが発生しました: ${error instanceof Error ? error.message : '不明なエラー'}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh]">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 text-spotify-black">
          Share<span className="text-spotify-green">Tunes</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-700 mb-10 max-w-2xl mx-auto">
          LLMが、あなたの好みに合わせた音楽をパーソナライズして推薦します。
          あなただけの特別なプレイリストを発見しましょう。
        </p>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6" role="alert">
            <p>{error}</p>
          </div>
        )}

        {testStatus && (
          <div className={`${testStatus.includes('接続できました') ? 'bg-green-100 border-green-400 text-green-700' : 'bg-yellow-100 border-yellow-400 text-yellow-700'} border px-4 py-3 rounded mb-6`} role="alert">
            <p>{testStatus}</p>
          </div>
        )}
        
        {isAuthenticated ? (
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
              <p>既にログインしています。ダッシュボードに移動しています...</p>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-spotify-green hover:bg-green-600 text-white font-bold py-3 px-8 rounded-full shadow-lg transform transition-all duration-300 hover:scale-105"
            >
              <span className="flex items-center">
                <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"></path>
                </svg>
                ダッシュボードを開く
              </span>
            </button>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <button
              onClick={handleSpotifyLogin}
              className={`bg-spotify-green hover:bg-green-600 text-white font-bold py-3 px-8 rounded-full shadow-lg transform transition-all duration-300 hover:scale-105 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  読み込み中...
                </span>
              ) : (
                <span className="flex items-center">
                  <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"></path>
                  </svg>
                  Spotifyでログイン
                </span>
              )}
            </button>
            
            <button
              onClick={testServerConnection}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded-full"
            >
              サーバー接続テスト
            </button>
          </div>
        )}
      </div>
      
      <div className="mt-12 text-center">
        <h2 className="text-xl font-semibold mb-4">特徴</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="font-bold mb-2">LLMによる高度な推薦</h3>
            <p>AIが好みを学習し、あなたにぴったりの楽曲を見つけます</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="font-bold mb-2">Spotify連携</h3>
            <p>再生履歴とお気に入りから、より正確なおすすめを提供</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="font-bold mb-2">パーソナライズされた説明</h3>
            <p>なぜこの曲があなたにおすすめなのか、理由も一緒に提供</p>
          </div>
        </div>
      </div>
    </div>
  );
}