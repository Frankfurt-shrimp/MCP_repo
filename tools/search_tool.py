"""
Tool：搜尋景點與美食資訊
使用套件：duckduckgo-search
負責：楊承軒
（沿用上週 w6-agnet-group-4 實作）
"""

from typing import Dict, Any
import warnings

# 忽略因為套件改名 (`ddgs`) 而產生的 RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

from duckduckgo_search import DDGS


def _perform_search(query: str, max_results: int = 3) -> str:
    """內部共用搜尋邏輯"""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get('title', '')
                body = r.get('body', '')
                results.append(f"- 【{title}】 {body}")

        if results:
            return "\n".join(results)
        return f"（目前找不到關於「{query}」的特定資訊）"
    except Exception as e:
        return f"（搜尋「{query}」時發生錯誤，請稍後再試）"


def search_attractions(city: str) -> str:
    """使用 DuckDuckGo 搜尋 {city} 景點"""
    return _perform_search(f"{city} 必去熱門景點 推薦", max_results=3)


def search_food(city: str) -> str:
    """使用 DuckDuckGo 搜尋 {city} 必吃美食"""
    return _perform_search(f"{city} 必吃美食 在地特色", max_results=3)


def web_search(query: str) -> str:
    """通用搜尋功能"""
    return _perform_search(query, max_results=5)


TOOL = {
    "name": "search_tool",
    "description": "搜尋當地的熱門景點、美食或天氣穿搭建議。",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "想搜尋的關鍵字或想了解的主題"
            }
        },
        "required": ["query"]
    }
}
