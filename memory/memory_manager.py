import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import Counter

# File where memory will be stored
MEMORY_FILE = "memory/conversation_memory.json"
EMOTION_ANALYTICS_FILE = "memory/emotion_analytics.json"

# Initialize memory files if they don't exist
def initialize_memory_files():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "messages": [],
                "user_profile": {
                    "preferred_language": "mixed",
                    "cultural_context": "indian",
                    "communication_style": "supportive",
                    "crisis_history": [],
                    "positive_triggers": [],
                    "stress_patterns": []
                },
                "session_metadata": {
                    "total_sessions": 0,
                    "last_session": None,
                    "average_session_length": 0
                }
            }, f)
    
    if not os.path.exists(EMOTION_ANALYTICS_FILE):
        with open(EMOTION_ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "emotion_history": [],
                "patterns": {},
                "insights": {},
                "last_updated": datetime.now().isoformat()
            }, f)

initialize_memory_files()

def add_to_memory(user_message: str, bot_reply: str, emotion: str = None, emotion_data: Dict = None):
    """Enhanced memory storage with detailed emotion tracking"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create comprehensive message entry
    message_entry = {
        "user": user_message,
        "bot": bot_reply,
        "emotion": emotion,
        "emotion_data": emotion_data or {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": _get_current_session_id(),
        "message_length": len(user_message),
        "response_length": len(bot_reply)
    }

    data["messages"].append(message_entry)

    # Keep last 50 interactions (increased from 10)
    data["messages"] = data["messages"][-50:]
    
    # Update session metadata
    data["session_metadata"]["last_session"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    # Update emotion analytics
    if emotion and emotion != "neutral":
        _update_emotion_analytics(user_message, emotion, emotion_data)

def _get_current_session_id() -> str:
    """Generate or get current session ID"""
    now = datetime.now()
    return f"session_{now.strftime('%Y%m%d_%H')}"  # New session every hour

def _update_emotion_analytics(user_message: str, emotion: str, emotion_data: Dict = None):
    """Update emotion analytics and patterns"""
    with open(EMOTION_ANALYTICS_FILE, "r", encoding="utf-8") as f:
        analytics = json.load(f)
    
    # Add to emotion history
    emotion_entry = {
        "emotion": emotion,
        "intensity": emotion_data.get("intensity", "medium") if emotion_data else "medium",
        "multiple_emotions": emotion_data.get("multiple_emotions", {}) if emotion_data else {},
        "text_sample": user_message[:100] + "..." if len(user_message) > 100 else user_message,
        "timestamp": datetime.now().isoformat(),
        "hour_of_day": datetime.now().hour,
        "day_of_week": datetime.now().weekday()
    }
    
    analytics["emotion_history"].append(emotion_entry)
    
    # Keep last 200 emotion entries
    analytics["emotion_history"] = analytics["emotion_history"][-200:]
    
    # Update patterns
    _analyze_emotion_patterns(analytics)
    
    analytics["last_updated"] = datetime.now().isoformat()
    
    with open(EMOTION_ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=4)

def _analyze_emotion_patterns(analytics: Dict):
    """Analyze emotion patterns and generate insights"""
    emotion_history = analytics["emotion_history"]
    
    if len(emotion_history) < 5:
        return
    
    # Recent emotions (last 10)
    recent_emotions = emotion_history[-10:]
    
    # Pattern analysis
    patterns = {
        "dominant_emotions": {},
        "time_patterns": {"morning": {}, "afternoon": {}, "evening": {}, "night": {}},
        "intensity_trends": {"high": 0, "medium": 0, "low": 0},
        "weekly_patterns": {str(i): {} for i in range(7)},  # 0=Monday, 6=Sunday
        "emotion_transitions": {},
        "concerning_patterns": []
    }
    
    # Analyze dominant emotions
    emotion_counts = Counter(entry["emotion"] for entry in emotion_history)
    patterns["dominant_emotions"] = dict(emotion_counts.most_common(10))
    
    # Time of day analysis
    for entry in emotion_history:
        hour = entry["hour_of_day"]
        emotion = entry["emotion"]
        
        if 5 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 17:
            time_period = "afternoon"
        elif 17 <= hour < 21:
            time_period = "evening"
        else:
            time_period = "night"
        
        if emotion not in patterns["time_patterns"][time_period]:
            patterns["time_patterns"][time_period][emotion] = 0
        patterns["time_patterns"][time_period][emotion] += 1
    
    # Intensity trends
    for entry in emotion_history:
        intensity = entry.get("intensity", "medium")
        patterns["intensity_trends"][intensity] += 1
    
    # Weekly patterns
    for entry in emotion_history:
        day = str(entry["day_of_week"])
        emotion = entry["emotion"]
        if emotion not in patterns["weekly_patterns"][day]:
            patterns["weekly_patterns"][day][emotion] = 0
        patterns["weekly_patterns"][day][emotion] += 1
    
    # Emotion transitions
    for i in range(1, len(emotion_history)):
        prev_emotion = emotion_history[i-1]["emotion"]
        curr_emotion = emotion_history[i]["emotion"]
        transition = f"{prev_emotion}->{curr_emotion}"
        
        if transition not in patterns["emotion_transitions"]:
            patterns["emotion_transitions"][transition] = 0
        patterns["emotion_transitions"][transition] += 1
    
    # Identify concerning patterns
    concerning_emotions = ["sad", "angry", "anxious", "overwhelmed", "lonely", "hopeless"]
    recent_concerning = [e["emotion"] for e in recent_emotions if e["emotion"] in concerning_emotions]
    
    if len(recent_concerning) >= 5:
        patterns["concerning_patterns"].append("high_frequency_negative_emotions")
    
    if len(set(recent_concerning)) <= 2 and len(recent_concerning) >= 4:
        patterns["concerning_patterns"].append("persistent_single_negative_emotion")
    
    high_intensity_negative = [e for e in recent_emotions if e["emotion"] in concerning_emotions and e.get("intensity") == "high"]
    if len(high_intensity_negative) >= 3:
        patterns["concerning_patterns"].append("high_intensity_distress")
    
    analytics["patterns"] = patterns
    
    # Generate insights
    _generate_insights(analytics)

def _generate_insights(analytics: Dict):
    """Generate actionable insights from patterns"""
    patterns = analytics["patterns"]
    insights = {}
    
    # Dominant emotion insights
    if patterns["dominant_emotions"]:
        top_emotion = max(patterns["dominant_emotions"], key=patterns["dominant_emotions"].get)
        insights["primary_emotional_state"] = {
            "emotion": top_emotion,
            "frequency": patterns["dominant_emotions"][top_emotion],
            "recommendation": _get_emotion_recommendation(top_emotion)
        }
    
    # Time-based insights
    time_recommendations = []
    for time_period, emotions in patterns["time_patterns"].items():
        if emotions:
            dominant_time_emotion = max(emotions, key=emotions.get)
            if dominant_time_emotion in ["sad", "anxious", "overwhelmed"]:
                time_recommendations.append(f"Consider {time_period} self-care routines")
    
    insights["time_based_recommendations"] = time_recommendations
    
    # Concerning pattern insights
    if patterns["concerning_patterns"]:
        insights["mental_health_alerts"] = {
            "patterns": patterns["concerning_patterns"],
            "recommendation": "Consider reaching out to a mental health professional",
            "urgency": "medium" if len(patterns["concerning_patterns"]) >= 2 else "low"
        }
    
    # Positive pattern recognition
    positive_emotions = ["happy", "grateful", "excited", "peaceful", "hopeful", "proud"]
    positive_count = sum(patterns["dominant_emotions"].get(emotion, 0) for emotion in positive_emotions)
    total_emotions = sum(patterns["dominant_emotions"].values())
    
    if total_emotions > 0:
        positive_ratio = positive_count / total_emotions
        insights["emotional_balance"] = {
            "positive_ratio": positive_ratio,
            "status": "good" if positive_ratio > 0.4 else "needs_attention" if positive_ratio > 0.2 else "concerning"
        }
    
    analytics["insights"] = insights

def _get_emotion_recommendation(emotion: str) -> str:
    """Get specific recommendation for dominant emotion"""
    recommendations = {
        "sad": "Try engaging in activities that bring you joy, connect with supportive people, or consider gentle exercise",
        "anxious": "Practice breathing exercises, try grounding techniques, or consider mindfulness meditation",
        "angry": "Use physical exercise to release tension, try journaling, or practice deep breathing",
        "lonely": "Reach out to friends or family, consider joining social activities, or engage in community service",
        "overwhelmed": "Break tasks into smaller steps, practice saying no, and prioritize self-care",
        "happy": "Great! Continue activities that bring you joy and consider sharing your positivity with others",
        "grateful": "Wonderful! Keep practicing gratitude and consider keeping a gratitude journal"
    }
    return recommendations.get(emotion, "Continue monitoring your emotional patterns and practice self-care")

def get_context(include_emotions: bool = True) -> str:
    """Return contextual information from recent conversations"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    last_msgs = data["messages"][-5:]  # Increased from 3 to 5
    context = ""
    
    for msg in last_msgs:
        if include_emotions and msg.get("emotion"):
            context += f"User ({msg['emotion']}): {msg['user']}\nBot: {msg['bot']}\n"
        else:
            context += f"User: {msg['user']}\nBot: {msg['bot']}\n"

    return context

def get_recent_emotions(count: int = 5) -> List[str]:
    """Return recent emotions with configurable count"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [m["emotion"] for m in data["messages"][-count:] if m.get("emotion")]

def get_emotion_analytics() -> Dict:
    """Get comprehensive emotion analytics"""
    try:
        with open(EMOTION_ANALYTICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"emotion_history": [], "patterns": {}, "insights": {}}

def get_user_profile() -> Dict:
    """Get user profile information"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("user_profile", {})

def update_user_profile(updates: Dict):
    """Update user profile with new information"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "user_profile" not in data:
        data["user_profile"] = {}
    
    data["user_profile"].update(updates)
    
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_session_summary() -> Dict:
    """Get summary of current session"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    current_session = _get_current_session_id()
    session_messages = [m for m in data["messages"] if m.get("session_id") == current_session]
    
    if not session_messages:
        return {"message_count": 0, "emotions": [], "duration": "0 minutes"}
    
    emotions = [m["emotion"] for m in session_messages if m.get("emotion")]
    emotion_counts = Counter(emotions)
    
    return {
        "message_count": len(session_messages),
        "emotions": dict(emotion_counts),
        "dominant_emotion": max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral",
        "start_time": session_messages[0]["timestamp"],
        "last_message": session_messages[-1]["timestamp"]
    }

def detect_emotional_crisis_pattern() -> Dict:
    """Detect if user is in emotional crisis based on recent patterns"""
    recent_emotions = get_recent_emotions(10)
    
    crisis_indicators = {
        "high_risk_emotions": ["hopeless", "suicidal", "overwhelmed"],
        "medium_risk_emotions": ["sad", "angry", "anxious", "lonely"],
        "crisis_score": 0,
        "recommendations": []
    }
    
    # Check for high-risk emotions
    high_risk_count = sum(1 for emotion in recent_emotions if emotion in crisis_indicators["high_risk_emotions"])
    medium_risk_count = sum(1 for emotion in recent_emotions if emotion in crisis_indicators["medium_risk_emotions"])
    
    crisis_indicators["crisis_score"] = (high_risk_count * 3) + (medium_risk_count * 1)
    
    if crisis_indicators["crisis_score"] >= 15:
        crisis_indicators["level"] = "high"
        crisis_indicators["recommendations"] = [
            "Immediate professional support recommended",
            "Consider crisis hotline",
            "Reach out to trusted person"
        ]
    elif crisis_indicators["crisis_score"] >= 8:
        crisis_indicators["level"] = "medium"
        crisis_indicators["recommendations"] = [
            "Consider professional counseling",
            "Practice self-care activities",
            "Connect with support system"
        ]
    else:
        crisis_indicators["level"] = "low"
        crisis_indicators["recommendations"] = [
            "Continue monitoring emotional wellbeing",
            "Maintain healthy habits"
        ]
    
    return crisis_indicators


def save_memory_to_file(filename="memory/conversation_backup.json"):
    """Manually save current memory to another file"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_memory_from_file(filename="memory/conversation_backup.json"):
    """Load memory backup into main memory file"""
    global MEMORY_FILE
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
from memory.memory_manager import (
    add_to_memory,
    get_context,
    get_recent_emotions
)
