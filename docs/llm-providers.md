# ShareTunes LLMプロバイダー設定ガイド

ShareTunesでは、複数のLLMプロバイダー（DeepSeek、OpenAI、Gemini）を切り替えて使用できるようになっています。このドキュメントでは、各プロバイダーの設定方法と切り替え手順について説明します。

## 対応LLMプロバイダー

現在、以下のLLMプロバイダーに対応しています：

1. **DeepSeek** - DeepSeekのモデルを使用
2. **OpenAI** - GPT-3.5/GPT-4を使用
3. **Gemini** - Google AIのGeminiモデルを使用

## 環境変数の設定

バックエンドの`.env`ファイルで各プロバイダーのAPIキーとモデル設定を行います：

```bash
# DeepSeek API設定
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# OpenAI API設定
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_URL=https://api.openai.com/v1/chat/completions
OPENAI_MODEL=gpt-3.5-turbo  # または gpt-4 など

# Gemini API設定
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro  # または gemini-1.0-pro など

# LLMプロバイダーの優先順位設定
LLM_PROVIDERS=deepseek,openai,gemini
```

## プロバイダー優先順位の設定

`LLM_PROVIDERS`環境変数でプロバイダーの優先順位を指定できます。カンマ区切りで記述し、最初に指定したプロバイダーが優先的に使用されます：

```bash
# DeepSeekを優先的に使用し、失敗した場合はOpenAI、さらに失敗した場合はGemini
LLM_PROVIDERS=deepseek,openai,gemini

# Geminiを優先的に使用
LLM_PROVIDERS=gemini,deepseek,openai

# OpenAIのみを使用
LLM_PROVIDERS=openai
```

システムは指定された順序でプロバイダーを試行し、エラーが発生した場合は次のプロバイダーを使用します。すべてのプロバイダーが失敗した場合のみエラーを返します。

## APIキーの取得方法

### DeepSeek APIキー

1. [DeepSeek公式サイト](https://deepseek.com/)にアクセス
2. アカウントを作成し、APIキーを生成

### OpenAI APIキー

1. [OpenAIダッシュボード](https://platform.openai.com/)にアクセス
2. アカウントを作成し、APIキーを生成

### Gemini APIキー

1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. Googleアカウントでログインし、APIキーを生成

## トラブルシューティング

### APIエラーが発生する場合

- APIキーが正しく設定されているか確認
- 使用制限に達していないか確認
- ネットワーク接続が正常か確認

### レスポンス形式が正しくない場合

LLMのレスポンス形式が期待通りでない場合は、プロンプトを調整する必要があります。現在のプロンプトはJSON形式の応答を要求するよう設計されています。

## 開発者向け情報

LLM APIの実装は `recommendations/services.py` で行われています。新しいプロバイダーを追加する場合は、以下の手順で実装します：

1. 設定を `settings.py` に追加（API_KEY、API_URL、MODELなどの変数を定義）
2. 必要に応じてAPIクライアントをrequirements.txtに追加
3. `services.py` に呼び出しメソッド（call_[provider]_api）を追加
4. `call_llm_api` メソッドに新しいプロバイダーのケースを追加

## 後方互換性について

過去の設定との互換性のために、以下の古い環境変数もサポートしています：

```bash
# 古い設定（互換性のために維持）
LLM_API_KEY=your-deepseek-api-key  # 代わりにDEEPSEEK_API_KEYを使用してください
LLM_API_URL=https://api.deepseek.com/v1/chat/completions  # 代わりにDEEPSEEK_API_URLを使用してください
```

将来のバージョンでは、これらの古い環境変数は削除される予定です。

## パフォーマンス比較

各LLMプロバイダーのパフォーマンスは以下の要素によって異なります：

- 応答速度
- 音楽ドメインでの知識の深さ
- コスト効率
- API安定性

実運用では、使用目的や予算に応じて最適なプロバイダーを選択することをお勧めします。