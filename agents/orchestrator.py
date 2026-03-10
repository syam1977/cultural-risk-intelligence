"""Orchestrator Agent - 市場エージェントの統括と統合分析を行う."""

import asyncio

from google import genai

from agents.market_agents import MarketAgentRunner

SYNTHESIS_MODEL = "gemini-2.5-flash"

SYNTHESIS_PROMPT = """\
あなたは文化リスク分析の統合アナリストです。
各市場エージェントから報告されたリスク分析結果を統合し、
グローバル視点での文化リスクレポートを生成してください。

以下の観点で統合してください:
- 市場横断的なリスクパターン
- 市場固有の重大リスク
- 推奨アクション（優先度付き）
- 全体リスクスコア (1-10)
"""


class Orchestrator:
    """複数市場エージェントを並列実行し、結果を統合する."""

    def __init__(self, client: genai.Client):
        self.client = client
        self.market_runner = MarketAgentRunner(client)

    async def analyze(self, query: str) -> str:
        """ユーザーのクエリに対して全市場を並列分析し、統合結果を返す."""
        market_results = await self.market_runner.run_all(query)

        combined = "\n\n".join(
            f"## {market} 市場レポート\n{result}"
            for market, result in market_results.items()
        )

        response = await self.client.aio.models.generate_content(
            model=SYNTHESIS_MODEL,
            contents=f"{SYNTHESIS_PROMPT}\n\n# 各市場レポート\n{combined}\n\n# 元の質問\n{query}",
        )
        return response.text
