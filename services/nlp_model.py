import os
import re
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# ---- Model selection ----
try:
    from config import MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE, TOP_P, TOP_K, REPETITION_PENALTY
except Exception:
    MODEL_NAME = os.getenv("NLP_MODEL_NAME", "microsoft/DialoGPT-medium")
    MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "160"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P = float(os.getenv("TOP_P", "0.92"))
    TOP_K = int(os.getenv("TOP_K", "50"))
    REPETITION_PENALTY = float(os.getenv("REPETITION_PENALTY", "1.15"))

FALLBACK_MODEL = "distilgpt2"

def _load_pipeline(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(model_name)
    gen = pipeline("text-generation", model=mdl, tokenizer=tok)
    return gen, tok

try:
    generator, tokenizer = _load_pipeline(MODEL_NAME)
except Exception:
    generator, tokenizer = _load_pipeline(FALLBACK_MODEL)

SYSTEM_STYLE = (
    "You are a supportive, non-judgmental mental health voice assistant. "
    "Be concise, warm, and empathetic. Avoid medical diagnosis or prescriptions. "
    "Encourage reflection, offer gentle coping strategies, and suggest professional help "
    "for severe or crisis situations. Keep responses under 4 sentences."
)

FEW_SHOTS = [
    ("User: I'm feeling really low today.\nAssistant:",
     "I’m really sorry you’re feeling this way. Do you want to share what made today tough? "
     "We can take it one step at a time together."),
    ("User: I’m so stressed about work.\nAssistant:",
     "That sounds overwhelming. What part of work is weighing on you most right now? "
     "We can try a small, doable next step."),
]

def _build_prompt(user_text: str, context: Optional[str]) -> str:
    ctx = (context or "").strip()
    few_shot_block = "\n\n".join(s + " " + r for s, r in FEW_SHOTS)
    prompt = (
        f"System: {SYSTEM_STYLE}\n"
        f"{('Context: ' + ctx + '\n') if ctx else ''}"
        f"{few_shot_block}\n\n"
        f"User: {user_text}\nAssistant:"
    )
    return prompt

def _postprocess(generated: str) -> str:
    if "Assistant:" in generated:
        generated = generated.split("Assistant:")[-1]
    generated = generated.split("\nUser:")[0].strip()
    generated = re.sub(r'\s+', ' ', generated).strip()
    return generated

# 🔥 Final Unified Function
def generate_reply(user_text: str, context: str = "", emotion: str = "neutral") -> str:
    prompt = _build_prompt(user_text, context)
    outputs = generator(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        repetition_penalty=REPETITION_PENALTY,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
        truncation=True,
    )

    raw = outputs[0]["generated_text"]
    reply = _postprocess(raw)

    if not reply:
        reply = "I’m here with you. Would you like to tell me a bit more about what’s on your mind?"

    # 🎯 Emotion-sensitive adjustment
    if emotion == "happy":
        reply = f"{reply} 😊 That’s wonderful to hear!"
    elif emotion == "sad":
        reply = f"{reply} 💙 I’m here for you, take your time."
    elif emotion == "angry":
        reply = f"{reply} 😔 I understand it’s frustrating. Let’s take a deep breath together."

    return reply
