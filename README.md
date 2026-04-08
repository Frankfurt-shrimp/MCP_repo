# MCP Server + AI agent 分組實作

> 課程：AI Agent 開發 — MCP（Model Context Protocol）
> 主題：旅遊顧問 MCP Server

---

## Server 功能總覽

> 這個 MCP Server 是一個「旅遊顧問」，提供天氣查詢、景點搜尋、國家資訊、活動推薦等旅行前必備功能。

| Tool 名稱            | 功能說明                     | 負責組員 |
| -------------------- | ---------------------------- | -------- |
| `get_weather`        | 查詢目的地即時天氣            | 陳柏宇   |
| `web_search`         | 搜尋景點、美食、旅遊攻略      | 楊承軒   |
| `get_activity`       | 推薦可以做的活動              | 陳婉榕   |
| `get_advice`         | 取得旅行前的人生建議          | 陳婉榕   |
| `get_fun_fact`       | 取得隨機趣味冷知識            | 陳婉榕   |
| `get_trivia`         | 旅途知識問答                  | 林永富   |
| `get_country_info`   | 查詢國家旅遊基本資訊          | 林永富   |

---

## 組員與分工

| 姓名   | 負責功能                              | 檔案                          | 使用的 API                    |
| ------ | ------------------------------------- | ----------------------------- | ----------------------------- |
| 陳柏宇 | get_weather                           | `tools/weather_tool.py`       | wttr.in                       |
| 楊承軒 | web_search                            | `tools/search_tool.py`        | duckduckgo-search             |
| 陳婉榕 | get_activity / get_advice / get_fun_fact | `tools/activity_tool.py` 等 | Bored API / Advice Slip / Useless Facts |
| 林永富 | get_trivia / get_country_info         | `tools/trivia_tool.py` 等    | Open Trivia / REST Countries  |
| 洪紹禎 | Resource + Prompt + Agent             | `server.py` / `agent.py`     | Gemini 2.5 Flash              |

---

## 專案架構

```
├── server.py                  # MCP Server 主程式（SSE 模式）
├── agent.py                   # MCP Client + Gemini Agent
├── tools/
│   ├── __init__.py
│   ├── weather_tool.py        # 天氣查詢（陳柏宇）
│   ├── search_tool.py         # 景點美食搜尋（楊承軒）
│   ├── activity_tool.py       # 推薦活動（陳婉榕）
│   ├── advice_tool.py         # 人生建議（陳婉榕）
│   ├── fun_fact_tool.py       # 趣味冷知識（陳婉榕）
│   ├── trivia_tool.py         # 知識問答（林永富）
│   └── country_info_tool.py   # 國家資訊（林永富）
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 使用方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定 API Key
cp .env.example .env
# 編輯 .env，填入你的 GEMINI_API_KEY

# 4. 用 MCP Inspector 測試 Server
mcp dev server.py

# 5. 用 Agent 對話（需開兩個終端機）
# 終端機 1：
python server.py
# 終端機 2：
python agent.py
```

---

## 測試結果

### MCP Inspector 截圖

> 貼上 Inspector 的截圖（Tools / Resources / Prompts 三個分頁都要有）

### Agent 對話截圖

![alt text](image.png)

---

## 各 Tool 說明

### `get_weather`（負責：陳柏宇）

- **功能**：查詢指定城市的即時天氣（溫度、體感、濕度、風速）
- **使用 API**：`https://wttr.in/{city}?format=j1`
- **參數**：`city: str` — 城市名稱
- **回傳範例**：

```
Taipei 天氣
溫度：22°C
體感：25°C
天氣：Partly Cloudy
濕度：78%
風速：11 km/h
```

### `web_search`（負責：楊承軒）

- **功能**：搜尋旅遊景點、美食、住宿等相關資訊
- **使用 API**：`duckduckgo-search` 套件
- **參數**：`query: str` — 搜尋關鍵字
- **回傳範例**：前 5 筆搜尋結果（標題 + 摘要 + 連結）

### `get_activity`（負責：陳婉榕）

- **功能**：推薦一個可以做的活動
- **使用 API**：`https://bored-api.appbrewery.com/random`
- **參數**：無
- **回傳範例**：

```
活動：Learn to play a new instrument
類型：music
參與人數：1
```

### `get_advice`（負責：陳婉榕）

- **功能**：取得一則隨機人生建議
- **使用 API**：`https://api.adviceslip.com/advice`
- **參數**：無
- **回傳範例**：`"Never regret. If it's good, it's wonderful. If it's bad, it's experience."`

### `get_fun_fact`（負責：陳婉榕）

- **功能**：取得一則隨機趣味冷知識
- **使用 API**：`https://uselessfacts.jsph.pl/api/v2/facts/random`
- **參數**：無
- **回傳範例**：`"The shortest war in history was between Zanzibar and England in 1896."`

### `get_trivia`（負責：林永富）

- **功能**：取得一則隨機知識問答（含問題、答案、類別和難度）
- **使用 API**：`https://opentdb.com/api.php?amount=1`
- **參數**：無
- **回傳範例**：

```
類別：Geography
難度：medium
問題：What is the capital of Australia?
答案：Canberra
```

### `get_country_info`（負責：林永富）

- **功能**：查詢指定國家的旅遊基本資訊（首都、貨幣、語言、時區）
- **使用 API**：`https://restcountries.com/v3.1/name/{country}`
- **參數**：`country: str` — 國家名稱（英文）
- **回傳範例**：

```
🌍 Japan 旅遊資訊
首都：Tokyo
地區：Asia / Eastern Asia
人口：125,836,021
貨幣：Japanese yen（¥）
語言：Japanese
時區：UTC+09:00
```

---

## 心得

### 遇到最難的問題

> 林永富：這次實作遇到最困難的部分是如何把從上週獨立開發的 Tool，全部整合進 FastMCP 的註冊系統裡。因為原本的架構大家是寫死在主程式，現在要透過 `@mcp.tool()` 來統一介面讓 Agent 辨識。我們解決的方式是，先規劃好每個 Tool 必須要有獨立的 return string，不處理任何互動邏輯，只要維持單純的 input/output。此外，`agent.py` 如何把伺服器的 MCP Tool schema 解析成 Gemini function declaration 也是一大挑戰，後來參考了老師的指引與使用迴圈一一對應 type 才成功。

### MCP 跟上週的 Tool Calling 有什麼不同？

> 林永富：做完這次實作後，我深刻體會到 MCP (Model Context Protocol) 帶來的高度解耦與擴展性。
> 上週的 Tool Calling，我們必須把 API 取得邏輯與呼叫大模型的程式碼「綁定」在同一個專案或腳本中。我們需要自己維護所有的函式定義，如果 Tool 增加，大模型的 prompt 或 function list 就要手動寫死。
> 然而，引入 MCP Server 後，**Tool 完全獨立於 Agent 之外**。Agent 就像客戶端，它只要連上 SSE (或 STDIO)，詢問「你有什麼能力？」，MCP Server 就會自動發出標準化的 JSON 宣告。這意味著，未來如果我想用別的模型（如 Claude 或其他大模型），我不需要重寫任何與天氣、查詢等有關的程式碼，只要換一個有配合 MCP 標準的 AI Client 即可。
> 簡單來說：**上週是「把工具塞給 AI」，這週 MCP 是「把工具做成伺服器，讓 AI 自己來要」**。這種標準化的架構讓開發與維護變得非常乾淨俐落！
