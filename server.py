# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0.0",
#     "requests>=2.28.0",
#     "duckduckgo-search>=7.0.0",
#     "typer>=0.16.0"
# ]
# ///

"""
W8 分組實作：MCP Server
主題：旅遊顧問 MCP Server

分工說明（沿用上週 w6-agnet-group-4）：
- 陳柏宇：weather_tool（天氣查詢）
- 楊承軒：search_tool（景點美食搜尋）
- 陳婉榕：bored_tool / advice_tool（活動建議 / 人生建議）
- 林永富：trivia_tool / country_info_tool（在地冷知識 / 國家資訊）
- 洪紹禎：Resource + Prompt + Agent
"""

import argparse
import os
import sys

from mcp.server.fastmcp import FastMCP

try:
    from .tools.weather_tool import get_weather
    from .tools.search_tool import web_search
    from .tools.advice_tool import get_random_advice
    from .tools.bored_tool import get_random_activity
    from .tools.trivia_tool import get_random_trivia
    from .tools.country_info_tool import get_country_info_data
except ImportError:
    from tools.weather_tool import get_weather
    from tools.search_tool import web_search
    from tools.advice_tool import get_random_advice
    from tools.bored_tool import get_random_activity
    from tools.trivia_tool import get_random_trivia
    from tools.country_info_tool import get_country_info_data

DEFAULT_HOST = os.environ.get("MCP_HOST", "localhost")
DEFAULT_PORT = int(os.environ.get("MCP_PORT", "8000"))

mcp = FastMCP(
    "旅遊顧問-server",
    host=DEFAULT_HOST,
    port=DEFAULT_PORT,
    dependencies=["requests", "duckduckgo-search", "typer"],
)


# ════════════════════════════════
#  Tools：各組員各自負責的 Tool
# ════════════════════════════════

# 陳柏宇：天氣查詢
@mcp.tool()
def weather(city: str) -> str:
    """查詢指定城市的即時天氣資訊，包含溫度、體感溫度、濕度和風速。
    當使用者詢問天氣、溫度、是否該帶傘或穿什麼衣服時使用。"""
    return get_weather(city)


# 楊承軒：景點美食搜尋
@mcp.tool()
def search(query: str) -> str:
    """搜尋旅遊景點、美食、住宿等相關資訊。
    當使用者想查找特定目的地的景點推薦、必吃美食或旅遊攻略時使用。"""
    return web_search(query)


# 陳婉榕：活動建議
@mcp.tool()
def activity() -> str:
    """取得一則隨機的休閒活動建議，適合旅途中不知道做什麼時參考。
    當使用者需要活動靈感、旅途中想找事做時使用。"""
    return get_random_activity()


# 陳婉榕：人生建議
@mcp.tool()
def advice() -> str:
    """取得一則隨機的人生建議或格言。
    當使用者需要旅行前的人生建議、鼓勵或心靈雞湯時使用。"""
    return get_random_advice()


# 林永富：在地冷知識
@mcp.tool()
def trivia(city: str) -> str:
    """取得與目的地相關的在地冷知識與背景介紹（使用維基百科）。
    當使用者想了解目的地的歷史、文化或有趣小知識時使用。"""
    return get_random_trivia(city)


# 林永富：國家旅遊資訊（本週新增）
@mcp.tool()
def country_info(country: str) -> str:
    """查詢指定國家的旅遊基本資訊，包含首都、貨幣、語言和時區。
    當使用者要去某個國家旅行，需要了解當地基本資訊時使用。"""
    return get_country_info_data(country)


# ════════════════════════════════
#  Resource：提供靜態參考資料
#  負責：洪紹禎
# ════════════════════════════════

@mcp.resource("info://travel-tips")
def get_travel_tips() -> str:
    """旅行必帶物品與注意事項清單"""
    return (
        "旅行必帶物品：\n"
        "- 護照 / 身分證\n"
        "- 當地貨幣或信用卡\n"
        "- 備用藥品\n"
        "- 充電器與轉接頭\n\n"
        "出發前注意：\n"
        "- 確認當地天氣，準備適當衣物\n"
        "- 查詢當地緊急電話\n"
        "- 備份重要文件"
    )


# ════════════════════════════════
#  Prompt：整合多個 Tool 的提示詞模板
#  負責：洪紹禎
# ════════════════════════════════

@mcp.prompt()
def plan_trip(city: str) -> str:
    """產生旅遊行前簡報的提示詞"""
    return (
        f"我要去 {city} 旅行，請幫我準備一份完整的行前簡報：\n"
        f"1. 查詢 {city} 的天氣，判斷需要帶什麼衣物\n"
        f"2. 搜尋 {city} 的熱門景點和必吃美食\n"
        f"3. 查詢該國家的基本旅遊資訊（貨幣、語言等）\n"
        f"4. 給我一則旅遊相關的在地冷知識\n"
        f"5. 推薦 2-3 個可以做的活動\n"
        f"6. 給我一則旅行前的人生建議\n"
        f"請用繁體中文，語氣活潑。"
    )


def parse_args() -> argparse.Namespace:
    """讓同一份 server 同時支援 Inspector(stdio) 與獨立 SSE 啟動。"""
    parser = argparse.ArgumentParser(description="Travel Advisor MCP Server")
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="HTTP bind host used for SSE/streamable-http transports.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="HTTP bind port used for SSE/streamable-http transports.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="MCP transport mode. Default is stdio for Inspector compatibility.",
    )
    parser.add_argument(
        "--mount-path",
        default=os.environ.get("MCP_MOUNT_PATH"),
        help="Optional mount path for HTTP transports.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    mcp.settings.host = args.host
    mcp.settings.port = args.port

    # stdio 模式不能往 stdout 印任何文字，否則會破壞 MCP JSON-RPC。
    if args.transport != "stdio":
        print(
            f"MCP Server 啟動中... transport={args.transport} http://{args.host}:{args.port}",
            file=sys.stderr,
        )

    run_kwargs = {"transport": args.transport}
    if args.mount_path:
        run_kwargs["mount_path"] = args.mount_path

    mcp.run(**run_kwargs)
