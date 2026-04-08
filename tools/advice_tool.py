"""
Tool：取得隨機人生建議
使用 API：https://api.adviceslip.com/advice
負責：陳婉榕
（沿用上週 w6-agnet-group-4 實作）
"""

import requests


def get_random_advice() -> str:
    """
    呼叫 https://api.adviceslip.com/advice 取得旅行格言/人生建議。
    回傳：一句隨機建議字串。
    """
    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("slip", {}).get("advice", "保持一顆開放的心，旅行就會處處充滿驚喜！")
    except Exception:
        return "保持一顆開放的心，旅行就會處處充滿驚喜！"


TOOL = {
    "name": "advice_tool",
    "description": "取得一則隨機的人生建議或格言。",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

if __name__ == '__main__':
    print(get_random_advice())
