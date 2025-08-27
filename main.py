import tkinter as tk
import threading
import time

from services.speech_to_text import transcribe_speech
from services.text_to_speech import speak_text
from services.nlp_model import generate_reply
from services.emotion_detection import detect_emotion
from memory.memory_manager import (   # ✅ FIXED import here
    add_to_memory,
    get_context,
    get_recent_emotions,
    save_memory_to_file,
    load_memory_from_file
)
from services.safety_guard import assess_risk, crisis_response
from utils.logger import log_message
from utils.helpers import clean_text

# ---------------- GUI / Display Setup ----------------
root = tk.Tk()
root.title("Mental Health Assistant")
root.geometry("500x200")
label = tk.Label(root, text="Assistant is starting...", font=("Arial", 16), wraplength=480)
label.pack(pady=50)


def update_display(text):
    """Update assistant reply on GUI"""
    label.config(text=text)
    root.update_idletasks()


# ---------------- Speak in Background ----------------
def speak_in_background(text):
    """Run TTS in a separate thread so GUI & loop don’t block"""
    threading.Thread(target=speak_text, args=(text,), daemon=True).start()


# ---------------- Main Assistant Loop ----------------
def assistant_loop():
    print("Mental Health Assistant is ready! Say 'exit' to quit.\n")
    load_memory_from_file()

    while True:
        print("🎤 Listening...")
        user_text = transcribe_speech()
        if not user_text:
            continue

        # ---- Exit Condition ----
        if "exit" in user_text.lower():
            print("👋 Goodbye!")
            update_display("Goodbye! Take care 💙")
            speak_in_background("Goodbye! Take care.")
            save_memory_to_file()
            break

        user_text = clean_text(user_text)
        log_message("User", user_text)

        # ---- SAFETY CHECK (FIRST) ----
        risk, category, patterns = assess_risk(user_text)
        if risk in ("high", "medium"):
            bot_reply = crisis_response(locale="IN")   # Adjust locale if needed
            log_message("Assistant", f"[CRISIS-{risk.upper()}:{category}] " + bot_reply)
            update_display(bot_reply)
            speak_in_background(bot_reply)
            add_to_memory(user_text, bot_reply, emotion="crisis")
            save_memory_to_file()
            time.sleep(2)
            continue  # Skip normal generation for this turn

        # ---- Emotion Detection ----
        emotion = detect_emotion(user_text)
        log_message("Emotion", emotion)

        # ---- Context + NLP Reply (emotion-aware) ----
        context = get_context()
        bot_reply = generate_reply(user_text, context, emotion)

        # ---- Repeated sadness nudge ----
        recent_emotions = get_recent_emotions()
        if recent_emotions.count("sad") >= 3:
            bot_reply = (
                "I’ve noticed you’ve been feeling low for a while. "
                "I care about you, and I want to make sure you’re okay. "
                "Would you like to talk more or take a break?"
            )

        # ---- Output ----
        log_message("Assistant", bot_reply)
        update_display(bot_reply)
        speak_in_background(bot_reply)

        # ---- Memory ----
        add_to_memory(user_text, bot_reply, emotion)
        save_memory_to_file()

        time.sleep(2)


# ---------------- Run App ----------------
threading.Thread(target=assistant_loop, daemon=True).start()
root.mainloop()
