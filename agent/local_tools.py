"""Tools that run on the agent's own machine (they never go through the MCP server)."""
import os
import re

from langchain.tools import ToolRuntime, tool

REPORT_DIR = "reports"
MAX_REPORT_CHARS = 5000


def save_report(filename: str, content: str) -> str:
    """Save a text report. Use only when the student asks to save."""
    if len(content) > MAX_REPORT_CHARS:
        return "Error: report too long."
    base = os.path.splitext(os.path.basename(filename))[0]
    safe = re.sub(r"[^A-Za-z0-9_\-]", "_", base)[:50] or "report"
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, safe + ".txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Saved as {safe}.txt"
    except Exception:
        return "Error: could not save file."


@tool
def history(runtime: ToolRuntime) -> str:
    """List what the student asked earlier in this chat. Runs locally, so it works even when the MCP server is down."""
    asked = [m.text for m in runtime.state["messages"] if m.type == "human"]
    return "\n".join(f"{i}. {q}" for i, q in enumerate(asked, 1)) or "No earlier messages."
