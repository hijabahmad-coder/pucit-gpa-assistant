# 🎓 PUCIT GPA/CGPA Assistant

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/YOUR_USERNAME/pucit-gpa-assistant/actions/workflows/ci.yml/badge.svg)

A conversational LangChain agent (Groq `gpt-oss-20b`) that answers GPA and CGPA questions for PUCIT BS(CS) students.
**All numbers come from plain-Python tools; the model does no arithmetic.** Runs as a Streamlit web app or in the terminal.

> Unofficial student project, not affiliated with PUCIT. Verify the grade scale and course list against the official policy.

<!-- Add a screenshot: save it as docs/screenshot.png and uncomment -->
<!-- ![Demo](docs/screenshot.png) -->

## Features

- Marks → grade points → semester GPA
- New CGPA after a semester
- Required GPA to hit a target CGPA, with automatic **window widening** (current semester → next semesters) when the target is mathematically unreachable
- Semester course list and remaining credit hours (semesters 1–8)
- Streamlit UI: welcome card, quick-action buttons, downloadable saved reports, message counter
- Optional text report saving (sandboxed to `reports/`, also downloadable from the sidebar)
- Basic LLM security layer: input guard, tool validation, rate limit, loop cap (see [SECURITY.md](SECURITY.md))

## Example

> I'm in semester 5, CGPA 3.0, 64 credit hours completed, I want a 3.4 CGPA.

The agent tests semester 5 alone (needs 4.78, impossible), then 5–6 (4.09, impossible), then 5–7 (**3.86, achievable**) and advises accordingly.

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/pucit-gpa-assistant.git
cd pucit-gpa-assistant
python -m venv .venv && .venv\Scripts\activate    # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                            # Linux/Mac: cp .env.example .env
# put your Groq key in .env:  GROQ_API_KEY=your_key_here
```

Run the web app:

```bash
streamlit run app.py
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
├── tools.py          # GPA/CGPA tools + course data + save_report
├── guards.py         # input guard and limits
├── llm.py            # Groq model setup (key from .env)
├── tests/            # pytest: tool logic + security regressions
├── SECURITY.md       # threat model and known limitations
└── .github/workflows # CI (runs pytest)
```

## Grade scale (as implemented in `tools.py`)

| Marks | GP | Marks | GP |
|---|---|---|---|
| 85+ | 4.0 | 61–64 | 2.3 |
| 80–84 | 3.7 | 58–60 | 2.0 |
| 75–79 | 3.3 | 55–57 | 1.7 |
| 70–74 | 3.0 | 50–54 | 1.0 |
| 65–69 | 2.7 | < 50 | 0.0 |

MD-001 / MD-002 (math deficiency) are non-credit and excluded from GPA.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Limitations

- The regex input guard is a basic first layer and can be bypassed.
- Course data and grade scale are hard-coded; they may change with PUCIT policy.
- Replies are model-generated; numbers are tool-generated.

## License

MIT, see [LICENSE](LICENSE).
