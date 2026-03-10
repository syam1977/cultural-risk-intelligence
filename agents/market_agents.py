"""Market Agents - 各市場の文化リスクを分析する専門エージェント."""

import asyncio
from pathlib import Path

import yaml
from google import genai

MARKET_MODEL = "gemini-3.1-flash-lite-preview"
PROMPTS_DIR = Path(__file__).parent / "prompts"

MARKETS = {
    "jp": "日本",
    "usuk": "米英",
    "fr": "フランス",
    "de": "ドイツ",
}


def load_prompt(market_key: str) -> str:
    """YAML からマーケットプロンプトを読み込む."""
    path = PROMPTS_DIR / f"{market_key}.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["system_prompt"]


class MarketAgentRunner:
    """全市場エージェントを並列実行する."""

    def __init__(self, client: genai.Client):
        self.client = client

    async def _run_single(self, market_key: str, query: str) -> tuple[str, str]:
        """単一市場の分析を実行."""
        system_prompt = load_prompt(market_key)
        label = MARKETS[market_key]

        response = await self.client.aio.models.generate_content(
            model=MARKET_MODEL,
            contents=query,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return label, response.text

    async def run_all(self, query: str) -> dict[str, str]:
        """全市場を並列分析."""
        tasks = [self._run_single(key, query) for key in MARKETS]
        results = await asyncio.gather(*tasks)
        return dict(results)
