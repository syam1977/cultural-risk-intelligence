# Cultural Risk Intelligence

> **Gemini Live Agent Challenge (DevPost) 2026**
> Built in 6 days · Deployed on Cloud Run · Powered by Gemini Live API

---

## Project Overview / プロジェクト概要

A real-time cultural risk analysis agent for A&R teams evaluating visual content across global markets.
Through live voice conversation, it acts as an always-present cultural advisor — analyzing costumes, symbols, and design elements across Japan, US, France, and Germany simultaneously.

A&Rチームがビジュアルコンテンツ（コスチューム・シンボル・デザイン）をグローバル市場向けに評価するためのリアルタイム文化リスク分析エージェント。
音声会話を通じて、日本・米国・フランス・ドイツ市場における文化的リスクを同時にリアルタイム分析します。

**Production URL / 本番URL:**
`https://cultural-risk-intelligence-121466101834.us-central1.run.app`

---

## Key Features / 主な機能

- **Real-time voice conversation** via Gemini Live API (native audio, interruptible)
- **Live playback interruption** — speaking mid-response stops the advisor and redirects instantly
- **Image attachment** — share a costume or visual for contextual analysis
- **Deep Analyze** — dispatches 4 market agents in parallel, returns unified risk report
- **World map visualization** — market pins highlight as the conversation shifts focus
- **Risk score dashboard** — per-market risk gauges (JP / US / FR / DE)
- **Extensible market agents** — adding a new market requires only a new YAML prompt file

---

- Gemini Live API によるリアルタイム音声会話（ネイティブオーディオ・割り込み対応）
- 応答中に話しかけると即座に応答を停止して切り替え
- 画像添付によるビジュアルコンテキスト分析
- Deep Analyze：4市場エージェントを並列実行し統合レポートを生成
- 世界地図ビジュアライゼーション：会話の焦点に合わせてマーケットピンが点灯
- 市場別リスクスコアゲージ表示
- YAMLプロンプト1ファイルで新市場を追加可能

---

## Tech Stack / 技術スタック

| Component | Technology |
|-----------|------------|
| Live Session (voice) | `gemini-live-2.5-flash-native-audio` (us-central1) |
| Market Agents | `gemini-2.5-flash` (global) |
| Synthesis | `gemini-2.5-flash` (global) |
| Backend | Python, FastAPI, WebSocket, uvicorn (`--loop asyncio`) |
| Frontend | Vanilla HTML/JS, Web Audio API (24kHz PCM) |
| Deployment | Google Cloud Run (us-central1) |
| Auth | Vertex AI + Service Account (`roles/aiplatform.user`) |

---

## Architecture / アーキテクチャ

```
User Browser (Voice / Text / Image)
        ↕ WebSocket
FastAPI Server (Cloud Run / us-central1)
        ↕
Gemini Live API  ──────────────────────────────────
gemini-live-2.5-flash-native-audio                 │
        ↓ [Deep Analyze trigger]                   │
Orchestrator (parallel)                            │
  ├── JP Agent  → gemini-2.5-flash (global)        │
  ├── US Agent  → gemini-2.5-flash (global)        │
  ├── FR Agent  → gemini-2.5-flash (global)        │
  └── DE Agent  → gemini-2.5-flash (global)        │
        ↓ Synthesis                                │
gemini-2.5-flash (global) ─────────────────────── │
        ↓
Unified Risk Report → WebSocket → Browser
```

---

## Market Coverage / 対象市場

| Market | Rationale |
|--------|-----------|
| **JP** | Home market — cultural context baseline for Japanese artists |
| **US** | Primary target — largest English-speaking market |
| **FR** | Highest J-culture affinity in Europe (Paris Japan Expo) |
| **DE** | Largest music market in continental Europe |

> Market agents are prompt-driven and modular. Adding a new market requires only a new YAML file under `agents/prompts/`.
> 市場エージェントはYAMLプロンプト駆動。`agents/prompts/` に新ファイルを追加するだけで拡張可能。

---

## Setup / セットアップ

### Prerequisites / 前提条件

- Python 3.11+
- Google Cloud project with Vertex AI enabled
- `gcloud` CLI authenticated

### Local Development / ローカル開発

```bash
# Install dependencies
pip install -r requirements.txt

# Check ADC and start server (recommended)
./dev-start.sh

# Or start directly
./start.sh
```

> **Important:** Always use `./dev-start.sh` for local development.
> It checks Application Default Credentials (ADC) before starting.
> ローカル開発では必ず `./dev-start.sh` を使うこと。ADC の確認を自動実行します。

Access: `http://localhost:8080`

### Deploy to Cloud Run / Cloud Run へのデプロイ

```bash
# Run from Windows Command Prompt (not WSL — gcloud builds submit hangs in WSL)
# WSLではなくWindowsコマンドプロンプトから実行すること

cd \\wsl$\Ubuntu\home\<user>\cultural-risk-intelligence
bash infra/deploy.sh
```

---

## Environment Variables / 環境変数

Defined in `start.sh` (no `.env` file required):

```bash
GOOGLE_CLOUD_PROJECT=avex-corp-elearning
GOOGLE_CLOUD_LOCATION=global           # Orchestrator / Market Agents
GOOGLE_CLOUD_LIVE_LOCATION=us-central1 # Live API
```

---

## Key Technical Decisions / 主要な技術的決定

| Decision | Detail |
|----------|--------|
| `--loop asyncio` | Required for uvicorn — uvloop conflicts with websockets library |
| `api_version='v1beta1'` | Required for Live API — omitting causes WebSocket timeout |
| Live API location | `us-central1` only — `global` is not supported |
| `output_audio_transcription` | Enables text transcription of voice responses for UI market detection |
| `Part(text=...)` | `Part.from_text()` is deprecated in current SDK |

---

## Day-by-Day Progress / 開発進捗

| Day | Summary | 概要 |
|-----|---------|------|
| 1 | Environment setup, verified all model connections (Live API, Market Agents, Synthesis) | 環境構築・全モデル接続確認 |
| 2 | Voice response, image input, continuous multi-turn conversation, AudioContext 24kHz playback | 音声応答・画像入力・連続会話・音声再生 |
| 3 | Microphone input, VAD (RMS-based), playback interruption on user speech | マイク入力・VAD・再生割り込み |
| 4 | Deep Analyze E2E, image support in analyze, `Part` API fix | Deep Analyze E2E・画像対応・Part APIバグ修正 |
| 5 | Cloud Run deployment, service account auth, Dockerfile fix | Cloud Runデプロイ・サービスアカウント認証 |
| 6 | UI redesign (world map, market indicators, risk score panel), transcription support, analyze session fix | UI全面刷新・世界地図・市場インジケーター・スコアパネル |

---

## Project Structure / プロジェクト構成

```
cultural-risk-intelligence/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── live_session.py      # WebSocket / Gemini Live API relay
│   └── static/
│       └── index.html       # Frontend (Vanilla JS)
├── agents/
│   ├── orchestrator.py      # Parallel analysis coordinator
│   ├── market_agents.py     # Market agents (JP / US / FR / DE)
│   └── prompts/             # Per-market YAML prompts
├── infra/
│   └── deploy.sh            # Cloud Run deploy script
├── start.sh                 # Production / Cloud Run launcher
├── dev-start.sh             # Local dev launcher (with ADC check)
├── Dockerfile
└── requirements.txt
```

---

## License / ライセンス

MIT
