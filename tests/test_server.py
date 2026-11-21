from fastmcp import Client
from server import mcp


async def test_lists_nine_tools_and_hides_save_report():
    async with Client(mcp) as c:
        names = {t.name for t in await c.list_tools()}
    assert len(names) == 9 and "save_report" not in names


async def test_remaining_hours_window():
    async with Client(mcp) as c:
        r = await c.call_tool("get_remaining_credit_hours", {"current_semester": 4, "through_semester": 6})
    assert r.data == 37.0


async def test_error_string_does_not_break_schema():
    async with Client(mcp) as c:
        r = await c.call_tool("marks_to_grade_points", {"marks": 150})
    assert str(r.data).startswith("Error")
