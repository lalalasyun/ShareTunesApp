'use client';

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import { authService } from '@/services/api';

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [userProfile, setUserProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // クライアントサイドでのみ実行
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('accessToken');
          if (token) {
            try {
              // APIからユーザープロフィールを実際に取得する
              const profile = await authService.getUserProfile();
              setUserProfile(profile);
              console.log('ユーザープロフィールを取得しました:', profile);
            } catch (profileError) {
              console.error('ユーザープロフィール取得エラー:', profileError);
              // エラーが発生した場合はログアウトする
              localStorage.removeItem('accessToken');
              localStorage.removeItem('refreshToken');
              window.location.href = '/';
            }
          }
        }
      } catch (error) {
        console.error('認証チェックエラー:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  return (
    <>
      {!loading && userProfile && (
        <Header userProfile={userProfile} />
      )}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </>
  );
}