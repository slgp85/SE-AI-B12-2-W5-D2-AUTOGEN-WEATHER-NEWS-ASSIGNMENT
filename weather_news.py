"""
Week 5 - Day 2 : AutoGen Weather News Agent (with a tool)
---------------------------------------------------------
A plain Python function becomes a tool. The agent reads its name, type hints
and docstring to decide when to call it. reflect_on_tool_use=True makes the
agent write a final answer from the raw search results.

Run (inside the VS Code terminal, venv activated):
    python weather_news.py
"""
import asyncio
import os

from dotenv import find_dotenv, load_dotenv
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv(find_dotenv())
if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY is not set. Add it to your .env file.")


def search_weather_news(city: str) -> str:
    """Search the live web for TODAY'S weather news and forecast for a city.

    Use this tool whenever the user asks about current weather, rain, heat,
    storms, temperature or weather alerts in a specific city. It is NOT for
    general facts or history.

    Args:
        city: Name of the city, e.g. "Chennai".
    Returns:
        Recent news headlines and snippets about the city's weather.
    """
    try:
        # timelimit="w" -> only news from the last week, so we never report old weather
        hits = DDGS().news(query=f"{city} weather today", max_results=5, timelimit="w")
        hits = [h for h in hits if "weather" in (h.get("title", "") + h.get("body", "")).lower()
                or "rain" in (h.get("title", "") + h.get("body", "")).lower()]
        if not hits:
            hits = DDGS().text(query=f"{city} weather today forecast", max_results=5)
    except Exception as exc:  # network / rate-limit problems
        return f"Search failed: {exc}"
    return "\n".join(
        f"- {h.get('title')} ({h.get('date', 'today')}): {h.get('body', '')}" for h in hits
    ) or "No results found."


city = input("Which city? ").strip() or "Chennai"
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

agent = AssistantAgent(
    name="weather_news",
    model_client=model_client,
    tools=[search_weather_news],
    system_message=(
        "You are a weather news reporter. Always call search_weather_news before "
        "answering. Reply in exactly 3 short lines (max 15 words each), plain text, "
        "no bullets, no headings. Only use facts from the search results, ignore "
        "results that are old or not about weather, and never invent details."
    ),
    reflect_on_tool_use=True,
)


async def main() -> None:
    try:
        await Console(agent.run_stream(task=f"What is the weather news in {city} today?"))
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
