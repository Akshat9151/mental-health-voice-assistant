# services/text_to_speech.py
import pyttsx3
import os
import time
import threading
from typing import Optional, Dict

class EmotionalTTS:
    def __init__(self):
        self.engine = None
        self.voices = []
        self.current_emotion = "neutral"
        self.initialize_engine()
    
    def initialize_engine(self):
        """Initialize TTS engine with error handling"""
        try:
            # Try different TTS engines based on platform
            engines_to_try = ["sapi5", "espeak", "nsss"]  # Windows, Linux, macOS
            
            for engine_name in engines_to_try:
                try:
                    self.engine = pyttsx3.init(engine_name)
                    break
                except:
                    continue
            
            if not self.engine:
                self.engine = pyttsx3.init()  # Default engine
            
            # Get available voices
            self.voices = self.engine.getProperty("voices") or []
            
            # Set default properties
            self.engine.setProperty("rate", 170)
            self.engine.setProperty("volume", 1.0)
            
            # Prefer female voice for mental health assistant (more soothing)
            if len(self.voices) >= 2:
                self.engine.setProperty("voice", self.voices[1].id)
            elif len(self.voices) >= 1:
                self.engine.setProperty("voice", self.voices[0].id)
                
        except Exception as e:
            print(f"[TTS INIT ERROR] {e}")
            self.engine = None
    
    def adjust_voice_for_emotion(self, emotion: str):
        """Adjust voice parameters based on emotion"""
        if not self.engine:
            return
        
        emotion_settings = {
            "happy": {"rate": 180, "volume": 1.0},
            "excited": {"rate": 190, "volume": 1.0},
            "sad": {"rate": 140, "volume": 0.8},
            "anxious": {"rate": 160, "volume": 0.9},
            "angry": {"rate": 200, "volume": 1.0},
            "calm": {"rate": 150, "volume": 0.9},
            "peaceful": {"rate": 140, "volume": 0.8},
            "overwhelmed": {"rate": 130, "volume": 0.7},
            "hopeful": {"rate": 165, "volume": 0.9},
            "grateful": {"rate": 160, "volume": 0.9},
            "neutral": {"rate": 170, "volume": 1.0}
        }
        
        settings = emotion_settings.get(emotion, emotion_settings["neutral"])
        
        try:
            self.engine.setProperty("rate", settings["rate"])
            self.engine.setProperty("volume", settings["volume"])
            self.current_emotion = emotion
        except Exception as e:
            print(f"[TTS EMOTION ADJUST ERROR] {e}")
    
    def add_emotional_pauses(self, text: str, emotion: str) -> str:
        """Add appropriate pauses based on emotion and content"""
        if emotion in ["sad", "overwhelmed", "anxious"]:
            # Add more pauses for emotional support
            text = text.replace(". ", "... ")
            text = text.replace(", ", ", ... ")
        elif emotion in ["excited", "happy"]:
            # Slightly faster with fewer pauses
            text = text.replace("... ", ". ")
        
        # Add pauses after supportive phrases
        supportive_phrases = [
            "I understand", "I hear you", "That sounds difficult", 
            "You're not alone", "I'm here with you", "Take your time"
        ]
        
        for phrase in supportive_phrases:
            text = text.replace(phrase, f"{phrase}...")
        
        return text
    
    def speak_with_emotion(self, text: str, emotion: str = "neutral", save_audio: bool = True) -> bool:
        """Speak text with emotional adjustment"""
        if not self.engine:
            print("[TTS ERROR] Engine not initialized")
            return False
        
        try:
            # Adjust voice for emotion
            self.adjust_voice_for_emotion(emotion)
            
            # Add emotional pauses
            enhanced_text = self.add_emotional_pauses(text, emotion)
            
            # Save audio file if requested
            if save_audio:
                timestamp = int(time.time())
                filename = f"reply_{emotion}_{timestamp}.wav"
                filepath = os.path.join("data", "voice_notes", filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                self.engine.save_to_file(enhanced_text, filepath)
            
            # Speak the text
            self.engine.say(enhanced_text)
            self.engine.runAndWait()
            return True
            
        except Exception as e:
            print(f"[TTS SPEAK ERROR] {e}")
            return False
    
    def get_voice_info(self) -> Dict:
        """Get information about available voices"""
        voice_info = {
            "current_emotion": self.current_emotion,
            "available_voices": len(self.voices),
            "engine_initialized": self.engine is not None
        }
        
        if self.voices:
            voice_info["voices"] = []
            for i, voice in enumerate(self.voices):
                voice_info["voices"].append({
                    "id": i,
                    "name": getattr(voice, 'name', f'Voice {i}'),
                    "language": getattr(voice, 'languages', ['unknown'])
                })
        
        return voice_info

# Global TTS instance
emotional_tts = EmotionalTTS()

def speak_text(text: str, emotion: str = "neutral", save_audio: bool = True) -> bool:
    """Main TTS function with emotional support"""
    return emotional_tts.speak_with_emotion(text, emotion, save_audio)

def speak_text_safe(text: str, emotion: str = "neutral"):
    """Thread-safe TTS function"""
    def run_tts():
        speak_text(text, emotion)
    
    t = threading.Thread(target=run_tts, daemon=True)
    t.start()

def get_tts_info() -> Dict:
    """Get TTS system information"""
    return emotional_tts.get_voice_info()

# Enhanced speech patterns for Indian context
def enhance_text_for_indian_context(text: str) -> str:
    """Enhance text pronunciation for Indian context"""
    # Common Indian name pronunciations
    indian_replacements = {
        "Namaste": "Nah-mas-tay",
        "ji": "jee",
        "haan": "haan",
        "nahi": "nah-hee",
        "achha": "ach-chaa",
        "theek": "theek hai",
        "samjha": "sam-jhaa",
        "pareshaan": "pa-re-shaan",
        "khushi": "khu-shee",
        "dukh": "dukh",
        "gussa": "gus-saa"
    }
    
    enhanced_text = text
    for hindi_word, pronunciation in indian_replacements.items():
        enhanced_text = enhanced_text.replace(hindi_word, pronunciation)
    
    return enhanced_text

def speak_with_indian_context(text: str, emotion: str = "neutral") -> bool:
    """Speak with Indian pronunciation adjustments"""
    enhanced_text = enhance_text_for_indian_context(text)
    return speak_text(enhanced_text, emotion)

# Testing function
if __name__ == "__main__":
    # Test different emotions
    test_cases = [
        ("Hello, I'm here to help you feel better.", "happy"),
        ("I understand you're going through a difficult time.", "sad"),
        ("Take a deep breath with me. You're safe now.", "calm"),
        ("That sounds really overwhelming. Let's take it step by step.", "anxious"),
        ("Namaste! Main aapki madad karne ke liye yahan hun.", "neutral")
    ]
    
    print("Testing Emotional TTS...")
    for text, emotion in test_cases:
        print(f"Speaking with {emotion} emotion: {text}")
        speak_text(text, emotion, save_audio=False)
        time.sleep(1)
    
    print(f"TTS Info: {get_tts_info()}")
