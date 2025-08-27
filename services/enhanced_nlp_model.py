# services/enhanced_nlp_model.py
import os
import re
import random
from typing import Optional, Dict, List
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from datetime import datetime

# Configuration
try:
    from config import MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE, TOP_P, TOP_K, REPETITION_PENALTY
except Exception:
    MODEL_NAME = os.getenv("NLP_MODEL_NAME", "microsoft/DialoGPT-medium")
    MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "160"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P = float(os.getenv("TOP_P", "0.92"))
    TOP_K = int(os.getenv("TOP_K", "50"))
    REPETITION_PENALTY = float(os.getenv("REPETITION_PENALTY", "1.15"))

FALLBACK_MODEL = "distilgpt2"

def _load_pipeline(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(model_name)
    gen = pipeline("text-generation", model=mdl, tokenizer=tok)
    return gen, tok

try:
    generator, tokenizer = _load_pipeline(MODEL_NAME)
except Exception:
    generator, tokenizer = _load_pipeline(FALLBACK_MODEL)

# Enhanced system prompt with cultural sensitivity
SYSTEM_STYLE = (
    "You are a compassionate, culturally-aware mental health voice assistant designed for Indian users. "
    "You understand Hindi, English, and Hinglish expressions. Be warm, empathetic, and non-judgmental. "
    "Respect Indian cultural values, family dynamics, and social contexts. "
    "Avoid medical diagnosis or prescriptions. Encourage reflection, offer gentle coping strategies, "
    "and suggest professional help when needed. Keep responses under 4 sentences and culturally appropriate."
)

# Emotion-specific response templates with Indian cultural context
EMOTION_RESPONSES = {
    "happy": {
        "acknowledgments": [
            "That's wonderful to hear! 😊",
            "Bahut achhi baat hai! I'm so glad you're feeling good.",
            "Your happiness is contagious! 🌟",
            "Khushi ki baat hai! It's beautiful to see you so positive.",
            "That's fantastic! Your joy makes my day brighter."
        ],
        "follow_ups": [
            "What's making you feel so happy today?",
            "Would you like to share what brought this joy?",
            "Kya khaas baat hai jo aapko itna khush kar rahi hai?",
            "It's great to celebrate these moments. What's the special reason?"
        ],
        "encouragements": [
            "Hold onto this feeling - you deserve all this happiness!",
            "These moments of joy are precious. Cherish them! ✨",
            "Yeh khushi aapke chehre par hamesha rahe!",
            "May this happiness stay with you for a long time!"
        ]
    },
    
    "sad": {
        "acknowledgments": [
            "I hear you, and I'm here with you. 💙",
            "Main samajh sakta hun. It's okay to feel this way.",
            "Your feelings are valid. I'm here to listen.",
            "Dil mein jo bhari hai, share kar sakte hain.",
            "It takes courage to express sadness. Thank you for trusting me."
        ],
        "comfort": [
            "You don't have to go through this alone.",
            "Mushkil waqt hai, lekin yeh guzar jaayega.",
            "These feelings are temporary, even when they feel overwhelming.",
            "Har raat ke baad subah hoti hai. This too shall pass.",
            "I'm here to support you through this difficult time."
        ],
        "gentle_questions": [
            "Would you like to share what's weighing on your heart?",
            "Kya aap batana chahenge ki kya pareshaan kar raha hai?",
            "Sometimes talking helps. What's been on your mind?",
            "Is there something specific that's making you feel low?"
        ]
    },
    
    "angry": {
        "acknowledgments": [
            "I can sense your frustration. It's understandable. 😔",
            "Gussa aana bilkul natural hai. Let's work through this.",
            "Your anger is valid. Let's find a way to process it.",
            "Main samajh raha hun aap kitna irritate feel kar rahe hain.",
            "It's okay to feel angry. These emotions need space too."
        ],
        "calming": [
            "Let's take a deep breath together. Inhale... exhale...",
            "Ek gehri saans lete hain. You're safe here.",
            "Anger is energy - let's channel it constructively.",
            "Thoda sa pause lete hain. I'm here with you.",
            "Your feelings matter. Let's process this step by step."
        ],
        "questions": [
            "What triggered this anger? Can you tell me more?",
            "Kya hua tha jo aapko itna gussa aa gaya?",
            "Would sharing the situation help you feel lighter?",
            "Sometimes anger hides other emotions. What else are you feeling?"
        ]
    },
    
    "anxious": {
        "acknowledgments": [
            "Anxiety can be really overwhelming. I'm here with you. 🤗",
            "Tension ho rahi hai, I understand. You're not alone.",
            "These worried thoughts are exhausting. I hear you.",
            "Ghabrahat normal hai, especially in uncertain times.",
            "Your anxiety is real and valid. Let's face it together."
        ],
        "grounding": [
            "Let's focus on your breathing. Feel your feet on the ground.",
            "Abhi is moment mein hain hum. You're safe right now.",
            "Name 5 things you can see around you. This can help ground you.",
            "Yahan, abhi, is waqt - you are okay.",
            "Let's bring your attention to the present moment."
        ],
        "support": [
            "What's your biggest worry right now?",
            "Sabse zyada kya chinta ho rahi hai?",
            "Would it help to break down what's making you anxious?",
            "Sometimes our minds create bigger problems than reality. Let's examine this together."
        ]
    },
    
    "lonely": {
        "acknowledgments": [
            "Loneliness can feel so heavy. I'm here with you now. 💙",
            "Akela feel karna bahut painful hai. You're not alone.",
            "I hear the loneliness in your words. It's real and it hurts.",
            "Tanhaai ka ehsaas samajh aata hai. I'm here to listen.",
            "Connection is a basic human need. Your feelings make complete sense."
        ],
        "connection": [
            "Even in loneliness, you reached out. That shows strength.",
            "Aap yahan hain, main yahan hun. We're connected right now.",
            "Would you like to talk about what makes you feel most alone?",
            "Sometimes loneliness is about quality, not quantity of connections.",
            "Your presence matters. You matter."
        ]
    },
    
    "overwhelmed": {
        "acknowledgments": [
            "Feeling overwhelmed is like carrying too much weight. I see you. 💪",
            "Bahut zyada pressure lag raha hai, I understand.",
            "When everything feels too much, it's okay to pause.",
            "Overwhelm is your system saying 'slow down' - and that's wise.",
            "You're juggling so much. No wonder you feel this way."
        ],
        "support": [
            "Let's break things down into smaller, manageable pieces.",
            "Ek ek karke dekhte hain. What needs immediate attention?",
            "What's the most important thing on your mind right now?",
            "Sometimes we need to put some balls down while juggling. What can wait?"
        ]
    },
    
    "grateful": {
        "acknowledgments": [
            "Gratitude is such a beautiful feeling! ✨",
            "Shukr ka ehsaas kitna achha hai! Thank you for sharing.",
            "Your appreciation warms my heart. 💖",
            "Grateful hearts are magnetic to more good things!",
            "This thankfulness shows your beautiful perspective on life."
        ],
        "amplification": [
            "What are you most grateful for right now?",
            "Kiske liye sabse zyada thankful feel kar rahe hain?",
            "Gratitude has a way of multiplying joy. Tell me more!",
            "These moments of appreciation are so precious."
        ]
    },
    
    "confused": {
        "acknowledgments": [
            "Confusion can be really unsettling. Let's untangle this together. 🤔",
            "Samajh nahi aa raha, bilkul normal hai. I'm here to help.",
            "When things feel unclear, it's okay to sit with the uncertainty.",
            "Confusion often comes before clarity. You're in process.",
            "Mixed feelings are completely human. Let's sort through them."
        ],
        "clarification": [
            "What's the main thing that's confusing you?",
            "Sabse zyada kya confuse kar raha hai?",
            "Would it help to talk through what you're thinking?",
            "Sometimes speaking confusion out loud helps organize thoughts."
        ]
    }
}

# Cultural context and family dynamics awareness
CULTURAL_CONTEXTS = {
    "family_pressure": [
        "Family expectations can be really heavy sometimes.",
        "Ghar waalon ka pressure samajh aata hai. It's challenging.",
        "Balancing family wishes with personal needs is tough.",
        "Indian families love deeply but sometimes that comes with pressure."
    ],
    "career_stress": [
        "Career pressure in today's world is immense.",
        "Job market ki tension bilkul real hai.",
        "Professional life balance karna mushkil hai sometimes.",
        "Your career concerns are completely valid in today's competitive world."
    ],
    "relationship_issues": [
        "Relationships can be complex, especially with cultural expectations.",
        "Rishton mein complications hoti rehti hain.",
        "Love and family approval don't always align easily.",
        "Emotional connections need understanding and patience."
    ],
    "social_expectations": [
        "Society ki expectations ka pressure samajh aata hai.",
        "Log kya kahenge - this worry is so common and understandable.",
        "Social norms can sometimes conflict with personal happiness.",
        "Your individual journey matters more than others' opinions."
    ]
}

# Indian coping strategies and wisdom
COPING_STRATEGIES = {
    "breathing": [
        "Try the 4-7-8 breathing: Inhale for 4, hold for 7, exhale for 8.",
        "Pranayama jaisa simple breathing exercise kar sakte hain.",
        "Deep belly breathing - haath pet par rakh kar try kariye.",
        "Box breathing: 4 counts in, hold 4, out 4, hold 4."
    ],
    "grounding": [
        "5-4-3-2-1 technique: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
        "Zameen par pair firmly rakh kar feel kariye - you're grounded.",
        "Hold something cool in your hands - ice cube or cold water.",
        "Name your current location out loud to anchor yourself."
    ],
    "mindfulness": [
        "Just for 2 minutes, focus only on your breath.",
        "Abhi is moment mein hain - past ya future nahi.",
        "Notice thoughts like clouds passing - don't grab them.",
        "Mindful walking - har step ko feel kariye."
    ],
    "self_compassion": [
        "Talk to yourself like you would to your best friend.",
        "Apne saath utna hi kind rahiye jitna dusron ke saath hain.",
        "Mistakes are human - self-forgiveness is healing.",
        "You're doing the best you can with what you have right now."
    ]
}

def get_emotion_specific_response(emotion: str, intensity: str = "medium") -> Dict[str, List[str]]:
    """Get appropriate responses based on emotion and intensity"""
    if emotion not in EMOTION_RESPONSES:
        emotion = "neutral"
    
    responses = EMOTION_RESPONSES.get(emotion, {})
    
    # Adjust responses based on intensity
    if intensity == "high":
        # For high intensity, use more urgent/immediate responses
        if emotion == "sad":
            responses["acknowledgments"] = [
                "I can hear the deep pain in your words. I'm right here with you. 💙",
                "This sounds incredibly difficult. You don't have to face this alone.",
                "Main samajh raha hun kitna mushkil waqt hai. I'm here."
            ]
        elif emotion == "angry":
            responses["calming"] = [
                "This anger feels really intense. Let's breathe together right now.",
                "I can feel how frustrated you are. Let's find a safe way to release this.",
                "Bohot zyada gussa aa raha hai. Let's pause and breathe."
            ]
    
    return responses

def detect_cultural_context(text: str) -> List[str]:
    """Detect cultural context clues in the text"""
    text_lower = text.lower()
    contexts = []
    
    family_keywords = ["family", "parents", "ghar wale", "mummy", "papa", "relatives", "rishta", "shaadi"]
    career_keywords = ["job", "work", "career", "office", "boss", "salary", "promotion", "naukri"]
    relationship_keywords = ["boyfriend", "girlfriend", "love", "breakup", "relationship", "pyaar"]
    social_keywords = ["society", "log", "friends", "social media", "comparison", "status"]
    
    if any(keyword in text_lower for keyword in family_keywords):
        contexts.append("family_pressure")
    if any(keyword in text_lower for keyword in career_keywords):
        contexts.append("career_stress")
    if any(keyword in text_lower for keyword in relationship_keywords):
        contexts.append("relationship_issues")
    if any(keyword in text_lower for keyword in social_keywords):
        contexts.append("social_expectations")
    
    return contexts

def generate_culturally_aware_response(user_text: str, emotion: str, contexts: List[str], intensity: str) -> str:
    """Generate response considering cultural context"""
    emotion_responses = get_emotion_specific_response(emotion, intensity)
    
    response_parts = []
    
    # Start with emotion acknowledgment
    if "acknowledgments" in emotion_responses:
        response_parts.append(random.choice(emotion_responses["acknowledgments"]))
    
    # Add cultural context awareness
    for context in contexts[:1]:  # Use first context to keep response concise
        if context in CULTURAL_CONTEXTS:
            response_parts.append(random.choice(CULTURAL_CONTEXTS[context]))
    
    # Add supportive follow-up based on emotion
    if emotion in ["sad", "anxious", "overwhelmed"] and "support" in emotion_responses:
        response_parts.append(random.choice(emotion_responses["support"]))
    elif emotion in ["happy", "grateful"] and "follow_ups" in emotion_responses:
        response_parts.append(random.choice(emotion_responses["follow_ups"]))
    
    # Suggest coping strategy for negative emotions
    if emotion in ["anxious", "angry", "overwhelmed"] and intensity in ["medium", "high"]:
        if emotion == "anxious":
            strategy = random.choice(COPING_STRATEGIES["breathing"])
        elif emotion == "angry":
            strategy = random.choice(COPING_STRATEGIES["grounding"])
        elif emotion == "overwhelmed":
            strategy = random.choice(COPING_STRATEGIES["mindfulness"])
        else:
            strategy = random.choice(COPING_STRATEGIES["self_compassion"])
        
        response_parts.append(f"Try this: {strategy}")
    
    # Combine response parts
    response = " ".join(response_parts)
    
    # Ensure response isn't too long
    if len(response) > 300:
        response = response[:297] + "..."
    
    return response

def _build_enhanced_prompt(user_text: str, context: Optional[str], emotion: str, emotion_data: Dict) -> str:
    """Build enhanced prompt with emotion and cultural awareness"""
    ctx = (context or "").strip()
    
    # Detect cultural contexts
    cultural_contexts = detect_cultural_context(user_text)
    intensity = emotion_data.get("intensity", "medium")
    
    # Build context-aware system prompt
    enhanced_system = SYSTEM_STYLE
    if cultural_contexts:
        enhanced_system += f" The user seems to be dealing with {', '.join(cultural_contexts)}."
    if intensity == "high":
        enhanced_system += " The user's emotional state seems intense - be extra supportive."
    
    # Few-shot examples based on emotion
    few_shots = []
    if emotion == "sad":
        few_shots = [
            ("User: I'm feeling really depressed and low today.\nAssistant:",
             "I hear you, and I'm here with you. 💙 Depression can feel so heavy. Would you like to share what's weighing on your heart?"),
            ("User: Bahut udaas feel kar raha hun, kuch achha nahi lag raha.\nAssistant:",
             "Main samajh sakta hun. Udaasi ka ehsaas bahut painful hai. Kya aap batana chahenge ki kya pareshaan kar raha hai?")
        ]
    elif emotion == "anxious":
        few_shots = [
            ("User: I'm so worried about everything, can't stop thinking.\nAssistant:",
             "Anxiety can be really overwhelming. Let's focus on your breathing for a moment. What's your biggest worry right now?"),
            ("User: Bahut tension ho rahi hai, dimag mein bohot thoughts aa rahe.\nAssistant:",
             "Ghabrahat normal hai, especially when thoughts race. Ek gehri saans lete hain together. Sabse zyada kya chinta hai?")
        ]
    elif emotion == "happy":
        few_shots = [
            ("User: I'm feeling so good today, everything is going well!\nAssistant:",
             "That's wonderful to hear! 😊 Your happiness is contagious. What's making you feel so good today?"),
            ("User: Aaj bahut khushi ho rahi hai, sab kuch achha chal raha.\nAssistant:",
             "Bahut achhi baat hai! Khushi ki baat hai. Kya khaas baat hai jo aapko itna khush kar rahi hai?")
        ]
    else:
        # Default few-shots
        few_shots = [
            ("User: I don't know what to do about my situation.\nAssistant:",
             "Uncertainty can feel overwhelming. I'm here to listen and support you. Would you like to share what's on your mind?"),
            ("User: Samajh nahi aa raha kya karu.\nAssistant:",
             "Confusion mein hona bilkul normal hai. Main yahan hun sunne ke liye. Kya share karna chahenge?")
        ]
    
    few_shot_block = "\n\n".join(s + " " + r for s, r in few_shots)
    
    prompt = (
        f"System: {enhanced_system}\n"
        f"{('Context: ' + ctx + '\n') if ctx else ''}"
        f"Detected emotion: {emotion} (intensity: {intensity})\n"
        f"{few_shot_block}\n\n"
        f"User: {user_text}\nAssistant:"
    )
    
    return prompt

def _postprocess_response(generated: str, emotion: str) -> str:
    """Enhanced postprocessing with emotion-aware adjustments"""
    if "Assistant:" in generated:
        generated = generated.split("Assistant:")[-1]
    generated = generated.split("\nUser:")[0].strip()
    generated = re.sub(r'\s+', ' ', generated).strip()
    
    # Remove any repetitive patterns
    sentences = generated.split('. ')
    unique_sentences = []
    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)
    generated = '. '.join(unique_sentences)
    
    return generated

def generate_enhanced_reply(user_text: str, context: str = "", emotion_data: Dict = None) -> str:
    """Enhanced reply generation with emotion and cultural awareness"""
    if not emotion_data:
        emotion_data = {"primary_emotion": "neutral", "intensity": "medium", "multiple_emotions": {}}
    
    emotion = emotion_data.get("primary_emotion", "neutral")
    intensity = emotion_data.get("intensity", "medium")
    
    # Try culturally-aware template response first
    cultural_contexts = detect_cultural_context(user_text)
    if cultural_contexts or emotion != "neutral":
        template_response = generate_culturally_aware_response(user_text, emotion, cultural_contexts, intensity)
        if len(template_response) > 50:  # If we got a substantial response
            return template_response
    
    # Fallback to AI generation
    prompt = _build_enhanced_prompt(user_text, context, emotion, emotion_data)
    
    try:
        outputs = generator(
            prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            repetition_penalty=REPETITION_PENALTY,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            truncation=True,
        )
        
        raw = outputs[0]["generated_text"]
        reply = _postprocess_response(raw, emotion)
        
        if not reply:
            reply = "I'm here with you. Would you like to tell me more about what's on your mind?"
        
        # Add emotion-specific emoji/tone
        if emotion == "happy" and "😊" not in reply:
            reply = f"{reply} 😊"
        elif emotion == "sad" and "💙" not in reply:
            reply = f"{reply} 💙"
        elif emotion in ["anxious", "overwhelmed"] and "🤗" not in reply:
            reply = f"{reply} Take it one step at a time."
        
        return reply
        
    except Exception as e:
        print(f"Error in AI generation: {e}")
        # Fallback to template response
        return generate_culturally_aware_response(user_text, emotion, cultural_contexts, intensity)

# Backward compatibility
def generate_reply(user_text: str, context: str = "", emotion: str = "neutral") -> str:
    """Backward compatible function"""
    emotion_data = {"primary_emotion": emotion, "intensity": "medium"}
    return generate_enhanced_reply(user_text, context, emotion_data)

# Testing function
if __name__ == "__main__":
    test_cases = [
        {
            "text": "I'm feeling really sad and depressed today",
            "emotion_data": {"primary_emotion": "sad", "intensity": "high", "multiple_emotions": {"sad": 0.9}}
        },
        {
            "text": "Bahut khush hun aaj, promotion mil gaya!",
            "emotion_data": {"primary_emotion": "happy", "intensity": "high", "multiple_emotions": {"happy": 0.8, "excited": 0.6}}
        },
        {
            "text": "Ghar wale shaadi ke liye pressure kar rahe hain, samajh nahi aa raha",
            "emotion_data": {"primary_emotion": "confused", "intensity": "medium", "multiple_emotions": {"confused": 0.7, "anxious": 0.5}}
        }
    ]
    
    for case in test_cases:
        print(f"\nInput: {case['text']}")
        print(f"Emotion: {case['emotion_data']['primary_emotion']}")
        response = generate_enhanced_reply(case['text'], "", case['emotion_data'])
        print(f"Response: {response}")
        print("-" * 50)