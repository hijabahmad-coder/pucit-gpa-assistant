"""Tools that run on the agent's own machine (they never go through the MCP server)."""
import os
import re

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
