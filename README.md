# Week 5 · Day 2 — AutoGen Weather News Agent (tool calling)

## Standalone setup (fresh clone, VS Code → Command Prompt)
```bat
py -3.12 -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
REM edit .env and paste your OpenAI key
```

`search_weather_news(city: str) -> str` (DuckDuckGo via `ddgs`, no key) is passed in `tools=[...]`;
`reflect_on_tool_use=True` turns raw results into exactly 3 short lines.

| File | Purpose |
|---|---|
| `weather_news.py` | The code |
| `output/run_<city>.txt` | Captured console output (two cities) |
| `screenshots/run_<city>.png` | Terminal screenshots showing the ToolCallRequestEvent + 3-line reply |

## Run
```bat
venv\Scripts\activate.bat
cd Week5_Day2_AutoGen_Weather_News
python weather_news.py
```
