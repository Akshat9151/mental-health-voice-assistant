import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# ------------------ Setup ------------------
MODEL_PATH = os.path.join(os.getcwd(), "data", "models", "vosk-model-small-en-us-0.15")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

# Load Vosk model
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8000
)
stream.start_stream()


# ------------------ Speech to Text Function ------------------
def transcribe_speech():
    print("🎤 Listening... Speak something!")

    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):  
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()

            if text:  
                print(f"✅ You said: {text}")
                return text   # Exit after first detected sentence

        else:
            # Partial results (while still speaking)
            partial = json.loads(recognizer.PartialResult())
            if partial.get("partial"):
                print(f"... {partial['partial']}", end="\r")


# ------------------ Run ------------------
if __name__ == "__main__":
    while True:
        text = transcribe_speech()

        if text.lower() in ["exit", "quit", "stop"]:
            print("👋 Exiting...")
            break
