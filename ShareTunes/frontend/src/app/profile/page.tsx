'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { userService, authService } from '@/services/api';

// ユーザー情報の型定義
interface UserProfile {
  username: string;
  email: string;
  profilePicture: string;
  bio: string;
  display_name: string; // 表示名を追加
  favoriteGenres: string[];
  preferences: {
    theme?: string;
    notification_settings?: {
      email_notifications?: boolean;
      push_notifications?: boolean;
    }
  };
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile>({
    username: '',
    email: '',
    profilePicture: '/default-avatar.png',
    bio: '',
    display_name: '', // 表示名の初期値
    favoriteGenres: [],
    preferences: {
      theme: 'light',
      notification_settings: {
        email_notifications: true,
        push_notifications: true
      }
    }
  });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    // ユーザー認証状態の確認
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          router.push('/');
          return;
        }

        try {
          // userServiceを使用してユーザープロフィール情報を取得
          const userProfileData = await userService.getProfile();
          
          // APIレスポンスの形式に合わせてマッピング
          const profile = userProfileData.user || {};
          
          // プロフィール画像のURLを適切に処理
          let profileImageUrl = '/default-avatar.png';
          if (userProfileData.profile_image) {
            // 完全なURLかどうかをチェック
            if (userProfileData.profile_image.startsWith('http')) {
              profileImageUrl = userProfileData.profile_image;
            } else {
              // 相対パスの場合はそのまま使用
              profileImageUrl = userProfileData.profile_image;
            }
          }
          
          setUser({
            username: profile.username || '',
            email: profile.email || '',
            profilePicture: profileImageUrl,
            bio: userProfileData.bio || '',
            display_name: userProfileData.display_name || '',
            favoriteGenres: userProfileData.favorite_genres || [],
            preferences: userProfileData.preferences || {
              theme: 'light',
              notification_settings: {
                email_notifications: true,
                push_notifications: true
              }
            }
          });
          
          console.log('プロフィールデータ取得成功:', userProfileData);
        } catch (apiError) {
          console.error('プロフィール情報の取得に失敗しました', apiError);
          setError('プロフィール情報の取得に失敗しました。');
          
          // 認証エラーの場合はログアウト処理
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          router.push('/');
        }
      } catch (err) {
        console.error('プロフィールページエラー:', err);
        setError('プロフィール情報の取得中にエラーが発生しました。');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setUser((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // APIを使ってプロフィールを更新
      await userService.updateProfile({
        username: user.username,
        email: user.email,
        bio: user.bio,
        display_name: user.display_name, // 表示名を更新
        preferences: user.preferences // プリファレンスを更新
      });
      
      setIsEditing(false);
      setLoading(false);
      
      // 成功メッセージの表示
      alert('プロフィールが正常に更新されました');
    } catch (err) {
      console.error('プロフィール更新エラー:', err);
      setError('プロフィールの更新中にエラーが発生しました。');
      setLoading(false);
    }
  };

  const handleProfilePictureChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      try {
        setLoading(true);
        const file = e.target.files[0];
        
        // FormDataオブジェクトを作成
        const formData = new FormData();
        formData.append('image', file); // フィールド名をバックエンドの期待する'image'に変更
        
        // APIを使って画像をアップロード
        const response = await userService.updateProfilePicture(formData);
        
        // アップロードに成功したら状態を更新
        setUser((prev) => ({
          ...prev,
          profilePicture: response.profile_image || prev.profilePicture,
        }));
        
        setLoading(false);
      } catch (err) {
        console.error('プロフィール画像のアップロードに失敗しました:', err);
        setError('画像のアップロードに失敗しました。');
        setLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      <div className="bg-white shadow-lg rounded-lg p-6 max-w-2xl mx-auto">
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="relative w-32 h-32 rounded-full overflow-hidden">
            {user.profilePicture && user.profilePicture !== '/default-avatar.png' ? (
              // next/image の代わりに標準のimg要素を使用してサーバーエラーを回避
              <img
                src={user.profilePicture}
                alt={`${user.username}のプロフィール画像`}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-32 h-32 rounded-full bg-spotify-green flex items-center justify-center text-white text-5xl">
                {user.username.charAt(0).toUpperCase() || 'U'}
              </div>
            )}
            {isEditing && (
              <label className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-center text-xs py-1 cursor-pointer">
                変更
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleProfilePictureChange}
                />
              </label>
            )}
          </div>
          
          <div className="flex-1">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-2xl font-bold">{isEditing ? 'プロフィール編集' : 'プロフィール'}</h1>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                >
                  編集
                </button>
              )}
            </div>

            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">ユーザー名</label>
                  <input
                    type="text"
                    name="username"
                    value={user.username}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">メールアドレス</label>
                  <input
                    type="email"
                    name="email"
                    value={user.email}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">自己紹介</label>
                  <textarea
                    name="bio"
                    value={user.bio}
                    onChange={handleInputChange}
                    rows={3}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">表示名</label>
                  <input
                    type="text"
                    name="display_name"
                    value={user.display_name}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded"
                  >
                    キャンセル
                  </button>
                  <button
                    onClick={handleSave}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                  >
                    保存
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h2 className="text-lg font-semibold">ユーザー名</h2>
                  <p>{user.username}</p>
                </div>
                <div>
                  <h2 className="text-lg font-semibold">メールアドレス</h2>
                  <p>{user.email}</p>
                </div>
                <div>
                  <h2 className="text-lg font-semibold">自己紹介</h2>
                  <p>{user.bio}</p>
                </div>
                <div>
                  <h2 className="text-lg font-semibold">表示名</h2>
                  <p>{user.display_name}</p>
                </div>
                <div>
                  <h2 className="text-lg font-semibold">好きなジャンル</h2>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {user.favoriteGenres.map((genre, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white shadow-lg rounded-lg p-6 max-w-2xl mx-auto">
        <h2 className="text-xl font-bold mb-4">アクティビティ</h2>
        <div className="space-y-4">
          <div className="border-b pb-4">
            <h3 className="font-medium">最近のプレイリスト</h3>
            <p className="text-gray-500">まだプレイリストがありません</p>
          </div>
          <div>
            <h3 className="font-medium">お気に入りの曲</h3>
            <p className="text-gray-500">まだお気に入りの曲がありません</p>
          </div>
        </div>
      </div>
    </div>
  );
}