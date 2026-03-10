"""Gemini Live API を使った WebSocket ベースのリアルタイムセッション."""

import asyncio
import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from agents.orchestrator import Orchestrator

router = APIRouter()

LIVE_MODEL = "gemini-live-2.5-flash-preview-native-audio-09-2025"

LIVE_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO", "TEXT"],
    system_instruction=types.Content(
        parts=[
            types.Part(
                text=(
                    "あなたは文化リスク分析の専門AIアシスタントです。"
                    "ユーザーの質問に対して、日本・米英・フランス・ドイツの各市場における"
                    "文化的リスクをリアルタイムで分析し、音声で報告します。"
                    "回答は簡潔かつ実用的にしてください。"
                )
            )
        ]
    ),
)


def _get_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )


@router.websocket("/ws/live")
async def live_session(ws: WebSocket):
    """WebSocket 経由で Gemini Live セッションを中継する."""
    await ws.accept()
    client = _get_client()
    orchestrator = Orchestrator(client)

    try:
        async with client.aio.live.connect(
            model=LIVE_MODEL, config=LIVE_CONFIG
        ) as session:

            async def _recv_from_gemini():
                """Gemini からのレスポンスを WebSocket に転送."""
                async for response in session.receive():
                    if response.text:
                        await ws.send_json({"type": "text", "data": response.text})
                    if response.data:
                        await ws.send_bytes(response.data)

            recv_task = asyncio.create_task(_recv_from_gemini())

            while True:
                msg = await ws.receive()

                if msg.get("text"):
                    payload = json.loads(msg["text"])

                    if payload.get("type") == "analyze":
                        # 詳細分析: Orchestrator 経由で全市場並列分析
                        query = payload["query"]
                        result = await orchestrator.analyze(query)
                        await ws.send_json({"type": "analysis", "data": result})
                    else:
                        # テキストメッセージを Live セッションに送信
                        await session.send(input=payload.get("data", ""), end_of_turn=True)

                elif msg.get("bytes"):
                    # 音声データを Live セッションに送信
                    await session.send(input=msg["bytes"])

            recv_task.cancel()

    except WebSocketDisconnect:
        pass
