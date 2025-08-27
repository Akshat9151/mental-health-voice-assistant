# services/safety_guard.py
import re
from typing import Literal, Tuple, List

Risk = Literal["none", "low", "medium", "high"]
Category = Literal["suicide", "self_harm", "violence", "abuse", "unknown"]

SUICIDE_PATTERNS = [
    r"\b(end (my|this) life\b)",
    r"\b(kill myself|suicide|take my life)\b",
    r"\b(i (don'?t|do not) want to live)\b",
    r"\bmujhe (jeena|jeene) nahi (hai|h)\b",
    r"\bapni zindagi (khatam|khatm) (karna|krna) (chahta|chahti) hu\b",
    r"\bmar (ja(?:u|na)|jana|jaunga|jaungi)\b",
]

SELF_HARM_PATTERNS = [
    r"\b(self[- ]?harm|cut(ting)? myself)\b",
    r"\bkhud ko nuksan (pahu(?:n|)chana|pahunchana)\b",
]

VIOLENCE_PATTERNS = [
    r"\b(kill|hurt) (him|her|them|someone)\b",
    r"\buse (a )?weapon\b",
    r"\bmaine kisi ko maar (diya|dunga|dungi)\b",
]

ABUSE_PATTERNS = [
    r"\b(domestic abuse|violence at home)\b",
    r"\bmujhe (maar(a|te)|dhakka|torture) (ja|diya) raha\b",
]

LOW_RISK_PATTERNS = [
    r"\b(kill me) (as joke|lol|jk)\b",
    r"\b(this job is killing me)\b",
]

COMPILED = [
    ("suicide", [re.compile(p, re.I) for p in SUICIDE_PATTERNS]),
    ("self_harm", [re.compile(p, re.I) for p in SELF_HARM_PATTERNS]),
    ("violence", [re.compile(p, re.I) for p in VIOLENCE_PATTERNS]),
    ("abuse", [re.compile(p, re.I) for p in ABUSE_PATTERNS]),
]
LOW_COMPILED = [re.compile(p, re.I) for p in LOW_RISK_PATTERNS]

def assess_risk(text: str) -> Tuple[Risk, Category, List[str]]:
    if not text:
        return "none", "unknown", []
    for pat in LOW_COMPILED:
        if pat.search(text):
            return "low", "unknown", [pat.pattern]
    matches: List[str] = []
    for category, regs in COMPILED:
        for r in regs:
            if r.search(text):
                matches.append(r.pattern)
                if category in ("suicide", "self_harm"):
                    return "high", category, matches
                if category in ("violence", "abuse"):
                    return "medium", category, matches
    return "none", "unknown", []

def crisis_response(locale: str = "IN") -> str:
    if locale.upper() == "IN":
        helplines = (
            "• 🇮🇳 Kiran Helpline (24x7): 1800-599-0019\n"
            "• AASRA Helpline: +91-9820466726\n"
            "• If you’re in immediate danger, please call 112."
        )
    else:
        helplines = (
            "• If you're in immediate danger, call your local emergency number.\n"
            "• Suicide & Crisis Lifeline (US): 988\n"
            "• Samaritans (UK & ROI): 116 123"
        )
    return (
        "I’m really sorry you’re feeling this way. Your safety matters a lot.\n\n"
        "I can’t provide emergency help, but you’re not alone. "
        "Please consider reaching out to someone you trust nearby, "
        "and contact a professional right now:\n"
        f"{helplines}\n\n"
        "Would you like me to share a short grounding exercise while you arrange help?"
    )
