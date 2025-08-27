#!/usr/bin/env python3
"""
Setup script for the Enhanced Mental Health Voice Assistant
Handles installation of dependencies and initial setup
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

def run_command(command, description):
    """Run a system command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def download_vosk_model():
    """Download and extract Vosk speech model"""
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_dir = "data/models"
    model_zip = "vosk-model.zip"
    
    # Create models directory
    os.makedirs(model_dir, exist_ok=True)
    
    # Check if model already exists
    if os.path.exists(os.path.join(model_dir, "vosk-model-small-en-us-0.15")):
        print("✅ Vosk model already exists")
        return True
    
    try:
        print("📥 Downloading Vosk speech model (this may take a while)...")
        urllib.request.urlretrieve(model_url, model_zip)
        
        print("📦 Extracting Vosk model...")
        with zipfile.ZipFile(model_zip, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
        
        # Clean up zip file
        os.remove(model_zip)
        
        print("✅ Vosk model downloaded and extracted")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download Vosk model: {e}")
        print("You can manually download it from:")
        print("https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        return False

def setup_nltk():
    """Setup NLTK data"""
    try:
        import nltk
        print("📥 Downloading NLTK data...")
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded")
        return True
    except Exception as e:
        print(f"❌ NLTK setup failed: {e}")
        return False

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "data/voice_notes",
        "data/conversations",
        "data/models", 
        "memory"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directory structure created")

def main():
    """Main setup function"""
    print("🧠 Enhanced Mental Health Voice Assistant - Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Create directories
    create_directory_structure()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup NLTK
    if not setup_nltk():
        print("⚠️ NLTK setup failed, but continuing...")
    
    # Download Vosk model
    if not download_vosk_model():
        print("⚠️ Vosk model download failed, speech recognition may not work")
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\nTo run the assistant:")
    print("  python3 run_assistant.py")
    print("\nOr directly:")
    print("  python3 main.py")
    print("\nTo test the system:")
    print("  python3 test_system.py")

if __name__ == "__main__":
    main()