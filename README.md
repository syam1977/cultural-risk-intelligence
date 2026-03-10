# Cultural Risk Intelligence

Gemini Live API を活用したリアルタイム文化リスク分析エージェント。

音声対話を通じて、日本・米英・フランス・ドイツの各市場における文化的リスクをリアルタイムで分析・報告します。

## アーキテクチャ

```
User (Voice) ←→ Gemini Live API (native audio)
                        ↓
                  Orchestrator Agent
                   ↙  ↓  ↓  ↘
                JP  USUK  FR  DE   ← Market Agents (gemini-3.1-flash-lite)
                   ↘  ↓  ↓  ↙
              Synthesis (gemini-2.5-flash)
                        ↓
               Voice Response to User
```

## 使用モデル

| 役割 | モデル |
|------|--------|
| Live Session (音声対話) | `gemini-live-2.5-flash-preview-native-audio-09-2025` |
| 市場エージェント | `gemini-3.1-flash-lite-preview` |
| 統合分析 | `gemini-2.5-flash` |

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集して GOOGLE_API_KEY を設定

# 起動
python app/main.py
```

## デプロイ (Cloud Run)

```bash
chmod +x infra/deploy.sh
./infra/deploy.sh
```

## ライセンス

MIT
