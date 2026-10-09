import re
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agents import ask
from guards import check_input, MAX_REQUESTS_PER_SESSION
st.set_page_config(page_title="PUCIT GPA Assistant")

# ---------- styling (dark green sidebar, light chat area) ----------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background: #123d33; }
    [data-testid="stSidebar"] * { color: #e8f1ee !important; }
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stDownloadButton > button {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        width: 100%; text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        background: rgba(255,255,255,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

QUICK_ACTIONS = {
    "Calculate GPA": "I want to calculate my semester GPA.",
    "Plan a target CGPA": "I want to reach a target CGPA. Help me plan.",
    "Check course info": "I want to see the courses and credit hours of a semester.",
}


def saved_reports(messages):
    """Reports the agent saved this session, taken from its save_report tool calls (per-session, no server files shared)."""
    out = []
    for m in messages:
        if isinstance(m, AIMessage):
            for call in getattr(m, "tool_calls", None) or []:
                if call.get("name") == "save_report":
                    args = call.get("args", {})
                    base = re.sub(r"[^A-Za-z0-9_\-]", "_", str(args.get("filename", "report")).rsplit(".", 1)[0])[:50] or "report"
                    out.append((base + ".txt", str(args.get("content", ""))))
    return out


# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### GPA Assistant")
    st.caption("Plan, calculate, improve")

    if st.button("New chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("**Quick actions**")
    for label, text in QUICK_ACTIONS.items():
        if st.button(label):
            st.session_state.pending_prompt = text

    reports = saved_reports(st.session_state.messages)
    if reports:
        st.markdown("**Saved reports**")
        for i, (name, content) in enumerate(reports):
            st.download_button(f"{name}", content, file_name=name, mime="text/plain", key=f"dl_{i}")

    left = max(MAX_REQUESTS_PER_SESSION - st.session_state.request_count, 0)
    st.caption(f"Messages left this session: {left}/{MAX_REQUESTS_PER_SESSION}")
    st.caption("Unofficial student project, not affiliated with PUCIT. Verify grades and course data with the official policy.")

# ---------- main ----------
st.title("PUCIT GPA/CGPA Assistant")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "Hi! I'm your GPA assistant. I can:\n"
            "- Convert marks to grade points and calculate your semester GPA\n"
            "- Project your new CGPA after a semester\n"
            "- Find the GPA you need to reach a target CGPA\n"
            "- Show semester courses and remaining credit hours\n\n"
            "Every number comes from a calculation tool, not from the model. "
            "Pick a quick action or just type below."
        )

# show only user messages and final AI replies (skip tool calls/results)
for m in st.session_state.messages:
    if isinstance(m, HumanMessage):
        with st.chat_message("user"):
            st.write(m.content)
    elif isinstance(m, AIMessage) and m.content:
        with st.chat_message("assistant"):
            st.write(m.content)

typed = st.chat_input("e.g. I'm in semester 5, CGPA 3.0, 64 credit hours, want 3.4")
prompt = st.session_state.pending_prompt or typed
st.session_state.pending_prompt = None

if prompt:
    ok, msg = check_input(prompt)
    if not ok:
        st.warning(msg)
        st.stop()
    if st.session_state.request_count >= MAX_REQUESTS_PER_SESSION:
        st.warning("Session limit reached. Please refresh the page to start again.")
        st.stop()

    st.session_state.request_count += 1
    with st.chat_message("user"):
        st.write(prompt)

    history = st.session_state.messages + [HumanMessage(content=prompt)]
    with st.spinner("Thinking..."):
        result = ask(history)

    if result is None:
        st.error("Model failed. Please repeat your message.")
    else:
        st.session_state.messages = result["messages"]
        st.rerun()
