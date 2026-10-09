"""Plain-Python tools the agent calls. The model never does arithmetic itself."""
import os
import re

REPORT_DIR = "reports"
MAX_REPORT_CHARS = 5000


def marks_to_grade_points(marks: int) -> float:
    """Convert course marks (0-100) into grade points. Use this whenever the student gives marks for a course."""
    if marks < 0 or marks > 100:
        return "Error: marks must be between 0 and 100."
    if marks >= 85:
        return 4.0
    elif marks >= 80:
        return 3.7
    elif marks >= 75:
        return 3.3
    elif marks >= 70:
        return 3.0
    elif marks >= 65:
        return 2.7
    elif marks >= 61:
        return 2.3
    elif marks >= 58:
        return 2.0
    elif marks >= 55:
        return 1.7
    elif marks >= 50:
        return 1.0
    else:
        return 0.0


def calculate_semester_gpa(grade_points: list[float], credit_hours: list[float]) -> float:
    """Calculate semester GPA from lists of grade points and credit hours. Use after converting marks to grade points."""
    if len(grade_points) != len(credit_hours) or not grade_points:
        return "Error: lists must be non-empty and the same length."
    if any(gp < 0 or gp > 4 for gp in grade_points):
        return "Error: grade points must be 0-4."
    if any(ch <= 0 for ch in credit_hours):
        return "Error: credit hours must be positive."
    return sum(g * c for g, c in zip(grade_points, credit_hours)) / sum(credit_hours)


def calculate_new_cgpa(current_cgpa: float, completed_credit_hours: float,
                       semester_gpa: float, semester_credit_hours: float) -> float:
    """Calculate the new CGPA after a semester. Use when the student wants to know their updated CGPA."""
    if not (0 <= current_cgpa <= 4) or not (0 <= semester_gpa <= 4):
        return "Error: CGPA and GPA must be between 0 and 4."
    if completed_credit_hours < 0 or semester_credit_hours < 0:
        return "Error: credit hours cannot be negative."
    total_hours = completed_credit_hours + semester_credit_hours
    if total_hours <= 0:
        return "Error: total credit hours must be positive."
    return (current_cgpa * completed_credit_hours
            + semester_gpa * semester_credit_hours) / total_hours


def required_gpa_for_target(target_cgpa: float, current_cgpa: float,
                            completed_credit_hours: float, remaining_credit_hours: float) -> float:
    """Calculate the GPA needed over the remaining credit hours to reach a target CGPA. Do not cap at 4.0."""
    if not (0 <= target_cgpa <= 4) or not (0 <= current_cgpa <= 4):
        return "Error: CGPA values must be between 0 and 4."
    if completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative."
    if remaining_credit_hours <= 0:
        return "Error: remaining credit hours must be positive."
    return (target_cgpa * (completed_credit_hours + remaining_credit_hours)
            - current_cgpa * completed_credit_hours) / remaining_credit_hours


COURSES = {
    1: [("MS-251", "Probability & Statistics", 3.0),
        ("GE-160", "Applications of ICT", 3.0),
        ("GE-169", "Applied Physics", 3.0),
        ("GE-167", "Discrete Structures", 3.0),
        ("HQ-001", "Quran Translation - I", 0.5),
        ("GE-190", "Functional English", 3.0)],

    2: [("CC-112", "Programming Fundamentals", 3.0),
        ("CC-112-L", "Programming Fundamentals Lab", 1.0),
        ("CC-110", "Digital Logic Design", 2.0),
        ("CC-110-L", "Digital Logic Design Lab", 1.0),
        ("MS-252", "Linear Algebra", 3.0),
        ("GE-191", "Expository Writing", 3.0),
        ("GE-163", "Islamic Studies", 2.0),
        ("HQ-002", "Quran Translation - II", 0.5)],

    3: [("CC-211", "Object Oriented Programming", 3.0),
        ("CC-211-L", "Object Oriented Programming Lab", 1.0),
        ("CC-215", "Database Systems", 3.0),
        ("CC-215-L", "Database Systems Lab", 1.0),
        ("CC-210", "Computer Organization & Assembly Language", 3.0),
        ("GE-162", "Calculus & Analytical Geometry", 3.0),
        ("GE-192", "Introduction to Management", 2.0),
        ("HQ-003", "Quran Translation - III", 0.5)],

    4: [("CC-213", "Data Structures", 3.0),
        ("CC-213-L", "Data Structures Lab", 1.0),
        ("CC-312", "Information Security", 3.0),
        ("CC-214", "Computer Networks", 3.0),
        ("CC-212", "Software Engineering", 3.0),
        ("DC-220", "Advanced Database Management Systems", 3.0),
        ("HQ-004", "Quran Translation - IV", 0.5)],

    5: [("CC-313", "Analysis of Algorithms", 3.0),
        ("CC-310", "Artificial Intelligence", 3.0),
        ("DC-320", "Theory of Automata and Formal Languages", 3.0),
        ("DC-321", "Human Computer Interaction", 3.0),
        ("DC-322", "Computer Architecture", 3.0),
        ("EC-330", "Web Technologies / Elective", 3.0),
        ("HQ-005", "Quran Translation - V", 0.5)],

    6: [("CC-311", "Operating Systems", 3.0),
        ("EC-333", "Mobile Application Development / Elective", 3.0),
        ("EC-324", "Software Construction & Development / Elective", 3.0),
        ("EC-335", "Machine Learning / Elective", 3.0),
        ("EC-334", "Game Design and Development / Elective", 3.0),
        ("MS-253", "Multivariable Calculus", 3.0),
        ("HQ-006", "Quran Translation - VI", 0.5)],

    7: [("CC-411", "Final Year Project - I", 2.0),
        ("DC-328", "Parallel & Distributed Computing", 3.0),
        ("EC-345", "Computer Vision / Elective", 3.0),
        ("EC-425", "Software Quality Engineering / Elective", 3.0),
        ("MS-254", "Technical and Business Writing", 3.0),
        ("GE-263", "Entrepreneurship", 2.0),
        ("GE-262", "Professional Practices", 2.0),
        ("HQ-007", "Quran Translation - VII", 0.5)],

    8: [("CC-412", "Final Year Project - II", 4.0),
        ("DC-421", "Compiler Construction", 3.0),
        ("UE-272", "Introduction to Marketing", 3.0),
        ("GE-168", "Ideology and Constitution of Pakistan", 2.0),
        ("GE-363", "Civics and Community Engagement", 2.0),
        ("HQ-008", "Quran Translation - VIII", 0.5)],
}


def get_semester_courses(semester: int) -> str:
    """Return the courses and credit hours of a semester (1-8). Use when the student asks what courses are in a semester."""
    if semester < 1 or semester > 8:
        return "Error: semester must be between 1 and 8."
    lines = []
    for code, name, credit in COURSES[semester]:
        lines.append(f"{code} - {name} ({credit})")
    return "\n".join(lines)


def get_remaining_credit_hours(current_semester: int, through_semester: int = 8) -> float:
    """Return the total credit hours of the semesters AFTER current_semester, up to and including through_semester (default 8 = the end of the degree). Use this when the student wants to know remaining credit hours, or to test a window of semesters when a target is unreachable."""
    if current_semester < 1 or current_semester > 8:
        return "Error: semester must be between 1 and 8."
    if through_semester < current_semester or through_semester > 8:
        return "Error: through_semester must be between current_semester and 8."
    total = 0.0
    for sem in range(current_semester + 1, through_semester + 1):
        for _code, _name, credit in COURSES[sem]:
            total += credit
    return total


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
