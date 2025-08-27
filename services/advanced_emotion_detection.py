# services/advanced_emotion_detection.py
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Initialize VADER analyzer
sia = SentimentIntensityAnalyzer()

# Comprehensive emotion mapping with Indian cultural context
EMOTION_KEYWORDS = {
    # Primary emotions
    "happy": {
        "english": ["happy", "joyful", "excited", "cheerful", "delighted", "elated", "thrilled", "ecstatic", "blissful", "content", "pleased", "glad", "overjoyed"],
        "hindi": ["khush", "prasanna", "anandita", "ullasit", "harshit"],
        "hinglish": ["bahut khush", "ekdum happy", "super excited", "full maja", "bohot achha lag raha"]
    },
    "sad": {
        "english": ["sad", "depressed", "melancholy", "dejected", "despondent", "downhearted", "gloomy", "miserable", "sorrowful", "unhappy", "blue", "down", "low"],
        "hindi": ["udaas", "dukhi", "vishad", "nirash", "hataash", "mayoos"],
        "hinglish": ["bahut sad", "dil kharab", "mood off", "depression mein", "down feel kar raha"]
    },
    "angry": {
        "english": ["angry", "furious", "enraged", "irate", "livid", "mad", "irritated", "annoyed", "frustrated", "outraged", "incensed", "wrathful"],
        "hindi": ["gussa", "krodh", "aakvosh", "chidh", "naraaz", "khafa"],
        "hinglish": ["bahut gussa", "full angry", "dimag kharab", "pagal ho gaya", "bohot irritate"]
    },
    
    # Complex emotions
    "anxious": {
        "english": ["anxious", "worried", "nervous", "tense", "stressed", "apprehensive", "uneasy", "restless", "troubled", "concerned", "panicked"],
        "hindi": ["chinta", "ghabrahat", "pareshaan", "vyakul", "udweg", "ashant"],
        "hinglish": ["tension mein", "stress ho raha", "ghabrahat ho rahi", "worried feel kar raha", "anxiety attack"]
    },
    "confused": {
        "english": ["confused", "puzzled", "bewildered", "perplexed", "baffled", "lost", "uncertain", "unclear", "mixed up"],
        "hindi": ["bhram", "confusion", "samjh nahi aa raha", "ajeeb lag raha"],
        "hinglish": ["confuse ho gaya", "kuch samjh nahi aa raha", "dimaag kharab", "mixed feelings"]
    },
    "lonely": {
        "english": ["lonely", "isolated", "alone", "abandoned", "forsaken", "solitary", "desolate", "friendless"],
        "hindi": ["akela", "tanhaai", "viyog", "nirjanta", "ekaki"],
        "hinglish": ["akela feel kar raha", "loneliness ho rahi", "koi nahi hai", "isolation mein"]
    },
    "overwhelmed": {
        "english": ["overwhelmed", "overloaded", "swamped", "buried", "drowning", "crushed", "overburdened"],
        "hindi": ["vyakulta", "adhikta", "bojh"],
        "hinglish": ["bohot zyada pressure", "handle nahi kar pa raha", "overwhelm ho gaya", "capacity se zyada"]
    },
    "grateful": {
        "english": ["grateful", "thankful", "appreciative", "blessed", "indebted", "obliged"],
        "hindi": ["kritajna", "dhanyawad", "aabhar", "shukraguzar"],
        "hinglish": ["bahut grateful", "thank you so much", "bohot meherbani", "aapka ehsaan"]
    },
    "hopeful": {
        "english": ["hopeful", "optimistic", "positive", "confident", "encouraged", "upbeat", "bright"],
        "hindi": ["aashawadi", "umang", "vishwas", "bharosa", "hausla"],
        "hinglish": ["umeed hai", "positive feeling", "confidence aa raha", "hopeful hu"]
    },
    "disappointed": {
        "english": ["disappointed", "let down", "disillusioned", "disheartened", "deflated", "crestfallen"],
        "hindi": ["nirash", "mayoos", "hatash", "dukhi"],
        "hinglish": ["disappoint ho gaya", "expectations nahi mile", "umeed toot gayi", "let down feel"]
    },
    "guilty": {
        "english": ["guilty", "ashamed", "remorseful", "regretful", "sorry", "repentant"],
        "hindi": ["paschataap", "lajja", "sharam", "aparadh-bhaav"],
        "hinglish": ["guilt feel kar raha", "sharam aa rahi", "galti ka ehsaas", "sorry lag raha"]
    },
    "proud": {
        "english": ["proud", "accomplished", "satisfied", "fulfilled", "successful", "triumphant"],
        "hindi": ["garv", "abhimaan", "santushti", "safalta"],
        "hinglish": ["proud feel kar raha", "garv hai", "achievement ka feeling", "success mili"]
    },
    "jealous": {
        "english": ["jealous", "envious", "resentful", "bitter", "covetous"],
        "hindi": ["jalan", "irshya", "dwesha", "matsarya"],
        "hinglish": ["jealous ho raha", "jalan ho rahi", "envy kar raha", "dusron se compare"]
    },
    "surprised": {
        "english": ["surprised", "shocked", "amazed", "astonished", "stunned", "startled", "bewildered"],
        "hindi": ["aaschary", "hairan", "chaunk", "vismay"],
        "hinglish": ["shocked ho gaya", "surprise mila", "hairan hun", "believe nahi ho raha"]
    },
    "excited": {
        "english": ["excited", "thrilled", "energetic", "enthusiastic", "eager", "pumped", "hyped"],
        "hindi": ["utsaah", "josh", "ullash", "harsha"],
        "hinglish": ["bahut excited", "full josh mein", "energy aa gayi", "pump up ho gaya"]
    },
    "frustrated": {
        "english": ["frustrated", "irritated", "exasperated", "aggravated", "vexed", "irked"],
        "hindi": ["pareshaan", "khijh", "chidh", "gussa"],
        "hinglish": ["frustrate ho gaya", "irritate kar raha", "dimag kharab", "patience khatam"]
    },
    "peaceful": {
        "english": ["peaceful", "calm", "serene", "tranquil", "relaxed", "composed", "zen"],
        "hindi": ["shanti", "shaant", "prasanna", "nirmal"],
        "hinglish": ["peace feel kar raha", "calm lag raha", "relaxed hun", "shanti mili"]
    },
    "motivated": {
        "english": ["motivated", "inspired", "driven", "determined", "ambitious", "focused"],
        "hindi": ["prerit", "udyami", "sankalp", "lakshya"],
        "hinglish": ["motivated feel kar raha", "inspiration mila", "drive aa gaya", "focus mein hun"]
    },
    "tired": {
        "english": ["tired", "exhausted", "drained", "weary", "fatigued", "worn out", "spent"],
        "hindi": ["thaka", "pareshaan", "shrama", "vyakul"],
        "hinglish": ["bahut tired", "energy khatam", "thak gaya", "drain ho gaya"]
    },
    "curious": {
        "english": ["curious", "interested", "intrigued", "wondering", "inquisitive"],
        "hindi": ["jigyasu", "utsukata", "ruchi", "chaah"],
        "hinglish": ["curious hun", "jaanna chahta", "interest aa raha", "wonder kar raha"]
    },
    "embarrassed": {
        "english": ["embarrassed", "humiliated", "mortified", "flustered", "awkward"],
        "hindi": ["lajja", "sharam", "sankoch", "vivashta"],
        "hinglish": ["embarrass ho gaya", "sharam aa rahi", "awkward feel", "face save nahi ho raha"]
    }
}

# Indian cultural expressions and idioms
CULTURAL_EXPRESSIONS = {
    "stress": ["sar par bojh", "dimag mein bhusa", "tension ki wajah se", "pressure cooker ki tarah"],
    "happiness": ["dil garden garden", "khushi ke maare pagal", "saat aasman par", "dil bagh bagh"],
    "sadness": ["dil mein bhari", "aankhon mein aansoo", "dil toot gaya", "mann udaas"],
    "anger": ["aag babula", "khoon khaul raha", "dimag ki nass phat gayi", "gusse mein andhaa"],
    "fear": ["dil mein dar", "ghabrahat ho rahi", "kaanp rahe hain", "dar ke maare"],
    "love": ["dil mein basa", "mohabbat mein", "pyaar ho gaya", "dil churana"],
    "worry": ["chinta mein dooba", "pareshani ka samudar", "fikar mein", "soch mein pad gaya"]
}

# Regional variations (basic implementation)
REGIONAL_PATTERNS = {
    "north_indian": ["yaar", "bhai", "dost", "ji haan", "arre", "oye"],
    "south_indian": ["anna", "akka", "machha", "ra", "da", "mama"],
    "west_indian": ["bhau", "tai", "dada", "kaka", "mavshi"],
    "east_indian": ["dada", "didi", "boudi", "jethu", "kaku"]
}

class AdvancedEmotionDetector:
    def __init__(self):
        self.emotion_history = []
        self.cultural_context = "indian"
        
    def detect_primary_emotion(self, text: str) -> Tuple[str, float]:
        """Detect the primary emotion with confidence score"""
        text_lower = text.lower()
        emotion_scores = {}
        
        # Check keyword matches with cultural context
        for emotion, keywords_dict in EMOTION_KEYWORDS.items():
            score = 0
            total_keywords = 0
            
            for lang, keywords in keywords_dict.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        # Weight different languages
                        if lang == "hinglish":
                            score += 2  # Higher weight for Hinglish
                        elif lang == "hindi":
                            score += 1.5  # Medium weight for Hindi
                        else:
                            score += 1  # Base weight for English
                        total_keywords += 1
            
            if total_keywords > 0:
                emotion_scores[emotion] = score / max(1, len(text_lower.split()) / 10)
        
        # Check cultural expressions
        for emotion_type, expressions in CULTURAL_EXPRESSIONS.items():
            for expr in expressions:
                if expr in text_lower:
                    # Map cultural expressions to emotions
                    if emotion_type == "stress":
                        emotion_scores["anxious"] = emotion_scores.get("anxious", 0) + 2
                    elif emotion_type == "happiness":
                        emotion_scores["happy"] = emotion_scores.get("happy", 0) + 2
                    elif emotion_type == "sadness":
                        emotion_scores["sad"] = emotion_scores.get("sad", 0) + 2
                    elif emotion_type == "anger":
                        emotion_scores["angry"] = emotion_scores.get("angry", 0) + 2
                    elif emotion_type == "fear":
                        emotion_scores["anxious"] = emotion_scores.get("anxious", 0) + 1.5
                    elif emotion_type == "worry":
                        emotion_scores["anxious"] = emotion_scores.get("anxious", 0) + 1.5
        
        # Fallback to VADER sentiment analysis
        if not emotion_scores:
            sentiment = sia.polarity_scores(text)
            compound = sentiment['compound']
            
            if compound >= 0.5:
                emotion_scores["happy"] = compound
            elif compound <= -0.5:
                emotion_scores["sad"] = abs(compound)
            elif compound <= -0.1:
                emotion_scores["angry"] = abs(compound) * 0.8
            elif 0.1 <= compound < 0.5:
                emotion_scores["hopeful"] = compound
            else:
                emotion_scores["neutral"] = 0.5
        
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[primary_emotion], 1.0)
            return primary_emotion, confidence
        
        return "neutral", 0.5
    
    def detect_multiple_emotions(self, text: str) -> Dict[str, float]:
        """Detect multiple emotions with their confidence scores"""
        text_lower = text.lower()
        emotion_scores = {}
        
        # Analyze each emotion category
        for emotion, keywords_dict in EMOTION_KEYWORDS.items():
            score = 0
            matches = 0
            
            for lang, keywords in keywords_dict.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        if lang == "hinglish":
                            score += 2
                        elif lang == "hindi":
                            score += 1.5
                        else:
                            score += 1
                        matches += 1
            
            if matches > 0:
                # Normalize by text length and number of matches
                normalized_score = score / max(1, len(text_lower.split()) / 5)
                emotion_scores[emotion] = min(normalized_score, 1.0)
        
        # Add cultural context boost
        for emotion_type, expressions in CULTURAL_EXPRESSIONS.items():
            for expr in expressions:
                if expr in text_lower:
                    if emotion_type == "stress" and "anxious" in emotion_scores:
                        emotion_scores["anxious"] += 0.3
                    elif emotion_type == "happiness" and "happy" in emotion_scores:
                        emotion_scores["happy"] += 0.3
                    # Add more mappings as needed
        
        # Remove emotions with very low scores
        emotion_scores = {k: v for k, v in emotion_scores.items() if v > 0.1}
        
        return emotion_scores
    
    def detect_regional_context(self, text: str) -> Optional[str]:
        """Detect regional linguistic patterns"""
        text_lower = text.lower()
        
        for region, patterns in REGIONAL_PATTERNS.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            if matches >= 2:
                return region
        
        return None
    
    def get_emotion_intensity(self, emotion: str, text: str) -> str:
        """Determine the intensity of an emotion (low, medium, high)"""
        text_lower = text.lower()
        
        # Intensity indicators
        high_intensity = ["very", "extremely", "really", "so", "too", "bahut", "bohot", "ekdam", "bilkul"]
        medium_intensity = ["quite", "pretty", "somewhat", "thoda", "kuch", "little bit"]
        
        high_count = sum(1 for word in high_intensity if word in text_lower)
        medium_count = sum(1 for word in medium_intensity if word in text_lower)
        
        if high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def analyze_emotion_context(self, text: str) -> Dict:
        """Comprehensive emotion analysis"""
        primary_emotion, confidence = self.detect_primary_emotion(text)
        multiple_emotions = self.detect_multiple_emotions(text)
        regional_context = self.detect_regional_context(text)
        intensity = self.get_emotion_intensity(primary_emotion, text)
        
        # Store in history
        emotion_data = {
            "text": text,
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "multiple_emotions": multiple_emotions,
            "intensity": intensity,
            "regional_context": regional_context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.emotion_history.append(emotion_data)
        if len(self.emotion_history) > 50:  # Keep last 50 entries
            self.emotion_history = self.emotion_history[-50:]
        
        return emotion_data
    
    def get_emotion_trends(self, window_size: int = 10) -> Dict:
        """Analyze emotion trends over recent conversations"""
        if len(self.emotion_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_emotions = self.emotion_history[-window_size:]
        emotion_counts = {}
        
        for entry in recent_emotions:
            emotion = entry["primary_emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        trend_strength = emotion_counts[dominant_emotion] / len(recent_emotions)
        
        return {
            "trend": "stable" if trend_strength < 0.4 else "strong",
            "dominant_emotion": dominant_emotion,
            "strength": trend_strength,
            "emotion_distribution": emotion_counts
        }

# Global instance
emotion_detector = AdvancedEmotionDetector()

def detect_emotion(text: str) -> str:
    """Simple interface for backward compatibility"""
    emotion_data = emotion_detector.analyze_emotion_context(text)
    return emotion_data["primary_emotion"]

def detect_emotion_detailed(text: str) -> Dict:
    """Detailed emotion analysis"""
    return emotion_detector.analyze_emotion_context(text)

def get_emotion_trends() -> Dict:
    """Get recent emotion trends"""
    return emotion_detector.get_emotion_trends()

# Example usage and testing
if __name__ == "__main__":
    test_texts = [
        "I'm feeling really sad and depressed today",
        "Bahut khush hun aaj, full excited feeling aa rahi hai",
        "Yaar, bohot tension ho rahi hai, sar mein dard",
        "मैं बहुत परेशान हूं, कुछ समझ नहीं आ रहा",
        "Dil mein bhari hai, kuch achha nahi lag raha",
        "Super happy! Everything is going great!",
        "Gussa aa raha hai, dimag kharab ho gaya"
    ]
    
    for text in test_texts:
        result = detect_emotion_detailed(text)
        print(f"\nText: {text}")
        print(f"Primary: {result['primary_emotion']} (confidence: {result['confidence']:.2f})")
        print(f"Multiple: {result['multiple_emotions']}")
        print(f"Intensity: {result['intensity']}")
        print(f"Regional: {result['regional_context']}")