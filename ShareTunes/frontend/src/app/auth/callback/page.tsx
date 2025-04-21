'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

// 実際のコールバック処理を行うコンポーネント
function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const processAuth = async () => {
      try {
        // URLからパラメータを取得
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        const accessToken = searchParams.get('access_token');
        const refreshToken = searchParams.get('refresh_token');
        
        console.log('認証コールバック受信:', { code, error, accessToken, refreshToken });
        
        if (error) {
          setError(`認証エラー: ${error}`);
          setIsLoading(false);
          return;
        }
        
        // バックエンドからのリダイレクトでトークンが直接渡された場合
        if (accessToken && refreshToken) {
          console.log('トークン直接受信');
          // トークンをlocalStorageに保存
          localStorage.setItem('accessToken', accessToken);
          localStorage.setItem('refreshToken', refreshToken);
          
          // ダッシュボードにリダイレクト
          router.push('/dashboard');
          return;
        }
        
        // SpotifyからのコールバックURLにcodeパラメータがある場合
        if (code) {
          console.log('認証コード受信、バックエンドにリダイレクト');
          // リダイレクトしてバックエンドで処理
          // Djangoバックエンドの処理でトークンを取得してから再度コールバックされる
          window.location.href = `http://localhost/api/auth/spotify/callback?code=${code}`;
          return;
        }
        
        setError('認証に必要なパラメータがありません');
        setIsLoading(false);
      } catch (err) {
        console.error('認証処理中のエラー:', err);
        setError('認証処理中にエラーが発生しました');
        setIsLoading(false);
      }
    };
    
    processAuth();
  }, [router, searchParams]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
        <button 
          onClick={() => router.push('/')}
          className="mt-4 bg-gray-800 text-white px-4 py-2 rounded"
        >
          ホームに戻る
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-spotify-green border-solid mb-4"></div>
        <h2 className="text-xl font-semibold">認証処理中...</h2>
        <p className="text-gray-600 mt-2">ログイン後、ダッシュボードにリダイレクトします。</p>
      </div>
    </div>
  );
}

// ローディング状態を表示するコンポーネント
function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-spotify-green border-solid mb-4"></div>
        <h2 className="text-xl font-semibold">読み込み中...</h2>
      </div>
    </div>
  );
}

// メインのコールバックページコンポーネント
export default function AuthCallback() {
  return (
    <Suspense fallback={<Loading />}>
      <AuthCallbackContent />
    </Suspense>
  );
}