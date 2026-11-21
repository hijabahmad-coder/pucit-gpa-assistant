"""Basic input guard. This is a first layer only, NOT a security boundary."""
import re

MAX_INPUT_CHARS = 1000
MAX_REQUESTS_PER_SESSION = 30  # unused since the Streamlit UI was retired

PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|rules)",
    r"(reveal|show|print|repeat).{0,30}(system prompt|instructions|rules)",
    r"you are now",
    r"developer mode",
    r"jailbreak",
    r"disregard",
    # basic Roman Urdu variants
    r"(pichl[ei]|purane|saare|sare) (rules|instructions|hidayat)",
    r"(bhool|ignore) (jao|kar do|karo).{0,30}(rules|instructions)",
]


def check_input(text: str):
    """Returns (ok, message)."""
    if len(text) > MAX_INPUT_CHARS:
        return False, "Message too long. Keep it under 1000 characters."
    low = " ".join(text.lower().split())
    if any(re.search(p, low) for p in PATTERNS):
        return False, "I can only help with GPA/CGPA questions."
    return True, ""
