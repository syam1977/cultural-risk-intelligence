"""Gemini Live API を使った WebSocket ベースのリアルタイムセッション."""

import asyncio
import base64
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from agents.orchestrator import Orchestrator

router = APIRouter()

LIVE_MODEL = "gemini-live-2.5-flash-preview-native-audio-09-2025"

LIVE_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=types.Content(
        parts=[
            types.Part(
                text=(
                    "You are a cultural risk intelligence assistant. "
                    "You help A&R teams evaluate visual content — costumes, "
                    "symbols, and design elements — across global markets. "
                    "Respond conversationally and concisely. "
                    "When asked about a specific market, share your perspective "
                    "as an interpretive hypothesis, not a definitive judgment. "
                    "Always acknowledge that other interpretations exist."
                )
            )
        ]
    ),
)

# Module-level references set by init_clients()
_live_client: genai.Client | None = None
_analysis_client: genai.Client | None = None
_orchestrator: Orchestrator | None = None


def init_clients(live_client: genai.Client, analysis_client: genai.Client) -> None:
    """main.py から呼び出され、2つのクライアントを設定する."""
    global _live_client, _analysis_client, _orchestrator
    _live_client = live_client
    _analysis_client = analysis_client
    _orchestrator = Orchestrator(analysis_client)


@router.websocket("/ws/live")
async def live_session(ws: WebSocket):
    """WebSocket 経由で Gemini Live セッションを中継する."""
    await ws.accept()

    try:
        async with _live_client.aio.live.connect(
            model=LIVE_MODEL, config=LIVE_CONFIG
        ) as session:

            async def _recv_from_gemini():
                """Gemini からのレスポンスを WebSocket に転送."""
                while True:
                    try:
                        async for response in session.receive():
                            if response.text:
                                await ws.send_json({"type": "text", "data": response.text})
                            if response.data:
                                await ws.send_bytes(response.data)
                    except Exception:
                        break

            recv_task = asyncio.create_task(_recv_from_gemini())

            while True:
                try:
                    msg = await ws.receive()
                except Exception:
                    break

                if msg.get("type") == "websocket.disconnect":
                    break

                if msg.get("text"):
                    payload = json.loads(msg["text"])

                    if payload.get("type") == "analyze":
                        # 詳細分析: Orchestrator 経由で全市場並列分析
                        query = payload["query"]
                        result = await _orchestrator.analyze(query)
                        await ws.send_json({"type": "analysis", "data": result})
                    else:
                        # テキスト（+画像）メッセージを Live セッションに送信
                        user_message = payload.get("data", "")
                        parts = []
                        if user_message:
                            parts.append(types.Part(text=user_message))
                        if payload.get("image"):
                            parts.append(
                                types.Part(
                                    inline_data=types.Blob(
                                        data=base64.b64decode(payload["image"]),
                                        mime_type=payload.get("mime_type", "image/jpeg"),
                                    )
                                )
                            )
                        await session.send_client_content(
                            turns=[
                                types.Content(role="user", parts=parts)
                            ],
                            turn_complete=True,
                        )

                elif msg.get("bytes"):
                    # 音声データを Live セッションに送信
                    await session.send_realtime_input(
                        media=types.Blob(data=msg["bytes"], mime_type="audio/pcm")
                    )

            recv_task.cancel()

    except WebSocketDisconnect:
        pass
