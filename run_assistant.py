#!/usr/bin/env python3
"""
Startup script for the Enhanced Mental Health Voice Assistant
Handles initialization, dependency checks, and graceful startup
"""

import sys
import os
import subprocess
import importlib

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'transformers', 'torch', 'nltk', 'speechrecognition', 
        'pyttsx3', 'vosk', 'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing dependencies: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_vosk_model():
    """Check if Vosk model is available"""
    model_path = os.path.join("data", "models", "vosk-model-small-en-us-0.15")
    if os.path.exists(model_path):
        print("✅ Vosk speech model found")
        return True
    else:
        print("❌ Vosk speech model not found")
        print("Please download it from: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        print("Extract to: data/models/")
        return False

def initialize_nltk():
    """Initialize NLTK data if needed"""
    try:
        import nltk
        try:
            nltk.data.find('vader_lexicon')
            print("✅ NLTK VADER lexicon available")
        except LookupError:
            print("📥 Downloading NLTK VADER lexicon...")
            nltk.download('vader_lexicon', quiet=True)
            print("✅ NLTK VADER lexicon downloaded")
        
        try:
            nltk.data.find('punkt')
            print("✅ NLTK punkt tokenizer available")
        except LookupError:
            print("📥 Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
            print("✅ NLTK punkt tokenizer downloaded")
        
        return True
    except Exception as e:
        print(f"❌ NLTK initialization error: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/voice_notes",
        "data/conversations", 
        "data/models",
        "memory"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directory structure verified")

def main():
    """Main startup function"""
    print("🧠 Enhanced Mental Health Voice Assistant - Startup")
    print("=" * 50)
    
    # System checks
    check_python_version()
    
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    create_directories()
    
    if not initialize_nltk():
        print("\n❌ NLTK initialization failed.")
        sys.exit(1)
    
    # Vosk model check (optional - system can work without speech recognition)
    if not check_vosk_model():
        print("\n⚠️ Warning: Speech recognition may not work without Vosk model")
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🚀 Starting Enhanced Mental Health Voice Assistant...")
    print("=" * 50)
    
    # Import and run the main application
    try:
        import main
        print("✅ Application started successfully!")
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()