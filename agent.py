"""
W8 分組實作：MCP Client + Gemini Agent
主題：旅遊顧問

使用方式：
  1. 直接使用 stdio（推薦，適合本地測試）：
     python agent.py
  2. 分開啟動 SSE Server：
     終端機 1：python server.py --transport sse
     終端機 2：python agent.py --transport sse

特殊指令：
  /prompts  - 列出所有可用的 Prompt
  /use <名稱> <參數> - 使用指定 Prompt（例：/use plan_trip Taipei）
  quit / exit / q - 離開
"""

import asyncio
import argparse
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

# 從 .env 檔讀取環境變數
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 建立 Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"

# 重試設定
MAX_RETRIES = 3
RETRY_DELAY = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Travel Advisor MCP Agent")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="How the agent connects to the MCP server.",
    )
    parser.add_argument(
        "--server-url",
        default=os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000/sse"),
        help="SSE endpoint used when --transport sse.",
    )
    return parser.parse_args()


def mcp_tools_to_gemini_declarations(mcp_tools):
    """把 MCP Server 的工具清單轉換成 Gemini function declaration 格式"""
    declarations = []
    for tool in mcp_tools:
        properties = {}
        required = []
        if tool.inputSchema and "properties" in tool.inputSchema:
            for prop_name, prop_info in tool.inputSchema["properties"].items():
                properties[prop_name] = types.Schema(
                    type=types.Type.STRING,
                    description=prop_info.get("description", ""),
                )
            required = tool.inputSchema.get("required", [])

        declaration = types.FunctionDeclaration(
            name=tool.name,
            description=tool.description or "",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties=properties,
                required=required,
            ) if properties else None,
        )
        declarations.append(declaration)
    return declarations


def call_gemini_with_retry(model, contents, config):
    """呼叫 Gemini API，遇到 429 rate limit 自動重試"""
    for attempt in range(MAX_RETRIES):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < MAX_RETRIES - 1:
                    print(f"\n⏳ API 額度暫時用完，等待 {RETRY_DELAY} 秒後重試... ({attempt + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                else:
                    print("\n❌ API 額度持續不足，請稍後再試。")
                    raise
            else:
                raise


@asynccontextmanager
async def open_mcp_session(args: argparse.Namespace):
    if args.transport == "sse":
        print(f"🔗 連接 MCP Server（SSE）：{args.server_url}")
        async with sse_client(args.server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
        return

    server_path = Path(__file__).with_name("server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )
    print(f"🔗 啟動 MCP Server（stdio）：{server_path}")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def main():
    args = parse_args()

    async with open_mcp_session(args) as session:
        # 取得所有工具
        tools_result = await session.list_tools()
        mcp_tools = tools_result.tools
        print(f"✅ 已連接！取得 {len(mcp_tools)} 個工具：")
        for t in mcp_tools:
            print(f"   🔧 {t.name}: {t.description}")

        # 取得所有 Prompt
        prompts_result = await session.list_prompts()
        mcp_prompts = prompts_result.prompts
        print(f"\n📝 可用的 Prompt：")
        for p in mcp_prompts:
            args_list = [a.name for a in p.arguments] if p.arguments else []
            print(f"   📌 {p.name}({', '.join(args_list)}): {p.description}")
        print()

        # 轉換成 Gemini function declaration 格式
        gemini_declarations = mcp_tools_to_gemini_declarations(mcp_tools)
        gemini_tools = types.Tool(function_declarations=gemini_declarations)

        # 對話歷史
        chat_history = []

        system_instruction = (
            "你是一個旅遊顧問 AI，名叫 Travel Advisor。"
            "你可以幫使用者查詢目的地天氣、推薦活動、提供旅行建議、分享冷知識和知識問答。"
            "請用繁體中文回答，語氣活潑親切。"
        )

        print("🌍 Travel Advisor 已啟動！")
        print("   輸入 /prompts 查看可用 Prompt")
        print("   輸入 /use <名稱> <參數> 使用 Prompt")
        print("   輸入 quit 離開")
        print("=" * 50)

        while True:
            user_input = input("\n你：").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("\n👋 祝旅途愉快！")
                break
            if not user_input:
                continue

            # 列出 Prompts
            if user_input == "/prompts":
                print("\n📝 可用的 Prompt：")
                for p in mcp_prompts:
                    args_list = [a.name for a in p.arguments] if p.arguments else []
                    print(f"   📌 {p.name}({', '.join(args_list)}): {p.description}")
                continue

            # 使用 Prompt：/use plan_trip Taipei
            if user_input.startswith("/use "):
                parts = user_input.split(maxsplit=2)
                if len(parts) < 3:
                    print("❌ 格式：/use <prompt名稱> <參數>")
                    continue
                prompt_name = parts[1]
                prompt_arg = parts[2]

                try:
                    # 取得 prompt 的參數名稱
                    prompt_info = next(
                        (p for p in mcp_prompts if p.name == prompt_name), None
                    )
                    if not prompt_info:
                        print(f"❌ 找不到 Prompt: {prompt_name}")
                        continue

                    arg_name = prompt_info.arguments[0].name if prompt_info.arguments else "arg"
                    prompt_result = await session.get_prompt(
                        prompt_name, arguments={arg_name: prompt_arg}
                    )
                    user_input = prompt_result.messages[0].content.text
                    print(f"\n📌 使用 Prompt: {prompt_name}({prompt_arg})")
                    print(f"   生成的提示詞：{user_input[:80]}...")
                except Exception as e:
                    print(f"❌ Prompt 呼叫失敗：{e}")
                    continue

            # 加入使用者訊息
            chat_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_input)],
                )
            )

            # 與 Gemini 對話
            while True:
                try:
                    response = call_gemini_with_retry(
                        model=MODEL,
                        contents=chat_history,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            tools=[gemini_tools],
                        ),
                    )
                except Exception as e:
                    print(f"\n❌ Gemini API 錯誤：{e}")
                    chat_history.pop()
                    break

                candidate = response.candidates[0]
                parts = candidate.content.parts
                chat_history.append(candidate.content)

                # 檢查 function call
                function_calls = [p for p in parts if p.function_call]

                if not function_calls:
                    text_parts = [p.text for p in parts if p.text]
                    if text_parts:
                        print(f"\n🤖：{''.join(text_parts)}")
                    break

                # 呼叫 MCP Tool
                function_response_parts = []
                for fc_part in function_calls:
                    fc = fc_part.function_call
                    tool_name = fc.name
                    tool_args = dict(fc.args) if fc.args else {}

                    print(f"\n🔧 呼叫工具：{tool_name}({tool_args})")

                    try:
                        result = await session.call_tool(
                            tool_name, arguments=tool_args
                        )
                        tool_result = result.content[0].text
                    except Exception as e:
                        tool_result = f"工具呼叫失敗：{str(e)}"

                    print(f"📦 結果：{tool_result[:100]}...")

                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=tool_name,
                            response={"result": tool_result},
                        )
                    )

                chat_history.append(
                    types.Content(
                        role="user",
                        parts=function_response_parts,
                    )
                )


if __name__ == "__main__":
    asyncio.run(main())
