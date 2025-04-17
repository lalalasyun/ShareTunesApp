import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// 開発環境では明示的にベースURLを設定
// Docker環境ではサービス名を使用
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api';

// デバッグ情報を出力
console.log('API_URL設定:', API_URL);
console.log('環境:', process.env.NODE_ENV);

// Axiosインスタンスの作成
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // タイムアウトを設定（ミリ秒）- LLM呼び出しのため長めに設定
  timeout: 60000, // 60秒に延長
  // CORSリクエストの設定を修正 - withCredentialsをfalseに変更
  withCredentials: false,
});

// 推薦生成用の長いタイムアウト設定を持つAxiosインスタンス
const longTimeoutClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // 推薦生成用に特に長めのタイムアウトを設定
  timeout: 120000, // 120秒（2分）
  withCredentials: false,
});

// _retryプロパティの型拡張を定義
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

// 共通のインターセプターを設定するヘルパー関数
const setupInterceptors = (client: AxiosInstance): void => {
  // リクエストインターセプタ
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );

  // レスポンスインターセプタ
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig;
      
      // error.responseが存在し、ステータスが401の場合のみトークン更新処理を行う
      if (error.response && error.response.status === 401 && originalRequest && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          const refreshToken = localStorage.getItem('refreshToken');
          const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          });
          
          if (response.data.access) {
            localStorage.setItem('accessToken', response.data.access);
            client.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
            return client(originalRequest);
          }
        } catch (err) {
          // リフレッシュトークンも期限切れの場合はログアウト処理
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/';
        }
      }
      
      // エラーの詳細をコンソールに出力（デバッグ用）
      console.error('API呼び出しエラー:', {
        url: originalRequest?.url,
        method: originalRequest?.method,
        errorMessage: error.message,
        errorResponse: error.response || 'レスポンスなし'
      });
      
      return Promise.reject(error);
    }
  );
};

// 両方のクライアントにインターセプターを設定
setupInterceptors(apiClient);
setupInterceptors(longTimeoutClient);

// 認証関連
export const authService = {
  getSpotifyAuthUrl: async () => {
    try {
      console.log('Spotify認証URLを取得しています...');
      // デバッグ情報を追加
      console.log('リクエストURL:', `${API_URL}/auth/spotify/login/`);
      
      // ベースURLが既にAPIサーバーのアドレスを含むため、パスの冒頭に/を付けない
      const response = await apiClient.get('auth/spotify/login/');
      console.log('Spotify認証URLの取得に成功しました:', response.data);
      return response.data;
    } catch (error) {
      console.error('Spotify認証URLの取得に失敗しました:', error);
      // エラー詳細情報を追加
      if (axios.isAxiosError(error)) {
        console.error('APIエラー詳細:', {
          status: error.response?.status,
          data: error.response?.data,
          config: {
            url: error.config?.url,
            method: error.config?.method,
            baseURL: error.config?.baseURL
          }
        });
      }
      throw error; // エラーを再スローして呼び出し元でも処理できるようにする
    }
  },
  
  getUserProfile: async () => {
    const response = await apiClient.get('auth/profile/');
    return response.data;
  },
  
  refreshSpotifyToken: async () => {
    const response = await apiClient.get('auth/spotify/refresh-token/');
    return response.data;
  }
};

// 推薦関連
export const recommendationService = {
  getRecommendations: async () => {
    try {
      console.log('推薦一覧を取得中...');
      const response = await apiClient.get('/recommendations/');
      console.log('推薦一覧取得成功:', response.data);
      return response.data;
    } catch (error) {
      console.error('推薦一覧取得エラー:', error);
      if (axios.isAxiosError(error)) {
        console.error('APIエラー詳細:', {
          status: error.response?.status,
          data: error.response?.data,
          config: {
            url: error.config?.url,
            method: error.config?.method,
            baseURL: error.config?.baseURL
          }
        });
      }
      throw error;
    }
  },
  
  getRecommendationById: async (id: string) => {
    try {
      const response = await apiClient.get(`/recommendations/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`ID ${id} の推薦取得エラー:`, error);
      throw error;
    }
  },
  
  generateRecommendation: async (context?: string) => {
    try {
      console.log('推薦生成を開始します...', { context });
      // 明示的にリクエストをログ
      console.log('リクエストURL:', `${API_URL}/recommendations/generate/`);
      console.log('リクエストボディ:', { context });
      console.log('認証トークン:', localStorage.getItem('accessToken') ? '設定済み' : 'なし');
      
      // 長いタイムアウトのクライアントを使用
      const response = await longTimeoutClient.post('/recommendations/generate/', { context });
      console.log('推薦生成成功:', response.data);
      return response.data;
    } catch (error) {
      console.error('推薦生成エラー:', error);
      if (axios.isAxiosError(error)) {
        console.error('APIエラー詳細:', {
          status: error.response?.status,
          data: error.response?.data,
          config: {
            url: error.config?.url,
            method: error.config?.method,
            baseURL: error.config?.baseURL
          }
        });
      }
      
      // より具体的なエラーメッセージでエラーを再スロー
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(`推薦生成に失敗しました: ${error.response.status} ${JSON.stringify(error.response.data)}`);
      } else {
        throw new Error('推薦生成に失敗しました: ' + (error instanceof Error ? error.message : '不明なエラー'));
      }
    }
  }
};

// ユーザープロフィール関連の型定義
interface ProfileData {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  bio?: string;
}

// ユーザープロフィール関連
export const userService = {
  getProfile: async () => {
    try {
      const response = await apiClient.get('/users/profile/');
      return response.data;
    } catch (error) {
      console.error('プロフィール取得エラー:', error);
      throw error;
    }
  },
  
  updateProfile: async (profileData: ProfileData) => {
    try {
      const response = await apiClient.put('/users/profile/', profileData);
      return response.data;
    } catch (error) {
      console.error('プロフィール更新エラー:', error);
      throw error;
    }
  },
  
  updateProfilePicture: async (formData: FormData) => {
    try {
      const response = await apiClient.post('/users/profile/picture/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('プロフィール画像更新エラー:', error);
      throw error;
    }
  },
  
  getFavoriteGenres: async () => {
    try {
      const response = await apiClient.get('/users/genres/');
      return response.data;
    } catch (error) {
      console.error('お気に入りジャンル取得エラー:', error);
      throw error;
    }
  },
  
  updateFavoriteGenres: async (genres: string[]) => {
    try {
      const response = await apiClient.post('/users/genres/', { genres });
      return response.data;
    } catch (error) {
      console.error('お気に入りジャンル更新エラー:', error);
      throw error;
    }
  }
};

export default {
  auth: authService,
  recommendations: recommendationService,
  users: userService
};