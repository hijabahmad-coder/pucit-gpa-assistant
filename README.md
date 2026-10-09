#  PUCIT GPA/CGPA Assistant

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/hijabahmad-coder/pucit-gpa-assistant/actions/workflows/ci.yml/badge.svg)

A conversational LangChain agent (Groq `gpt-oss-20b`) that answers GPA and CGPA questions for PUCIT BS(CS) students.
**All numbers come from plain-Python tools; the model does no arithmetic.** Runs as a Streamlit web app or in the terminal.

> Unofficial student project, not affiliated with PUCIT. Verify the grade scale, course list and prerequisites against the official policy.

<!-- Add a screenshot: save it as docs/screenshot.png and uncomment -->
<!-- ![Demo](docs/screenshot.png) -->

## Features

- Marks → grade points → semester GPA
- New CGPA after a semester
- Required GPA to hit a target CGPA, with automatic **window widening** (current semester → next semesters) when the target is mathematically unreachable
- **No credit-hour typing:** the agent computes completed and remaining credit hours from the semester you are in
- **Dropped courses:** pass course codes and they are excluded from GPA and completed hours
- **Failed courses:** marks below 50 count as 0.0 grade points, credit hours still count
- **Retakes:** the new grade replaces the old one in CGPA, retake hours are not counted twice
- **Prerequisite check** for a course (e.g. before suggesting a retake)
- Semester course list (semesters 1-8)
- Streamlit UI: welcome card, quick-action buttons, downloadable saved reports, message counter
- Optional text report saving (sandboxed to `reports/`, also downloadable from the sidebar)
- Basic LLM security layer: input guard, tool validation, rate limit, loop cap (see [SECURITY.md](SECURITY.md))

## Examples

**Target CGPA (window widening)**

> I'm in semester 5, CGPA 3.0, I want a 3.4 CGPA.

The agent works out 64 completed credit hours itself, then tests semester 5 alone (needs 4.78, impossible), then 5-6 (4.09, impossible), then 5-7 (**3.86, achievable**) and advises accordingly.

**Retake**

> I failed a course in an earlier semester and I am retaking it now. Old marks were 42.

The agent asks for the course and the new marks, then uses the retake tool so the old grade is replaced instead of double counted.

The agent will not claim that a course is offered in a given semester or state any retake fee. You must check offering and register yourself.

## Tools

All calculations live in `tools.py` as plain Python functions:

| Tool | Purpose |
|---|---|
| `marks_to_grade_points` | Marks (0-100) → grade points |
| `calculate_semester_gpa` | Semester GPA from grade points and credit hours |
| `calculate_new_cgpa` | CGPA after a semester |
| `calculate_new_cgpa_with_retakes` | CGPA when the semester includes retaken courses |
| `required_gpa_for_target` | GPA needed over remaining hours (not capped at 4.0) |
| `get_completed_credit_hours` | Hours completed through a semester, minus dropped course codes |
| `get_remaining_credit_hours` | Hours left, up to a chosen semester (used for window widening) |
| `get_semester_courses` | Course codes, names and credit hours of a semester |
| `check_prerequisites` | Whether the prerequisites of a course are passed |
| `save_report` | Save a `.txt` report (only when you ask) |

Every tool validates its inputs and returns an `Error:` string instead of crashing.

## Quick start

```bash
git clone https://github.com/hijabahmad-coder/pucit-gpa-assistant.git
cd pucit-gpa-assistant
python -m venv .venv
.venv\Scripts\activate                            # Linux/Mac: source .venv/bin/activate
python -m pip install -r requirements.txt
copy .env.example .env                            # Linux/Mac: cp .env.example .env
# put your Groq key in .env:  GROQ_API_KEY=your_key_here
```

Run the web app:

```bash
python -m streamlit run app.py
```

Or the terminal version:

```bash
python agents.py
```

Get a free API key from the [Groq console](https://console.groq.com/).

## Project structure

```
├── app.py            # Streamlit UI
├── .streamlit/       # theme config
├── agents.py         # agent, system prompt, CLI loop
├── tools.py          # GPA/CGPA tools, course data, prerequisites, save_report
├── guards.py         # input guard and limits
├── llm.py            # Groq model setup (key from .env)
├── tests/            # pytest: tool logic + security regressions
├── SECURITY.md       # threat model and known limitations
└── .github/workflows # CI (runs pytest)
```

## Grade scale (as implemented in `tools.py`)

| Marks | GP | Marks | GP |
|---|---|---|---|
| 85+ | 4.0 | 61-64 | 2.3 |
| 80-84 | 3.7 | 58-60 | 2.0 |
| 75-79 | 3.3 | 55-57 | 1.7 |
| 70-74 | 3.0 | 50-54 | 1.0 |
| 65-69 | 2.7 | < 50 | 0.0 |

MD-001 / MD-002 (math deficiency) are non-credit and excluded from GPA. Quran Translation courses count at 0.5 credit hours.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Limitations

- The regex input guard is a basic first layer and can be bypassed.
- Course data, grade scale and the prerequisite map are hard-coded and may not match the latest PUCIT policy. The prerequisite map covers only some courses.
- Elective slots are listed with a default course; your actual electives may differ.
- Retake fees and course offerings are not checked by the tool.
- Replies are model-generated; numbers are tool-generated.

## License

MIT, see [LICENSE](LICENSE).