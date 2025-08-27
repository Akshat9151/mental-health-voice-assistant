import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from typing import Dict, List

# Enhanced imports for comprehensive mental health support
from services.speech_to_text import transcribe_speech
from services.text_to_speech import speak_text
from services.enhanced_nlp_model import generate_enhanced_reply
from services.advanced_emotion_detection import detect_emotion_detailed, get_emotion_trends
from memory.memory_manager import (
    add_to_memory,
    get_context,
    get_recent_emotions,
    save_memory_to_file,
    load_memory_from_file,
    get_emotion_analytics,
    get_session_summary,
    detect_emotional_crisis_pattern
)
from services.safety_guard import assess_risk, crisis_response, provide_grounding_exercise, get_risk_trends
from utils.logger import log_message
from utils.helpers import clean_text

# ---------------- Enhanced GUI Setup ----------------
root = tk.Tk()
root.title("AI Mental Health Voice Assistant - Enhanced Edition")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# Create main frame
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configure grid weights
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(1, weight=1)

# Title
title_label = tk.Label(main_frame, text="🧠 AI Mental Health Voice Assistant", 
                      font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Status indicator
status_frame = ttk.Frame(main_frame)
status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

status_label = tk.Label(status_frame, text="🟢 Ready", font=("Arial", 12, "bold"), 
                       bg="#f0f0f0", fg="#27ae60")
status_label.pack(anchor="w")

emotion_label = tk.Label(status_frame, text="😐 Emotion: Neutral", font=("Arial", 10), 
                        bg="#f0f0f0", fg="#7f8c8d")
emotion_label.pack(anchor="w", pady=(5, 0))

# Conversation display
conv_frame = ttk.Frame(main_frame)
conv_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

conv_text = scrolledtext.ScrolledText(conv_frame, wrap=tk.WORD, width=50, height=20,
                                     font=("Arial", 10), bg="white", fg="#2c3e50")
conv_text.pack(fill="both", expand=True)

# Analytics panel
analytics_frame = ttk.LabelFrame(main_frame, text="Emotion Analytics", padding="5")
analytics_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

analytics_text = tk.Text(analytics_frame, wrap=tk.WORD, width=25, height=20,
                        font=("Arial", 9), bg="#ecf0f1", fg="#2c3e50")
analytics_text.pack(fill="both", expand=True)

# Control buttons
control_frame = ttk.Frame(main_frame)
control_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0))

def show_analytics():
    """Display emotion analytics in the side panel"""
    analytics = get_emotion_analytics()
    session_summary = get_session_summary()
    crisis_pattern = detect_emotional_crisis_pattern()
    
    analytics_text.delete(1.0, tk.END)
    
    # Session info
    analytics_text.insert(tk.END, "📊 SESSION SUMMARY\n", "header")
    analytics_text.insert(tk.END, f"Messages: {session_summary['message_count']}\n")
    analytics_text.insert(tk.END, f"Dominant: {session_summary.get('dominant_emotion', 'N/A')}\n\n")
    
    # Recent emotions
    recent_emotions = get_recent_emotions(5)
    analytics_text.insert(tk.END, "🎭 RECENT EMOTIONS\n", "header")
    for i, emotion in enumerate(recent_emotions[-5:], 1):
        emoji = get_emotion_emoji(emotion)
        analytics_text.insert(tk.END, f"{i}. {emoji} {emotion.title()}\n")
    
    # Crisis assessment
    analytics_text.insert(tk.END, f"\n⚠️ WELLNESS CHECK\n", "header")
    analytics_text.insert(tk.END, f"Level: {crisis_pattern['level'].upper()}\n")
    analytics_text.insert(tk.END, f"Score: {crisis_pattern['crisis_score']}/30\n")
    
    if crisis_pattern['level'] != 'low':
        analytics_text.insert(tk.END, "\n💡 RECOMMENDATIONS:\n", "header")
        for rec in crisis_pattern['recommendations'][:2]:
            analytics_text.insert(tk.END, f"• {rec}\n")
    
    # Insights
    insights = analytics.get("insights", {})
    if "primary_emotional_state" in insights:
        primary = insights["primary_emotional_state"]
        analytics_text.insert(tk.END, f"\n🎯 PRIMARY STATE\n", "header")
        analytics_text.insert(tk.END, f"{get_emotion_emoji(primary['emotion'])} {primary['emotion'].title()}\n")
        analytics_text.insert(tk.END, f"Frequency: {primary['frequency']}\n")

def get_emotion_emoji(emotion):
    """Get emoji for emotion"""
    emoji_map = {
        "happy": "😊", "sad": "😢", "angry": "😠", "anxious": "😰", "excited": "🤩",
        "confused": "😕", "lonely": "😔", "overwhelmed": "😵", "grateful": "🙏",
        "hopeful": "🌟", "disappointed": "😞", "guilty": "😳", "proud": "😌",
        "jealous": "😒", "surprised": "😲", "frustrated": "😤", "peaceful": "😌",
        "motivated": "💪", "tired": "😴", "curious": "🤔", "embarrassed": "😅",
        "neutral": "😐"
    }
    return emoji_map.get(emotion, "😐")

analytics_btn = ttk.Button(control_frame, text="📊 Show Analytics", command=show_analytics)
analytics_btn.pack(side="left", padx=(0, 10))

grounding_btn = ttk.Button(control_frame, text="🧘 Grounding Exercise", 
                          command=lambda: add_system_message(provide_grounding_exercise()))
grounding_btn.pack(side="left", padx=(0, 10))

def update_display(text, speaker="Assistant"):
    """Enhanced display update with conversation history"""
    timestamp = datetime.now().strftime("%H:%M")
    
    if speaker == "User":
        conv_text.insert(tk.END, f"\n[{timestamp}] 👤 You: {text}\n", "user")
    elif speaker == "System":
        conv_text.insert(tk.END, f"\n[{timestamp}] 🤖 System: {text}\n", "system")
    else:
        conv_text.insert(tk.END, f"\n[{timestamp}] 🤖 Assistant: {text}\n", "assistant")
    
    conv_text.see(tk.END)
    root.update_idletasks()
    
    # Update analytics panel
    show_analytics()

def add_system_message(message):
    """Add system message to conversation"""
    update_display(message, "System")

def update_status(status_text, emotion=None):
    """Update status and emotion display"""
    status_label.config(text=status_text)
    if emotion:
        emoji = get_emotion_emoji(emotion)
        emotion_label.config(text=f"{emoji} Emotion: {emotion.title()}")
    root.update_idletasks()

# Configure text tags for better formatting
conv_text.tag_configure("user", foreground="#3498db", font=("Arial", 10, "bold"))
conv_text.tag_configure("assistant", foreground="#27ae60", font=("Arial", 10))
conv_text.tag_configure("system", foreground="#e67e22", font=("Arial", 10, "italic"))

analytics_text.tag_configure("header", foreground="#2c3e50", font=("Arial", 9, "bold"))

# Initial welcome message
update_display("Welcome! I'm your AI Mental Health Assistant. I understand English, Hindi, and Hinglish. "
              "I'm here to listen, support, and help you navigate your emotions. "
              "Say 'exit' when you're ready to end our conversation. 💙", "System")


# ---------------- Enhanced Speak in Background ----------------
def speak_in_background(text, emotion="neutral"):
    """Run emotional TTS in a separate thread so GUI & loop don't block"""
    threading.Thread(target=speak_text, args=(text, emotion), daemon=True).start()


# ---------------- Enhanced Main Assistant Loop ----------------
def assistant_loop():
    print("🧠 Enhanced Mental Health Assistant is ready! Say 'exit' to quit.\n")
    load_memory_from_file()
    
    # Initialize session
    add_system_message("Starting new conversation session... 🌟")
    update_status("🟢 Ready to listen")

    while True:
        try:
            print("🎤 Listening...")
            update_status("🎤 Listening...", None)
            
            user_text = transcribe_speech()
            if not user_text:
                continue

            # ---- Exit Condition ----
            if "exit" in user_text.lower():
                print("👋 Goodbye!")
                session_summary = get_session_summary()
                goodbye_msg = (f"Goodbye! We talked for {session_summary['message_count']} messages today. "
                              f"Your primary emotion was {session_summary.get('dominant_emotion', 'neutral')}. "
                              f"Take care of yourself! 💙")
                update_display(goodbye_msg, "System")
                speak_in_background("Goodbye! Take care of yourself.")
                save_memory_to_file()
                break

            # Clean and log user input
            user_text = clean_text(user_text)
            log_message("User", user_text)
            update_display(user_text, "User")
            update_status("🤔 Processing...", None)

            # ---- ENHANCED SAFETY CHECK (FIRST PRIORITY) ----
            risk, category, patterns = assess_risk(user_text)
            if risk in ("high", "medium"):
                bot_reply = crisis_response(locale="IN", category=category)
                log_message("Assistant", f"[CRISIS-{risk.upper()}:{category}] " + bot_reply)
                update_display(bot_reply)
                speak_in_background(bot_reply, "sad")  # Use sad tone for crisis response
                add_to_memory(user_text, bot_reply, emotion="crisis")
                save_memory_to_file()
                
                # Offer grounding exercise for high-risk situations
                if risk == "high":
                    time.sleep(3)
                    grounding_offer = ("Would you like me to guide you through a grounding exercise right now? "
                                     "It can help when everything feels overwhelming.")
                    update_display(grounding_offer, "System")
                    
                time.sleep(2)
                continue  # Skip normal generation for crisis situations

            # ---- COMPREHENSIVE EMOTION DETECTION ----
            emotion_data = detect_emotion_detailed(user_text)
            primary_emotion = emotion_data["primary_emotion"]
            intensity = emotion_data["intensity"]
            multiple_emotions = emotion_data["multiple_emotions"]
            
            log_message("Emotion", f"{primary_emotion} ({intensity}) - {multiple_emotions}")
            update_status("💭 Understanding emotions...", primary_emotion)

            # ---- CONTEXT-AWARE NLP REPLY GENERATION ----
            context = get_context(include_emotions=True)
            bot_reply = generate_enhanced_reply(user_text, context, emotion_data)

            # ---- EMOTIONAL PATTERN ANALYSIS ----
            recent_emotions = get_recent_emotions(10)
            crisis_pattern = detect_emotional_crisis_pattern()
            
            # Handle concerning emotional patterns
            if crisis_pattern["level"] == "high":
                pattern_warning = (
                    "\n\nI've noticed some concerning patterns in our conversations. "
                    "Your wellbeing is important to me. Would you consider reaching out to "
                    "a mental health professional? I can provide some resources if helpful."
                )
                bot_reply += pattern_warning
            elif crisis_pattern["level"] == "medium":
                gentle_nudge = (
                    "\n\nI want to check in - how are you taking care of yourself lately? "
                    "Remember, it's okay to seek support when you need it. 💙"
                )
                bot_reply += gentle_nudge

            # ---- REPEATED EMOTION PATTERN DETECTION ----
            if len(recent_emotions) >= 5:
                emotion_counts = {emotion: recent_emotions.count(emotion) for emotion in set(recent_emotions)}
                dominant_recent = max(emotion_counts, key=emotion_counts.get)
                
                if emotion_counts[dominant_recent] >= 4:
                    if dominant_recent in ["sad", "lonely", "overwhelmed"]:
                        pattern_response = (
                            f"\n\nI've noticed you've been feeling {dominant_recent} quite often lately. "
                            "That must be really tough. Would you like to talk about what's been "
                            "contributing to these feelings, or would you prefer some coping strategies?"
                        )
                        bot_reply += pattern_response
                    elif dominant_recent == "anxious":
                        anxiety_response = (
                            "\n\nI see anxiety has been a recurring theme. That's exhausting to deal with. "
                            "Would you like to try a quick breathing exercise, or would you prefer to "
                            "talk through what's been triggering these anxious feelings?"
                        )
                        bot_reply += anxiety_response

            # ---- OUTPUT AND INTERACTION ----
            log_message("Assistant", bot_reply)
            update_display(bot_reply)
            speak_in_background(bot_reply, primary_emotion)  # Use detected emotion for TTS
            update_status("🟢 Ready to listen", primary_emotion)

            # ---- ENHANCED MEMORY STORAGE ----
            add_to_memory(user_text, bot_reply, primary_emotion, emotion_data)
            save_memory_to_file()

            # ---- EMOTION TREND ANALYSIS ----
            emotion_trends = get_emotion_trends()
            if emotion_trends.get("trend") == "strong" and emotion_trends.get("dominant_emotion") in ["sad", "angry", "anxious"]:
                print(f"[ALERT] Strong negative emotion trend detected: {emotion_trends['dominant_emotion']}")

            time.sleep(2)

        except Exception as e:
            print(f"[ERROR] Assistant loop error: {e}")
            error_message = "I'm having some technical difficulties. Let me try to help you anyway. 💙"
            update_display(error_message, "System")
            update_status("⚠️ Technical issue", None)
            time.sleep(2)


# ---------------- Run App ----------------
threading.Thread(target=assistant_loop, daemon=True).start()
root.mainloop()
