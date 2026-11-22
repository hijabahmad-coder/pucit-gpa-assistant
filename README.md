# PUCIT CGPA Guider (Assignment 3: memory, streaming, MCP)

A LangChain agent (Groq `gpt-oss-20b`) for PUCIT BS(CS) GPA/CGPA questions.
All numbers come from plain-Python tools, served by **our own MCP server**. The model does no arithmetic.

> Unofficial student project, not affiliated with PUCIT. Verify the grade scale and course list against the official policy.

**MCP server URL:** `hhttps://cgpa-guide.fastmcp.app/mcp`  *(fill in after deploying; no API key needed unless noted here)*

## What changed from the first version

| Problem | Fix |
|---|---|
| It forgot everything on exit | `AsyncSqliteSaver` (`chats.db`), username = `thread_id` |
| Blank screen while thinking | `astream(stream_mode=["updates","messages"])`: live tokens + tool-call lines |
| Tools locked inside `tools.py` | `server/server.py` exposes them over MCP (FastMCP) |
| Crash when the server is down | tool errors become results; local `history` tool and `/history` still work |

## Layout

```
server/   server.py (FastMCP), tools.py (9 tools), requirements.txt
agent/    agent.py (CLI agent), local_tools.py (history, save_report), guards.py, llm.py
tests/    pytest (tools, MCP server, memory, streaming, server-down, security)
render.yaml   deploys server/ on Render
```

`save_report` stays on the agent side on purpose: file writes belong on the student's machine, not on a public server.
The old Streamlit version is kept at git tag `v1-streamlit`.

## Run locally

```bash
python -m venv .venv && .venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r server/requirements.txt -r agent/requirements.txt

# terminal 1: the MCP server (http://127.0.0.1:8000/mcp)
cd server && python server.py
fastmcp list server.py                                # check: 9 tools, no agent or key needed

# terminal 2: the agent
cd agent && copy .env.example .env                    # then put GROQ_API_KEY in .env
python agent.py
```

Chat commands: `/switch` (change user), `/history` (show saved chat), `/forget` (delete saved chat), `exit`.

## Deploy the server (Task 5)

1. Push this repo to GitHub. On Render: New > Blueprint > pick the repo (uses `render.yaml`).
2. Copy the service URL, check it: `fastmcp list https://cgpa-guide.fastmcp.app/mcp`
3. In `agent/.env` set `https://cgpa-guide.fastmcp.app/mcp` 

Free Render services sleep when idle, so the first request can take about a minute.

## When the server is down (Task 6)

- Start-up: the agent still starts with local tools only.
- Mid-chat: a failed tool call becomes an error result, the model tells the student, and the next message works.
- `/history`, `/switch`, `/forget` never touch the network or the model.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

See [SECURITY.md](SECURITY.md) for the threat model. License: MIT.
