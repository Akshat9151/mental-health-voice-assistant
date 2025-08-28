#!/usr/bin/env python3
"""
Simplified Demo of AI Mental Health Voice Assistant
This demo showcases the system's functionality using only built-in Python modules
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

class SimplifiedMentalHealthAssistant:
    def __init__(self):
        # Simple emotion detection keywords
        self.emotion_keywords = {
            "happy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "fantastic", "good", "khush", "achha", "badhiya"],
            "sad": ["sad", "depressed", "down", "unhappy", "upset", "crying", "tears", "udaas", "dukhi", "pareshaan"],
            "angry": ["angry", "mad", "furious", "irritated", "annoyed", "pissed", "gussa", "naraz"],
            "anxious": ["anxious", "worried", "nervous", "scared", "fear", "panic", "stress", "tension", "ghabrahat", "pareshan"],
            "lonely": ["lonely", "alone", "isolated", "abandoned", "akela", "tanhai"],
            "overwhelmed": ["overwhelmed", "too much", "can't handle", "burden", "pressure", "bahut zyada"]
        }
        
        # Crisis keywords for safety detection
        self.crisis_keywords = {
            "suicide": ["kill myself", "suicide", "end my life", "want to die", "mar jana", "jeena nahi"],
            "self_harm": ["hurt myself", "cut myself", "harm myself", "blade", "nuksan pahunchana"],
            "violence": ["kill someone", "hurt others", "violence", "fight", "maar dena"],
            "abuse": ["abuse", "violence at home", "hitting", "beating", "ghar mein violence"]
        }
        
        # Response templates
        self.responses = {
            "happy": [
                "I'm so glad to hear you're feeling happy! That's wonderful. What's bringing you joy today?",
                "Your happiness is infectious! It's great to see you in such a positive mood.",
                "Khushi ki baat hai! It's beautiful to hear you're feeling so good."
            ],
            "sad": [
                "I'm sorry you're feeling sad. It's okay to feel this way sometimes. Would you like to talk about what's bothering you?",
                "I hear that you're going through a difficult time. Remember, it's okay to not be okay. I'm here to listen.",
                "Dukh ki baat hai, but please know that these feelings will pass. You're not alone."
            ],
            "angry": [
                "I can sense your anger. It's a natural emotion, but let's work on channeling it constructively. What triggered this feeling?",
                "Anger can be overwhelming. Take a deep breath with me. Let's talk about what's making you feel this way.",
                "Gussa aana natural hai, but let's find healthy ways to deal with it."
            ],
            "anxious": [
                "I understand you're feeling anxious. Let's try some grounding techniques. Can you name 5 things you can see around you?",
                "Anxiety can be really difficult. Remember to breathe deeply. You're safe right now.",
                "Ghabrahat ho rahi hai? Let's practice some breathing exercises together."
            ],
            "lonely": [
                "Feeling lonely is hard, but remember you're not truly alone. I'm here with you, and there are people who care.",
                "Loneliness can feel overwhelming, but it's temporary. Would you like to talk about connecting with others?",
                "Akela feel kar rahe hain? Remember, reaching out for help is a sign of strength."
            ],
            "overwhelmed": [
                "When everything feels like too much, let's break it down into smaller pieces. What's the most pressing thing right now?",
                "Being overwhelmed is exhausting. Let's prioritize what really needs your attention today.",
                "Bahut zyada lag raha hai? Let's take it one step at a time."
            ]
        }
        
        # Crisis responses
        self.crisis_responses = {
            "suicide": "🚨 I'm very concerned about you. Please reach out to a crisis helpline immediately: National Suicide Prevention Lifeline: 988 (US) or AASRA: 91-9820466726 (India). Your life has value.",
            "self_harm": "🚨 I'm worried about your safety. Please consider reaching out to a mental health professional or crisis helpline. You deserve support and care.",
            "violence": "🚨 If you're having thoughts of harming others, please contact emergency services or a mental health crisis line immediately.",
            "abuse": "🚨 If you're experiencing abuse, please contact local authorities or a domestic violence helpline. Your safety is important."
        }

    def detect_emotion(self, text: str) -> Dict:
        """Simple emotion detection based on keywords"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if not emotion_scores:
            return {"primary_emotion": "neutral", "confidence": 0.5, "multiple_emotions": {"neutral": 0.5}}
        
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        confidence = min(primary_emotion[1] * 0.3, 1.0)  # Simple confidence calculation
        
        return {
            "primary_emotion": primary_emotion[0],
            "confidence": confidence,
            "multiple_emotions": emotion_scores
        }

    def assess_crisis_risk(self, text: str) -> Dict:
        """Simple crisis risk assessment"""
        text_lower = text.lower()
        
        for crisis_type, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        "risk_level": "high" if crisis_type in ["suicide", "self_harm"] else "medium",
                        "crisis_type": crisis_type,
                        "needs_intervention": True
                    }
        
        return {"risk_level": "low", "crisis_type": "none", "needs_intervention": False}

    def generate_response(self, text: str) -> Dict:
        """Generate a response based on emotion and crisis detection"""
        emotion_result = self.detect_emotion(text)
        crisis_result = self.assess_crisis_risk(text)
        
        # Handle crisis situations first
        if crisis_result["needs_intervention"]:
            response = self.crisis_responses.get(crisis_result["crisis_type"], "I'm concerned about your wellbeing. Please consider reaching out to a mental health professional.")
        else:
            # Generate normal emotional support response
            primary_emotion = emotion_result["primary_emotion"]
            responses = self.responses.get(primary_emotion, ["I hear you. Would you like to tell me more about how you're feeling?"])
            response = responses[0]  # Use first response for simplicity
        
        return {
            "response": response,
            "emotion": emotion_result,
            "crisis_assessment": crisis_result,
            "timestamp": datetime.now().isoformat()
        }

def run_demo_examples():
    """Run the assistant with various example inputs"""
    assistant = SimplifiedMentalHealthAssistant()
    
    # Test cases covering different scenarios
    test_cases = [
        # English emotions
        "I'm feeling really happy today! Got a promotion at work!",
        "I'm so depressed and can't get out of bed",
        "I'm furious about what happened at the office",
        "I'm worried about my exam results next week",
        "I feel so alone in this world, nobody understands me",
        "Everything feels too much to handle right now",
        
        # Hindi/Hinglish expressions
        "Bahut khush hun aaj, sab kuch achha chal raha hai",
        "Bohot udaas feel kar raha hun, kuch achha nahi lag raha",
        "Gussa aa raha hai, office mein bohot tension hai",
        "Ghabrahat ho rahi hai exam ke liye",
        "Akela feel kar raha hun, koi nahi hai saath mein",
        
        # Cultural expressions
        "Dil mein bhari hai aaj",
        "Dil garden garden ho gaya promotion ke baad",
        "Sar mein bohot tension chal rahi hai",
        
        # Crisis situations (for safety testing)
        "I want to end my life, can't take it anymore",
        "Mujhe jeena nahi hai, mar jana chahta hun",
        "I'm going to hurt myself with this knife",
        
        # Normal conversation
        "How are you today?",
        "Tell me about mental health",
        "I'm having a normal day, nothing special"
    ]
    
    print("🧠 AI Mental Health Voice Assistant - Simplified Demo")
    print("=" * 60)
    print("This demo showcases emotion detection, crisis assessment, and supportive responses")
    print("Testing with various English and Hindi/Hinglish expressions\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"📝 Example {i}: \"{test_input}\"")
        
        result = assistant.generate_response(test_input)
        
        print(f"🎭 Detected Emotion: {result['emotion']['primary_emotion']} (confidence: {result['emotion']['confidence']:.2f})")
        
        if result['emotion']['multiple_emotions']:
            emotions_str = ", ".join([f"{emotion}: {score}" for emotion, score in result['emotion']['multiple_emotions'].items()])
            print(f"   Multiple emotions: {emotions_str}")
        
        print(f"⚠️  Crisis Risk: {result['crisis_assessment']['risk_level']}")
        if result['crisis_assessment']['needs_intervention']:
            print(f"   Crisis Type: {result['crisis_assessment']['crisis_type']}")
        
        print(f"🤖 Response: {result['response']}")
        print("-" * 60)
        print()

if __name__ == "__main__":
    run_demo_examples()