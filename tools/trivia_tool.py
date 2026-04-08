"""
Tool：取得目的地在地冷知識
使用 API：中文維基百科 API
負責：林永富
（沿用上週 w6-agnet-group-4 實作）
"""

import requests


def get_random_trivia(city: str) -> str:
    """
    呼叫中文維基百科 API 取得該城市的簡單介紹，當作在地冷知識返回。
    回傳：回傳一段中文的在地小常識字串
    """
    try:
        url = (
            f"https://zh.wikipedia.org/w/api.php?action=query&prop=extracts"
            f"&exsentences=2&exlimit=1&titles={city}"
            f"&explaintext=1&redirects=1&format=json"
        )
        headers = {"User-Agent": "TravelAgentBot/1.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if page_id == "-1":
                return f"你知道嗎？{city} 是一個充滿無限可能的地方，等待你親自去發掘！"
            extract = page_info.get("extract", "")
            if extract:
                return f"你知道嗎？{extract}"
        return f"你知道嗎？{city} 是一個值得細細品味的美麗城市！"
    except Exception:
        return f"你知道嗎？關於 {city} 的每個角落幾乎都藏著有趣的歷史故事！"


TOOL = {
    "name": "trivia_tool",
    "description": "取得與目的地相關的在地冷知識與背景介紹。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "目的地城市名稱"
            }
        },
        "required": ["city"]
    }
}

if __name__ == '__main__':
    print(get_random_trivia("東京"))
