import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.tools import tool

import agent as A
from fakes import fake, tool_call


@tool
def flaky(x: int) -> int:
    """A tool whose server is down."""
    raise ConnectionError("server down")


async def ask(ag, text, thread="sara"):
    await A.stream_reply(ag, text, thread)


async def test_memory_survives_restart(tmp_path, capsys):
    db = str(tmp_path / "c.db")
    async with AsyncSqliteSaver.from_conn_string(db) as mem:
        await ask(A.build_agent(fake(AIMessage("Hi Sara")), [], mem), "I am sara, CGPA 3.1")
    async with AsyncSqliteSaver.from_conn_string(db) as mem:  # fresh agent, same file
        ag = A.build_agent(fake(AIMessage("ok")), [], mem)
        assert await A.list_threads(mem) == ["sara"]
        texts = [m.text for m in (await ag.aget_state(A.make_config("sara"))).values["messages"]]
        assert "I am sara, CGPA 3.1" in texts
        await A.show_history(ag, "sara")
    assert "You: I am sara" in capsys.readouterr().out


async def test_forget_deletes_thread(tmp_path, monkeypatch):
    async with AsyncSqliteSaver.from_conn_string(str(tmp_path / "c.db")) as mem:
        ag = A.build_agent(fake(AIMessage("hello")), [], mem)
        await ask(ag, "hi")
        monkeypatch.setattr("builtins.input", lambda _="": "y")
        await A.run_command("/forget", ag, mem, "sara")
        assert await A.list_threads(mem) == []


async def test_streaming_prints_tokens_and_tool_progress(tmp_path, capsys):
    async with AsyncSqliteSaver.from_conn_string(str(tmp_path / "c.db")) as mem:
        ag = A.build_agent(fake(tool_call("history", {}), AIMessage("done now")), [], mem)
        await ask(ag, "what did I ask?")
    out = capsys.readouterr().out
    assert "[calling history" in out and "Agent: done now" in out


async def test_dead_server_does_not_crash_or_corrupt_chat(tmp_path, capsys):
    async with AsyncSqliteSaver.from_conn_string(str(tmp_path / "c.db")) as mem:
        ag = A.build_agent(fake(tool_call("flaky", {"x": 1}), AIMessage("Server is down."),
                                AIMessage("Still here.")), [flaky], mem)
        await ask(ag, "calculate")
        await ask(ag, "again?")  # second turn works: no dangling tool call in the saved state
    out = capsys.readouterr().out
    assert "tool failed: ConnectionError" in out and "Still here." in out


async def test_history_tool_is_local(tmp_path, capsys):
    async with AsyncSqliteSaver.from_conn_string(str(tmp_path / "c.db")) as mem:
        ag = A.build_agent(fake(tool_call("history", {}), AIMessage("ok")), [], mem)
        await ask(ag, "my first question")
        msgs = (await ag.aget_state(A.make_config("sara"))).values["messages"]
    assert "1. my first question" in [m for m in msgs if m.type == "tool"][0].content


async def test_startup_falls_back_when_server_down(monkeypatch, capsys):
    monkeypatch.setattr(A, "MCP_URL", "http://127.0.0.1:9/mcp")  # nothing listens here
    assert await A.safe_load_tools() == []
    assert "unreachable" in capsys.readouterr().out
