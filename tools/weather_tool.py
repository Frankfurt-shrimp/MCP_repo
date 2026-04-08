"""
Tool：查詢目的地即時天氣
使用 API：https://wttr.in/{city}?format=j1
負責：陳柏宇
（沿用上週 w6-agnet-group-4 實作）
"""

import requests


def get_weather(city: str) -> str:
    """
    查詢指定城市的即時天氣資訊。
    呼叫 https://wttr.in/{city}?format=j1 API 取得天氣資料，
    解析 temp_C（溫度）與 weatherDesc（天氣描述）。
    回傳格式：「城市：{city}, 溫度：{temp}°C, 天氣：{desc}」
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        weather_desc = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        feels_like = current["FeelsLikeC"]
        wind_speed = current["windspeedKmph"]
        wind_dir = current["winddir16Point"]

        return (
            f"城市：{city}\n"
            f"溫度：{temp_c}°C（體感溫度：{feels_like}°C）\n"
            f"天氣：{weather_desc}\n"
            f"濕度：{humidity}%\n"
            f"風速：{wind_speed} km/h，風向：{wind_dir}"
        )
    except requests.exceptions.Timeout:
        return f"錯誤：查詢 {city} 天氣時連線逾時，請稍後再試。"
    except requests.exceptions.RequestException as e:
        return f"錯誤：無法取得 {city} 的天氣資訊，網路錯誤：{str(e)}"
    except (KeyError, IndexError) as e:
        return f"錯誤：解析 {city} 天氣資料失敗，資料格式異常：{str(e)}"
    except Exception as e:
        return f"錯誤：查詢 {city} 天氣時發生未預期的錯誤：{str(e)}"


TOOL = {
    "name": "weather_tool",
    "description": "查詢目的地的即時天氣，包含溫度、體感溫度、天氣狀況、濕度與風速資訊",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "要查詢天氣的城市名稱（英文），例如: Tokyo, Taipei, London"
            }
        },
        "required": ["city"]
    }
}

if __name__ == '__main__':
    print(get_weather("Taipei"))
