# ShareTunes：LLMを活用した音楽推薦システム

![ShareTunes](https://www.msiism.jp/.assets/introduction-to-llm-for-business_thumbnail.jpeg)

## プロジェクト概要

ShareTunesは、大規模言語モデル（LLM）を活用した次世代の音楽推薦システムです。従来の協調フィルタリングなどの手法に加え、LLMの自然言語理解能力を活用することで、よりパーソナライズされた音楽体験を提供します。

ユーザーのSpotifyデータと状況に基づいて、LLMが最適な楽曲を推薦。「今日は疲れているからリラックスできる曲が聴きたい」といった複雑な要望にも応えられるシステムを目指しています。

## 主な機能

- **Spotify連携**: ユーザーのプレイリスト・再生履歴を活用
- **LLM推薦エンジン**: ユーザーの好み・状況を理解した楽曲推薦
- **パーソナライズされた提案**: 時間帯・気分・天気などのコンテキスト情報を活用
- **フィードバックシステム**: ユーザーの反応を学習し、推薦精度を向上
- **プレイリスト管理**: 推薦された曲を自分のプレイリストに追加可能
- **楽曲詳細・プレビュー**: 推薦された曲の詳細情報と試聴機能

## 技術スタック

### フロントエンド
- **Next.js**: Reactベースのフレームワーク
- **TypeScript**: 型安全な開発
- **TailwindCSS**: 効率的なUIスタイリング

### バックエンド
- **Django REST Framework**: 堅牢なAPIバックエンド
- **PostgreSQL**: 関係データベース
- **JWT認証**: セキュアなユーザー認証

### 外部サービス連携
- **Spotify Web API**: 音楽データ取得・操作
- **LLMサービス**: OpenAI, DeepSeek等
- **OAuth2.0**: セキュアな認証フロー

## システムアーキテクチャ

1. ユーザーがアプリを起動し、Spotifyアカウントでログイン
2. バックエンドはSpotify APIからユーザーデータを取得・保存
3. ユーザーの状況やリクエストに基づきLLMへプロンプトを送信
4. LLMは最適な楽曲を推薦し、その結果をバックエンドが解析
5. ユーザーに楽曲が表示され、フィードバックを収集
6. フィードバックは再度推薦アルゴリズムに反映

## プロジェクト構成

```
ShareTunes/
├── backend/          # Django REST APIバックエンド
│   ├── feedbacks/    # ユーザーフィードバック管理
│   ├── playlists/    # プレイリスト管理
│   ├── recommendations/ # LLM推薦エンジン
│   ├── sharetunes/   # プロジェクト設定
│   ├── tracks/       # 楽曲情報管理
│   └── users/        # ユーザー管理
└── frontend/         # Next.jsフロントエンド
    └── src/          # ソースコード
        ├── app/      # ページコンポーネント
        ├── components/ # UIコンポーネント
        └── services/ # APIサービス
```

## セットアップ方法

### 前提条件
- Python 3.8+
- Node.js 16+
- PostgreSQL
- Spotify開発者アカウント

### バックエンドセットアップ
```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係のインストール
cd backend
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーなどを設定

# データベースのマイグレーション
python manage.py migrate

# 開発サーバーの起動
python manage.py runserver
```

### フロントエンドセットアップ
```bash
# 依存関係のインストール
cd frontend
npm install

# 環境変数の設定
cp .env.example .env.local
# .env.localファイルを編集してAPIキーなどを設定

# 開発サーバーの起動
npm run dev
```

## LLM活用のポイント

- **多様なデータの活用**: 歌詞や楽曲の説明文など、従来の機械学習では扱いにくかった情報も活用
- **柔軟な推薦**: ユーザーの状況や好みに合わせて、よりきめ細かい推薦が可能
- **説明可能性**: LLMが推薦理由を説明することで、ユーザーは推薦結果をより理解しやすく

## 今後の展望

- 他音楽サービス（Apple Music等）への対応拡大
- モバイルアプリ版の開発
- より高度な説明生成機能
- ユーザーコミュニティ機能の実装

## 参考リソース

- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [DeepSeek LLM](https://deepseek.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [Next.js](https://nextjs.org/)

## ライセンス

MIT License

---

© 2025 ShareTunes Project