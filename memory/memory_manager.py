import json
import os
from datetime import datetime

# File where memory will be stored
MEMORY_FILE = "memory/conversation_memory.json"

# Initialize memory file if it doesn’t exist
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": []}, f)


def add_to_memory(user_message, bot_reply, emotion=None):
    """Add a new interaction to memory"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["messages"].append({
        "user": user_message,
        "bot": bot_reply,
        "emotion": emotion,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # keep only last 10 interactions
    data["messages"] = data["messages"][-10:]

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_context():
    """Return last few messages for context"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    last_msgs = data["messages"][-3:]  # last 3 messages
    context = ""
    for msg in last_msgs:
        context += f"User: {msg['user']}\nBot: {msg['bot']}\n"

    return context


def get_recent_emotions():
    """Return last 3 emotions"""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [m["emotion"] for m in data["messages"][-3:] if m.get("emotion")]


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
