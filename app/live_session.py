"""Gemini Live API を使った WebSocket ベースのリアルタイムセッション."""

import asyncio
import base64
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from agents.orchestrator import Orchestrator

router = APIRouter()

LIVE_MODEL = "gemini-live-2.5-flash-native-audio"

LIVE_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    output_audio_transcription=types.AudioTranscriptionConfig(),
    input_audio_transcription=types.AudioTranscriptionConfig(),
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
                            # 音声データを転送
                            if response.data:
                                await ws.send_bytes(response.data)
                            # model_turn 内のテキスト（TEXT モダリティ時）
                            if response.text:
                                await ws.send_json({"type": "text", "data": response.text})
                            # 音声トランスクリプション（AUDIO モダリティ時）
                            sc = response.server_content
                            if sc and sc.output_transcription and sc.output_transcription.text:
                                await ws.send_json({"type": "text", "data": sc.output_transcription.text})
                            # ユーザー音声入力トランスクリプション
                            if sc and sc.input_transcription and sc.input_transcription.text:
                                await ws.send_json({"type": "user_transcript", "data": sc.input_transcription.text})
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
                        query = payload["query"]
                        image_bytes = None
                        if payload.get("image"):
                            image_bytes = base64.b64decode(payload["image"])

                        # Step1: アナウンスをawaitで送信（create_taskではなく）
                        start_msg = (
                            "Starting deep analysis across all four markets — "
                            "Japan, US/UK, France, and Germany. "
                            "This will take about 20 seconds."
                        )
                        await ws.send_json({"type": "text", "data": f"[Deep Analysis] {start_msg}"})
                        await session.send_client_content(
                            turns=[types.Content(role="user", parts=[types.Part(text=start_msg)])],
                            turn_complete=True,
                        )

                        # Step2: Orchestrator実行
                        try:
                            result = await asyncio.wait_for(
                                _orchestrator.analyze(query, image_bytes),
                                timeout=60.0
                            )
                        except asyncio.TimeoutError:
                            await ws.send_json({"type": "analysis", "data": "Analysis timed out."})
                            continue
                        except Exception as e:
                            await ws.send_json({"type": "analysis", "data": f"Analysis failed: {str(e)}"})
                            continue

                        # Step3: スコア表示
                        await ws.send_json({"type": "analysis", "data": result})

                        # Step4: サマリー音声
                        summary_prompt = (
                            f"The deep analysis is complete. Here are the results:\n\n{result[:800]}\n\n"
                            "Please summarize the key cultural risks across the four markets "
                            "in a concise, conversational way — as if briefing the creative team in the room."
                        )
                        await session.send_client_content(
                            turns=[types.Content(role="user", parts=[types.Part(text=summary_prompt)])],
                            turn_complete=True,
                        )
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
                    audio_bytes = msg["bytes"]
                    await session.send_realtime_input(
                        media=types.Blob(data=audio_bytes, mime_type="audio/pcm")
                    )

            recv_task.cancel()

    except WebSocketDisconnect:
        pass
