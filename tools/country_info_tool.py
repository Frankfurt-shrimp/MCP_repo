"""
Tool：查詢國家旅遊基本資訊
使用 API：https://restcountries.com/v3.1/name/{country}
負責：林永富
"""

import requests

TOOL_INFO = {
    "name": "get_country_info",
    "api": "https://restcountries.com/v3.1/name/{country}",
    "author": "林永富",
}


def get_country_info_data(country: str) -> str:
    """呼叫 REST Countries API，回傳國家的旅遊實用資訊"""
    resp = requests.get(
        f"https://restcountries.com/v3.1/name/{country}",
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()[0]

    name = data.get("name", {}).get("common", country)
    capital = ", ".join(data.get("capital", ["未知"]))
    region = data.get("region", "未知")
    subregion = data.get("subregion", "")
    population = data.get("population", 0)

    # 貨幣
    currencies = data.get("currencies", {})
    currency_list = [
        f"{v.get('name', k)}（{v.get('symbol', '')}）"
        for k, v in currencies.items()
    ]
    currency_str = ", ".join(currency_list) if currency_list else "未知"

    # 語言
    languages = data.get("languages", {})
    lang_str = ", ".join(languages.values()) if languages else "未知"

    # 時區
    timezones = data.get("timezones", [])
    tz_str = ", ".join(timezones[:3]) if timezones else "未知"

    return (
        f"🌍 {name} 旅遊資訊\n"
        f"首都：{capital}\n"
        f"地區：{region}" + (f" / {subregion}" if subregion else "") + "\n"
        f"人口：{population:,}\n"
        f"貨幣：{currency_str}\n"
        f"語言：{lang_str}\n"
        f"時區：{tz_str}"
    )


if __name__ == "__main__":
    print(get_country_info_data("Japan"))
