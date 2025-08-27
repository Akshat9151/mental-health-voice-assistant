# services/text_to_speech.py
import pyttsx3
import os
import time

def speak_text(text, save_audio=True):
    """Convert text to speech and (optionally) save as .wav file."""
    try:
        # Windows ke liye sapi5 engine (recommended)
        engine = pyttsx3.init("sapi5")

        # Voice settings
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)  # Male voice
            # engine.setProperty("voice", voices[1].id)  # Female voice (optional)

        engine.setProperty("rate", 170)   # Speed
        engine.setProperty("volume", 1.0) # Full volume

        # Save audio file (optional)
        if save_audio:
            timestamp = int(time.time())
            filename = f"reply_{timestamp}.wav"
            filepath = os.path.join("data", "voice_notes", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            engine.save_to_file(text, filepath)

        # Speak aloud
        engine.say(text)
        engine.runAndWait()
        return True

    except Exception as e:
        print(f"[TTS ERROR] {e}")
        return False
import threading

def speak_text_safe(text):
    def run_tts():
        speak_text(text)  # aapka TTS function
    
    t = threading.Thread(target=run_tts)
    t.start()
