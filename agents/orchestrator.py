"""Orchestrator Agent - 市場エージェントの統括と統合分析を行う."""

import asyncio

from google import genai

from agents.market_agents import MarketAgentRunner, MARKETS

SYNTHESIS_MODEL = "gemini-2.5-flash"

# MARKETS の日本語ラベル → フロントエンドが期待するコードへのマッピング
_LABEL_TO_CODE = {
    "日本": "JP",
    "米英": "US",
    "フランス": "FR",
    "ドイツ": "DE",
}

SYNTHESIS_PROMPT = """\
You are a global cultural risk synthesis analyst.
Integrate the risk analysis reports from each market agent and produce
a unified global cultural risk report.

Structure your output as follows:
1. Cross-market risk patterns: risks that appear across multiple markets
2. Market-specific critical risks: high-severity risks unique to individual markets
3. Recommended actions with priority (High / Medium / Low)
4. Per-market risk scores on a single line in EXACTLY this format:
   Risk Score — JP: <score>/100, US: <score>/100, FR: <score>/100, DE: <score>/100
   where <score> is an integer from 0 to 100. Use market codes JP, US, FR, DE only.
5. Overall risk score (1-10)

IMPORTANT: You MUST include the "Risk Score —" line with all four market codes.
Output in English. Keep it concise.
"""


class Orchestrator:
    """複数市場エージェントを並列実行し、結果を統合する."""

    def __init__(self, client: genai.Client):
        self.client = client
        self.market_runner = MarketAgentRunner(client)

    async def analyze(self, query: str, image_bytes: bytes | None = None) -> str:
        """ユーザーのクエリに対して全市場を並列分析し、統合結果を返す."""
        market_results = await self.market_runner.run_all(query, image_bytes)

        combined = "\n\n".join(
            f"## {_LABEL_TO_CODE.get(market, market)} ({market}) 市場レポート\n{result}"
            for market, result in market_results.items()
        )

        response = await self.client.aio.models.generate_content(
            model=SYNTHESIS_MODEL,
            contents=f"{SYNTHESIS_PROMPT}\n\n# 各市場レポート\n{combined}\n\n# 元の質問\n{query}",
        )
        return response.text
