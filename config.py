# config.py

# Generation model
MODEL_NAME = "microsoft/DialoGPT-medium"   # or "gpt2-medium" if you prefer
MAX_NEW_TOKENS = 160
TEMPERATURE = 0.7
TOP_P = 0.92
TOP_K = 50
REPETITION_PENALTY = 1.15

# Locale for helplines
LOCALE = "IN"

# Output control
SPEAK_OUT_LOUD = False  # robot may handle TTS; set True to let backend speak too
