# services/safety_guard.py
import re
from typing import Literal, Tuple, List, Dict
from datetime import datetime

Risk = Literal["none", "low", "medium", "high"]
Category = Literal["suicide", "self_harm", "violence", "abuse", "substance", "eating_disorder", "unknown"]

# Enhanced suicide detection with Indian expressions
SUICIDE_PATTERNS = [
    r"\b(end (my|this) life\b)",
    r"\b(kill myself|suicide|take my life)\b",
    r"\b(i (don'?t|do not) want to live)\b",
    r"\b(want to die|wish i was dead)\b",
    r"\b(better off dead|no point living)\b",
    
    # Hindi/Hinglish patterns
    r"\bmujhe (jeena|jeene) nahi (hai|h)\b",
    r"\bapni zindagi (khatam|khatm) (karna|krna) (chahta|chahti) hu\b",
    r"\bmar (ja(?:u|na)|jana|jaunga|jaungi)\b",
    r"\bmaut (aa|aaye) jaye\b",
    r"\bzinda nahi (rehna|raha) chahta\b",
    r"\b(suicide|aatmahatya) kar(na|unga|ungi)\b",
    r"\bkhud ko (maar|khatam) (dena|karna)\b",
    r"\bzindagi se (thak|tang) gaya\b",
    r"\bbas ab nahi (rehna|jeena)\b",
    r"\bmujhe (maut|marna) chahiye\b",
    
    # Cultural expressions
    r"\bduniya se (ja|chala) jana\b",
    r"\bsab kuch (khatam|over) kar dena\b",
    r"\bapne haathon (maut|end) kar\b",
    r"\bzindagi ka (bojh|burden) nahi\b"
]

SELF_HARM_PATTERNS = [
    r"\b(self[- ]?harm|cut(ting)? myself)\b",
    r"\b(hurt myself|harm myself)\b",
    r"\b(cutting|scratching|burning) myself\b",
    r"\bwant to hurt myself\b",
    
    # Hindi/Hinglish patterns
    r"\bkhud ko nuksan (pahu(?:n|)chana|pahunchana)\b",
    r"\bapne (haath|body) ko (cut|kata|nuksan)\b",
    r"\bkhud ko (maarna|hurt|pain)\b",
    r"\b(blade|razor) se (cut|kata)\b",
    r"\bapni (skin|body) ko (scratch|cut)\b",
    r"\bkhud pe (gussa|anger) nikalna\b"
]

VIOLENCE_PATTERNS = [
    r"\b(kill|hurt) (him|her|them|someone)\b",
    r"\buse (a )?weapon\b",
    r"\b(murder|violence) kar\b",
    r"\bsomeone (deserves to|should) die\b",
    
    # Hindi/Hinglish patterns
    r"\bmaine kisi ko maar (diya|dunga|dungi)\b",
    r"\b(weapon|hatiyar) use kar\b",
    r"\bkisi ko (maar|kill|hurt) (dena|karna)\b",
    r"\bgusse mein kuch (galat|bura) kar\b",
    r"\bviolence karna (padega|hai)\b"
]

ABUSE_PATTERNS = [
    r"\b(domestic abuse|violence at home)\b",
    r"\b(physical abuse|sexual abuse)\b",
    r"\bsomeone is (hitting|hurting|abusing) me\b",
    
    # Hindi/Hinglish patterns
    r"\bmujhe (maar(a|te)|dhakka|torture) (ja|diya) raha\b",
    r"\bghar mein (violence|maar-peet)\b",
    r"\bkoi mujhe (abuse|torture|hurt) kar raha\b",
    r"\b(domestic violence|ghar ki hinsa)\b",
    r"\bmujhpe (haath|violence) uthaya\b",
    r"\bfamily (abuse|violence|maar-peet)\b"
]

# Additional categories for comprehensive mental health support
SUBSTANCE_PATTERNS = [
    r"\b(overdose|too many pills)\b",
    r"\b(drugs|alcohol) to (end|stop|numb)\b",
    r"\bdrinking to (forget|die)\b",
    
    # Hindi/Hinglish patterns
    r"\b(nasha|drugs|alcohol) se (bhagana|escape)\b",
    r"\b(pills|medicine) zyada (khana|lena)\b",
    r"\b(daaru|sharab) mein (dubana|doobna)\b"
]

EATING_DISORDER_PATTERNS = [
    r"\b(starving myself|not eating)\b",
    r"\b(throwing up|purging) after eating\b",
    r"\bhate (my body|how i look)\b",
    
    # Hindi/Hinglish patterns
    r"\bkhana (band|chhod) diya\b",
    r"\b(vomit|ulti) kar deta hun khane ke baad\b",
    r"\bmera (body|figure) pasand nahi\b"
]

LOW_RISK_PATTERNS = [
    r"\b(kill me) (as joke|lol|jk|haha)\b",
    r"\b(this job is killing me)\b",
    r"\b(traffic|exam|work) will kill me\b",
    r"\b(killing time|bored to death)\b",
    
    # Hindi/Hinglish patterns
    r"\b(mazak|joke) mein (mar|kill)\b",
    r"\b(exam|work) se (mar|kill) jaaunga\b"
]

COMPILED = [
    ("suicide", [re.compile(p, re.I) for p in SUICIDE_PATTERNS]),
    ("self_harm", [re.compile(p, re.I) for p in SELF_HARM_PATTERNS]),
    ("violence", [re.compile(p, re.I) for p in VIOLENCE_PATTERNS]),
    ("abuse", [re.compile(p, re.I) for p in ABUSE_PATTERNS]),
    ("substance", [re.compile(p, re.I) for p in SUBSTANCE_PATTERNS]),
    ("eating_disorder", [re.compile(p, re.I) for p in EATING_DISORDER_PATTERNS]),
]
LOW_COMPILED = [re.compile(p, re.I) for p in LOW_RISK_PATTERNS]

# Risk assessment history for pattern tracking
risk_history: List[Dict] = []

def assess_risk(text: str) -> Tuple[Risk, Category, List[str]]:
    """Enhanced risk assessment with better categorization"""
    if not text:
        return "none", "unknown", []
    
    # Check for low-risk patterns first (jokes, metaphors)
    for pat in LOW_COMPILED:
        if pat.search(text):
            return "low", "unknown", [pat.pattern]
    
    matches: List[str] = []
    highest_risk = "none"
    risk_category = "unknown"
    
    for category, regs in COMPILED:
        for r in regs:
            match = r.search(text)
            if match:
                matches.append(r.pattern)
                
                # Determine risk level based on category
                if category == "suicide":
                    highest_risk = "high"
                    risk_category = category
                elif category == "self_harm" and highest_risk != "high":
                    highest_risk = "high"
                    risk_category = category
                elif category in ("violence", "abuse") and highest_risk not in ("high",):
                    highest_risk = "medium"
                    risk_category = category
                elif category in ("substance", "eating_disorder") and highest_risk == "none":
                    highest_risk = "medium"
                    risk_category = category
    
    # Store in history for pattern analysis
    if highest_risk != "none":
        risk_entry = {
            "text": text,
            "risk": highest_risk,
            "category": risk_category,
            "patterns": matches,
            "timestamp": datetime.now().isoformat()
        }
        risk_history.append(risk_entry)
        if len(risk_history) > 100:  # Keep last 100 entries
            risk_history[:] = risk_history[-100:]
    
    return highest_risk, risk_category, matches

def get_risk_trends() -> Dict:
    """Analyze risk patterns over time"""
    if len(risk_history) < 3:
        return {"status": "insufficient_data"}
    
    recent_risks = risk_history[-10:]  # Last 10 risk events
    high_risk_count = sum(1 for r in recent_risks if r["risk"] == "high")
    medium_risk_count = sum(1 for r in recent_risks if r["risk"] == "medium")
    
    return {
        "total_recent_risks": len(recent_risks),
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "escalating": high_risk_count >= 2,
        "categories": list(set(r["category"] for r in recent_risks))
    }

def crisis_response(locale: str = "IN", category: str = "unknown") -> str:
    """Enhanced crisis response with category-specific guidance"""
    
    # Base helplines based on locale
    if locale.upper() == "IN":
        base_helplines = (
            "• 🇮🇳 Kiran Mental Health Helpline (24x7): 1800-599-0019\n"
            "• AASRA Mumbai: +91-9820466726\n"
            "• Vandrevala Foundation: 1860-2662-345\n"
            "• Sneha Chennai: +91-44-2464-0050\n"
            "• Parivarthan Bangalore: +91-76766-02602\n"
            "• Emergency Services: 112"
        )
        
        # Category-specific helplines for India
        if category == "abuse":
            specific_helplines = (
                "• Women Helpline: 181\n"
                "• Domestic Violence Helpline: 1091\n"
                "• Child Helpline: 1098\n"
            )
        elif category == "substance":
            specific_helplines = (
                "• NIMHANS De-addiction Centre: +91-80-2699-5130\n"
                "• All India Institute of Medical Sciences: +91-11-2659-3677\n"
            )
        else:
            specific_helplines = ""
            
    else:
        base_helplines = (
            "• Suicide & Crisis Lifeline (US): 988\n"
            "• Samaritans (UK & ROI): 116 123\n"
            "• Crisis Text Line: Text HOME to 741741\n"
            "• International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
        )
        specific_helplines = ""
    
    # Category-specific responses
    if category == "suicide":
        opening = (
            "I'm deeply concerned about what you're going through. Your life has value, and you matter. 💙\n\n"
            "These thoughts can feel overwhelming, but they are temporary. You don't have to face this alone."
        )
    elif category == "self_harm":
        opening = (
            "I understand you're in pain right now. Self-harm might feel like relief, but there are safer ways to cope. 💙\n\n"
            "You deserve care and support, not harm."
        )
    elif category == "abuse":
        opening = (
            "I'm sorry you're experiencing this. What you're going through isn't okay, and it's not your fault. 💙\n\n"
            "Your safety is the priority. You deserve to be treated with respect and kindness."
        )
    elif category == "substance":
        opening = (
            "Struggling with substances is incredibly difficult. You're brave for recognizing this. 💙\n\n"
            "Recovery is possible, and you don't have to do this alone."
        )
    else:
        opening = (
            "I'm really sorry you're feeling this way. Your safety and well-being matter deeply to me. 💙\n\n"
            "You don't have to go through this alone."
        )
    
    # Immediate safety guidance
    safety_guidance = (
        "Right now, please:\n"
        "1. Stay with someone you trust, or call a friend/family member\n"
        "2. Remove any means of harm from your immediate area\n"
        "3. Focus on your breathing - you are safe in this moment\n\n"
    )
    
    # Professional help section
    help_section = (
        "Please reach out to professional support immediately:\n"
        f"{specific_helplines}"
        f"{base_helplines}\n\n"
    )
    
    # Grounding offer
    grounding_offer = (
        "While you arrange help, would you like me to guide you through a grounding exercise? "
        "Sometimes focusing on the present moment can help when everything feels overwhelming."
    )
    
    return f"{opening}\n\n{safety_guidance}{help_section}{grounding_offer}"

def provide_grounding_exercise() -> str:
    """Provide a grounding exercise for crisis situations"""
    exercises = [
        (
            "Let's try the 5-4-3-2-1 grounding technique together:\n\n"
            "• Name 5 things you can SEE around you\n"
            "• Name 4 things you can TOUCH\n"
            "• Name 3 things you can HEAR\n"
            "• Name 2 things you can SMELL\n"
            "• Name 1 thing you can TASTE\n\n"
            "Take your time with each step. You're doing great. 🤗"
        ),
        (
            "Let's focus on breathing together:\n\n"
            "• Breathe in slowly for 4 counts... 1, 2, 3, 4\n"
            "• Hold your breath for 4 counts... 1, 2, 3, 4\n"
            "• Breathe out slowly for 6 counts... 1, 2, 3, 4, 5, 6\n\n"
            "Repeat this 3 more times. You're safe. You're doing well. 💙"
        ),
        (
            "Let's ground yourself physically:\n\n"
            "• Feel your feet on the floor\n"
            "• Press your hands together and feel the pressure\n"
            "• Hold something cool (ice cube, cold water)\n"
            "• Say out loud: 'I am [your name], I am in [location], today is [date]'\n\n"
            "You are here, you are present, you are safe right now. 🤗"
        )
    ]
    
    return random.choice(exercises)

def get_safety_resources(locale: str = "IN") -> Dict[str, List[str]]:
    """Get comprehensive safety resources"""
    if locale.upper() == "IN":
        return {
            "crisis_helplines": [
                "Kiran Mental Health: 1800-599-0019",
                "AASRA Mumbai: +91-9820466726",
                "Vandrevala Foundation: 1860-2662-345",
                "Sneha Chennai: +91-44-2464-0050"
            ],
            "specialized_support": [
                "Women Helpline: 181",
                "Child Helpline: 1098",
                "Elder Helpline: 14567",
                "Domestic Violence: 1091"
            ],
            "online_resources": [
                "https://www.nimhans.ac.in/",
                "https://www.manthanhub.org/",
                "https://www.thelivelovelaughfoundation.org/"
            ]
        }
    else:
        return {
            "crisis_helplines": [
                "Suicide & Crisis Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "Samaritans: 116 123"
            ],
            "online_resources": [
                "https://suicidepreventionlifeline.org/",
                "https://www.crisistextline.org/",
                "https://www.samaritans.org/"
            ]
        }
