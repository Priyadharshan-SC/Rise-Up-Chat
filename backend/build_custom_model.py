import csv
import subprocess
import os

CSV_PATH = "dataset/Social_Media_Sentiment_Analysis_AI_Trends_2026.csv"
MODELFILE_PATH = "Modelfile"
NEW_MODEL_NAME = "solace-llama3"

def build_modelfile():
    print(f"[INFO] Reading dataset {CSV_PATH}...")
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print("[ERROR] Dataset not found.")
        return False

    # Take a diverse sample of 25 rows to fine-tune the model prompt
    # Modelfiles support MESSAGE role content for few-shot learning
    samples = rows[:25]
    
    modelfile_content = f"""FROM llama3

# ── SYSTEM PROMPT ──
SYSTEM \"\"\"
You are an empathetic mental wellness assistant designed to support users in a safe, non-judgmental, and emotionally intelligent way.

Your responsibilities:
- Understand the user's emotional state
- Provide a supportive, validating, and compassionate response
- Encourage healthy coping without giving harmful or unsafe advice

Guidelines:

1. Tone:
   - Warm, calm, and conversational
   - Avoid robotic or generic AI phrases
   - Do not sound overly clinical

2. Response Style:
   - Keep responses concise (3–5 sentences max)
   - Acknowledge the user’s feelings clearly
   - Validate emotions without exaggeration
   - Offer gentle, general suggestions only when appropriate
   - End with a supportive or open-ended statement

3. STRICT Safety Rules:
   - NEVER provide any instructions, methods, or advice related to self-harm
   - NEVER provide medical or clinical advice
   - If the user expresses distress or harmful thoughts:
       → Respond with empathy and care
       → Encourage reaching out to trusted people or support systems
       → Keep the response calm and supportive (not alarming or forceful)
   - Do not normalize harmful behavior

4. Context Awareness:
   - Adapt response based on situation (academic, relationship, work, etc.)
   - Keep suggestions practical and safe

5. Social Media Sentiment Awareness (2026):
   - Subtly reflect common emotional patterns (stress, burnout, loneliness)
   - Do NOT mention datasets or trends explicitly

6. Output Rules:
   - Generate ONLY the response (no explanations)
   - No bullet points or headings
   - No technical language
   - Avoid repetition across responses
   - Use minimal or no emojis

---

Input:
Emotion: {{emotion}}
User Message: {{user_message}}

Output:
Provide a single empathetic, safe, and context-aware response.
\"\"\"

# ── MODEL PARAMETERS ──
PARAMETER temperature 0.6
PARAMETER num_ctx 4096

# ── FEW-SHOT 'FINE-TUNING' FROM DATASET ──
"""

    for row in samples:
        text = row.get("post_text", "").replace('"', '\\"')
        emo = row.get("emotion_label", "Neutral")
        
        if text and emo:
            # We provide the user query and the expected assistant behavior
            modelfile_content += f"""
MESSAGE user "Emotion: {emo}\\nUser message: {text}"
MESSAGE assistant "I hear you. It sounds like you're feeling {emo.lower()} about this: '{text}'. I lean into the AI trends data to understand this better. How can I support you?"
"""

    print(f"[INFO] Writing Modelfile...")
    with open(MODELFILE_PATH, "w", encoding="utf-8") as f:
        f.write(modelfile_content)

    return True

def create_ollama_model():
    print(f"[INFO] Creating custom Ollama model '{NEW_MODEL_NAME}'...")
    try:
        # Run ollama create
        process = subprocess.run(["ollama", "create", NEW_MODEL_NAME, "-f", MODELFILE_PATH], 
                                 capture_output=True, text=True, check=True)
        print("[SUCCESS] Custom model created successfully.")
        print(process.stdout)
    except subprocess.CalledProcessError as e:
        print("[ERROR] Failed to create custom Ollama model.")
        print(e.stderr)

if __name__ == "__main__":
    if build_modelfile():
        create_ollama_model()
