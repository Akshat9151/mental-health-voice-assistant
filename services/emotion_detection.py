# services/emotion_detection.py
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon (only once)
nltk.download('vader_lexicon')

# Initialize analyzer
sia = SentimentIntensityAnalyzer()

def detect_emotion(text):
    """
    Advanced offline emotion detection using VADER + keyword mapping.
    Optimized thresholds for better sensitivity.
    Returns: 'happy', 'sad', 'angry', 'neutral'
    """
    text_lower = text.lower()

    # Keyword mapping (high priority)
    if any(word in text_lower for word in ["sad", "depressed", "unhappy", "down", "lonely"]):
        return "sad"
    elif any(word in text_lower for word in ["happy", "great", "good", "awesome", "joyful", "excited"]):
        return "happy"
    elif any(word in text_lower for word in ["angry", "mad", "furious", "frustrated", "annoyed"]):
        return "angry"

    # Fallback: VADER sentiment analysis
    scores = sia.polarity_scores(text_lower)
    compound = scores['compound']

    # Optimized thresholds
    if compound >= 0.3:      # small-medium positive → happy
        return "happy"
    elif compound <= -0.3:   # small-medium negative → sad
        return "sad"
    elif -0.3 < compound < -0.05:  # slightly negative → angry
        return "angry"
    else:
        return "neutral"
# Example mapping (just for demo)
keywords = {
    "happy": ["great", "awesome", "good", "love"],
    "sad": ["bad", "tired", "upset", "depressed"],
    "angry": ["angry", "hate", "annoyed", "frustrated"]
}
