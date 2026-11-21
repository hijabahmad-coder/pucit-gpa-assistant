"""MCP server: exposes the GPA/CGPA tools over HTTP. save_report stays on the agent side."""
import os

from fastmcp import FastMCP

from tools import (
    marks_to_grade_points, calculate_semester_gpa, calculate_new_cgpa,
    required_gpa_for_target, get_semester_courses, get_remaining_credit_hours,
    get_completed_credit_hours, calculate_new_cgpa_with_retakes, check_prerequisites,
)

mcp = FastMCP("cgpa")

for fn in (marks_to_grade_points, calculate_semester_gpa, calculate_new_cgpa,
           required_gpa_for_target, get_semester_courses, get_remaining_credit_hours,
           get_completed_credit_hours, calculate_new_cgpa_with_retakes, check_prerequisites):
    mcp.tool(fn)  # docstring + type hints become the tool description

if __name__ == "__main__":
    # PORT is set by hosts like Render; locally it serves at http://127.0.0.1:8000/mcp
    mcp.run(transport="http", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
