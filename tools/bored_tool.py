"""
Tool：推薦隨機活動
使用 API：https://bored-api.appbrewery.com/random
負責：陳婉榕
（沿用上週 w6-agnet-group-4 實作）
"""

import requests


def get_random_activity() -> str:
    """
    呼叫 https://bored-api.appbrewery.com/random API 取得活動建議。
    回傳：回傳活動名稱與類型 (例如：Learn a new recipe (類型: education))
    """
    try:
        response = requests.get("https://bored-api.appbrewery.com/random", timeout=5)
        response.raise_for_status()
        data = response.json()
        activity = data.get("activity", "Go for a walk")
        type_ = data.get("type", "relaxation")
        return f"{activity} (類型: {type_})"
    except Exception:
        return "Take a deep breath and relax (類型: relaxation)"


TOOL = {
    "name": "bored_tool",
    "description": "取得一則隨機的休閒活動建議，適合旅途中不知道做什麼時參考。",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

if __name__ == '__main__':
    print(get_random_activity())
