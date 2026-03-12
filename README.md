# Cultural Risk Intelligence

## Project Overview / プロジェクト概要

A real-time cultural risk analysis agent powered by the Gemini Live API.
Through voice interaction, it analyzes and reports cultural risks across markets in Japan, US/UK, France, and Germany in real time.

Gemini Live API を活用したリアルタイム文化リスク分析エージェント。
音声対話を通じて、日本・米英・フランス・ドイツの各市場における文化的リスクをリアルタイムで分析・報告します。

## Features / 機能

- **Real-time voice interaction** via Gemini Live API (native audio)
- **Multi-market parallel analysis** across JP, US/UK, FR, DE
- **Cultural risk detection** with market-specific agents
- **Synthesis reporting** combining insights from all markets
- **Image attachment support** for visual context analysis
- **Voice Activity Detection (VAD)** with RMS-based silence filtering
- **Playback interruption** — speaking into the mic stops the current response

- Gemini Live API によるリアルタイム音声対話（ネイティブオーディオ）
- JP・US/UK・FR・DE の多市場並列分析
- 市場別エージェントによる文化リスク検出
- 全市場のインサイトを統合した合成レポート
- 画像添付によるビジュアルコンテキスト分析
- RMS ベースの簡易 VAD による無音フィルタリング
- マイク入力による再生割り込み機能

## Tech Stack / 技術スタック

| Component | Technology |
|-----------|------------|
| Live Session (voice) | `gemini-live-2.5-flash-preview-native-audio-09-2025` |
| Market Agents | `gemini-3.1-flash-lite-preview` |
| Synthesis | `gemini-2.5-flash` |
| Backend | Python, FastAPI, WebSocket |
| Frontend | Vanilla HTML/JS, Web Audio API |
| Deployment | Cloud Run |

## Setup / セットアップ

```bash
# Install dependencies / 依存関係インストール
pip install -r requirements.txt

# Configure environment / 環境変数設定
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
# .env を編集して GOOGLE_API_KEY を設定

# Run / 起動
python app/main.py
```

### Deploy to Cloud Run / Cloud Run へのデプロイ

```bash
chmod +x infra/deploy.sh
./infra/deploy.sh
```

## Usage / 使い方

1. Open the app in your browser (default: `http://localhost:8000`)
2. Click the microphone button to start voice input
3. Speak to ask about cultural risks in specific markets
4. Use the text input to type questions, or attach images for visual analysis
5. Click "Deep Analyze" for a comprehensive multi-market parallel analysis

---

1. ブラウザでアプリを開く（デフォルト: `http://localhost:8000`）
2. マイクボタンをクリックして音声入力を開始
3. 特定市場の文化リスクについて音声で質問
4. テキスト入力で質問を入力、または画像を添付してビジュアル分析
5. 「Deep Analyze」で全市場の並列詳細分析を実行

## Architecture / アーキテクチャ

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

## Day-by-Day Progress / 開発進捗

| Day | Summary | 概要 |
|-----|---------|------|
| 1 | TODO | TODO |
| 2 | TODO | TODO |
| 3 | TODO | TODO |

## License / ライセンス

MIT
