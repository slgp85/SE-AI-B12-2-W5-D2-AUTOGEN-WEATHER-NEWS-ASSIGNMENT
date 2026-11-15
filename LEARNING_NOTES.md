# Week 5 · Day 2: Build an AutoGen Weather News Agent: Learning Notes (What · Why · How)


---

_Personal study notes: what was built, why it was built that way, how it works, and what happened when it ran._


---

## 9. Week 5 Day 2: AutoGen Weather News (tool calling)

**What:** `weather_news.py`. The agent gets a Python function as a tool, searches DuckDuckGo (`ddgs`, no key) and replies in 3 short lines.

**How tool calling works**
1. AutoGen turns `search_weather_news(city: str) -> str` plus its **docstring** into a JSON schema.
2. The model decides to call it: `ToolCallRequestEvent → search_weather_news(city='Chennai')`.
3. AutoGen runs the function: `ToolCallExecutionEvent` (the raw results).
4. **`reflect_on_tool_use=True`** makes a second LLM call that turns the raw results into 3 clean lines.
   *If it were False* the agent's final message would be the **raw tool output** (a `ToolCallSummaryMessage`), i.e. a dump of search results.

**Why the docstring matters:** it is the tool's manual for the model. "Search the live web for **TODAY'S weather news**… NOT for general facts" tells the model exactly when to use the tool.

---

## 3. Environment setup (VS Code + Command Prompt)

Folder layout:
```
Pending Assignment/
├─ .env                 ← your keys (git-ignored)
├─ .env.example         ← template without secrets (safe to commit)
├─ .gitignore           ← ignores .env, venv/
├─ .vscode/settings.json← default terminal = Command Prompt, interpreter = venv
├─ venv/                ← one Python 3.12 virtual environment for all projects
├─ tools/terminal_shot.py ← turns a captured run log into a terminal screenshot
├─ Week4_Day1_.../  Week4_Day2_.../  ...  Weekly_Buildathon_CrewAI_Support/
│     ├─ <code>.py / <workflow>.json
│     ├─ output/       ← captured console output of each run
│     └─ screenshots/  ← PNG screenshots for submission
└─ _assignment_pdfs/    ← the original assignment PDFs
```

**Step by step (in VS Code: Terminal → New Terminal; it opens Command Prompt):**
```bat
cd "D:\SocialEagle AI\Pending Assignment"
py -3.12 -m venv venv
venv\Scripts\activate.bat
pip install "crewai[tools]" streamlit python-dotenv ddgs autogen-agentchat "autogen-ext[openai]"
copy .env.example .env      &  REM then edit .env and paste your keys
```
**Why Python 3.12 and not 3.14?** CrewAI and several of its dependencies don't support 3.14 yet. Pick a Python version your libraries support. This is a common interview "gotcha".

**Why a venv?** It keeps each project's dependencies separate, so the project is reproducible and won't break other projects.

**Why `.env` + `load_dotenv(find_dotenv())`?** Secrets never go into code or Git. `find_dotenv()` searches upward from the script's folder, so all sub-folders share one `.env` at the root.

---

## 2. Core vocabulary (memorise these)

| Term | Meaning |
|---|---|
| **System prompt / system_message** | Hidden instructions that set the model's persona and rules. They have more influence than anything else you write. |
| **Role / Goal / Backstory** (CrewAI) | Three parts of an agent's persona. *Role* = job title, *Goal* = what success looks like, *Backstory* = experience and audience, which sets the tone. |
| **Task** (CrewAI) | One unit of work: `description` (what to do) + `expected_output` (the format of the result) + `agent`. |
| **expected_output** | The output contract. It is the best lever for getting a precise format such as "exactly 3 numbered lines". |
| **Crew** | A container that holds the agents and tasks and runs them with a **Process** (`sequential` or `hierarchical`). |
| **context=[task]** | Passes one task's output into another task. |
| **Tool** | A function the LLM may call. The model sees the tool's **name, parameters and description/docstring** and nothing else. |
| **Tool calling / function calling** | The model returns structured JSON such as `{"name": "search", "args": {...}}`. The framework runs it and sends the result back to the model. |
| **reflect_on_tool_use** (AutoGen) | After a tool runs, make one more LLM call so the agent writes a natural-language answer from the raw result. |
| **async / await** | AutoGen is built on `asyncio`, so calls to the model don't block. `asyncio.run(main())` starts the event loop. |
| **Human-in-the-loop (HITL)** | The workflow pauses until a person approves (Gmail *Send and wait*). |
| **Memory** | Information that persists between turns or sessions. Hermes `USER.md` is long-term memory that is loaded at start-up. |
| **Credential store** | n8n keeps API keys encrypted, apart from the workflow JSON, so exported JSON has no secrets. |
| **Environment variable / .env** | Where secrets live outside the code. `python-dotenv` loads `.env` into `os.environ`. |
| **Hallucination** | The model makes up facts. Reduce it with tools (search) and grounding instructions ("use only the search results"). |
| **Token** | About ¾ of a word. Cost and context limits are counted in tokens, which is why you send the snippet and not the full email body. |

---

## 14. Best practices, security & common errors

**Security**
- Never hard-code keys. Use `.env` + `.gitignore`, or the n8n credential store. Commit `.env.example` only.
- Never screenshot `.env`, `config.yaml` with keys, or the n8n credential pages.
- Give each agent only the tools it needs (least privilege).
- Treat tool and web output as untrusted, because of the prompt-injection risk.

**Reliability**
- Specify format in `expected_output` / the system message ("exactly N lines").
- Use `verbose=True` while developing and turn it off in production.
- Always `await model_client.close()` in AutoGen.
- Add fallbacks (Serper → DuckDuckGo) and timeouts.

**Common errors & fixes**
| Error | Cause | Fix |
|---|---|---|
| `OPENAI_API_KEY is not set` | `.env` not loaded | `load_dotenv(find_dotenv())`, check the file location |
| CrewAI install fails on Python 3.14 | Version not supported | Use Python 3.10–3.13 |
| pip "resolving dependencies" forever | Many packages with conflicting pins | Use `uv pip install`, pin versions |
| AutoGen script never exits | Model client not closed | `await model_client.close()` |
| Writer agent searches again | Writer was given tools | Remove `tools` from the Writer |
| n8n sends 5 emails | No Aggregate node | Add Aggregate before Send |
| n8n `{{$json.from}}` is empty | Field is `From` (capital) in simplified output | Check the output panel for exact field names |
| Hermes ignores USER.md | No restart / wrong folder | Restart; the file must be `%HERMES_HOME%\memories\USER.md` |
| DuckDuckGo `RatelimitException` | Too many requests | Retry later, lower `max_results`, or use Serper |

---

## 15. Interview questions & model answers

**Basics**
1. **What is an AI agent?** An LLM that runs in a loop: it reasons about a goal, decides whether to call tools, looks at the results and repeats until it can answer. Its parts are model + instructions + tools + memory + an orchestration loop.
2. **Agent vs workflow?** A workflow follows a path set in advance (deterministic and easy to audit). An agent chooses its path at run time (flexible but less predictable). Production systems often put agents *inside* workflows.
3. **What is tool/function calling?** The model is given JSON schemas of the functions it may use. It returns a structured call (name + args), the framework runs it and sends the result back as a message, and the model continues.
4. **How does the model know when to use a tool?** Only from the tool's name, parameter schema and description/docstring, so a precise docstring is essential.
5. **What is ReAct?** Reason + Act: the model alternates thought → action (tool) → observation until it gives a final answer. CrewAI agents follow this loop.

**CrewAI**
6. **Agent, Task, Crew?** An Agent is a persona (role/goal/backstory, tools, LLM). A Task is a unit of work (description, expected_output, agent, context). A Crew holds agents and tasks plus a process.
7. **How does data pass between tasks?** In sequential mode, the previous task's output is available to the next one. Use `context=[task]` to pass a specific task's output explicitly, including outputs from several tasks.
8. **Sequential vs hierarchical?** Sequential runs tasks in order. Hierarchical adds a manager agent/LLM that plans, delegates and checks the work.
9. **Why give the Writer no tools?** If it has tools, an agent may keep researching instead of writing. Least privilege keeps each role focused and cuts cost.
10. **Why does backstory matter?** It goes into the system prompt and sets the audience, expertise and tone, which changes both content and style.

**AutoGen**
11. **Why async?** LLM and tool calls are I/O-bound. Async lets agents stream output and run concurrently without blocking. `asyncio.run(main())` starts the event loop.
12. **What does `reflect_on_tool_use` do?** After a tool call it makes one more model call to summarise the tool result in natural language. Without it the reply is the raw tool output.
13. **`run` vs `run_stream`?** `run` returns the final `TaskResult`. `run_stream` yields every message and event as it happens, so `Console` can show it live.
14. **AutoGen team types?** RoundRobinGroupChat, SelectorGroupChat (the LLM picks the next speaker), Swarm (hand-offs), GraphFlow (a directed graph).

**n8n**
15. **How does n8n handle multiple items?** Each node runs once per item. Aggregate/Merge/Split nodes change the number of items.
16. **How do you add human approval?** Use Gmail/Slack *Send and wait for response* (Approval type) or a Wait node. The execution is saved and resumes when the person clicks.
17. **Where are credentials stored?** Encrypted in n8n's database. An exported workflow JSON only refers to them by ID or name.

**Memory & Hermes**
18. **Types of agent memory?** Short-term (conversation history), long-term (persisted facts, e.g. USER.md, vector DB), entity memory (facts about people and things), procedural (skills).
19. **Why did Hermes need a restart after editing USER.md?** The file goes into the system prompt when a session starts. A running session already has its prompt built.
20. **Instruction vs description in a prompt?** Instructions can be checked ("max 3 bullets"). Descriptions ("I like concise") are vague and often ignored.

**Design / scenario**
21. **How would you reduce hallucinations in the support bot?** Ground answers with web search or RAG, tell the agent to use only the retrieved sources, cite sources, lower the temperature, and add a reviewer/judge agent.
22. **How would you scale the Buildathon app?** Run crews as background jobs (Celery/queue), cache answers, use a DB instead of a txt file, add auth, rate limits and observability (LangSmith/AgentOps/OpenTelemetry), and use a cheaper model for simple routing.
23. **How do you control cost?** Smaller models (gpt-4o-mini) for simple steps, trimmed inputs (snippets, not bodies), caching, `max_iter`/`max_tokens` limits, and fewer agents.
24. **How do you test agents?** Fixed test prompts with assertions on format (e.g. line count), LLM-as-judge for quality, mocked tools for deterministic tests, and logging of every trace.
25. **How do you keep secrets safe in a team repo?** `.env` + `.gitignore` + `.env.example`, secret managers in production (Azure Key Vault / AWS Secrets Manager), pre-commit secret scanning, and key rotation.
26. **What should be done by the LLM and what by plain code?** Let the LLM do reasoning and language. Do deterministic work (copying exact text, file I/O, IDs, dates, maths) in code or tools. Example: the Buildathon save tool reads the task outputs directly instead of trusting the LLM to copy them.
27. **Tell me about a bug you fixed in an agent.** Use the Entry Agent story: the symptom (paraphrased answers, repeated tool calls), the root cause (the LLM was given data to copy), the fix (a no-argument, idempotent tool) and how you verified it (one entry per query in answers.txt).
