"""
emotion.py
----------
Emotion detection service for Solace AI.

Replaces the rule-based keyword matcher with a HuggingFace text-classification 
pipeline using the 'j-hartmann/emotion-english-distilroberta-base' model.
"""

import os
from typing import Dict, Any, List, Union
from transformers import pipeline

# ---------------------------------------------------------------------------
# Globals and Model Loading
# ---------------------------------------------------------------------------

# Label mapping to transform the model's 7 labels to the system's 5 labels
LABEL_MAPPING = {
    "sadness": "sad",
    "joy": "happy",
    "anger": "angry",
    "fear": "anxious",
    "surprise": "neutral",
    "neutral": "neutral",
    "disgust": "angry"
}

_DEFAULT_EMOTION = "neutral"

# Load the model globally so it isn't re-initialized on every request.
# top_k=1 ensures we only get the highest confidence label.
try:
    print("[INFO] Loading Hugging Face text-classification pipeline...")
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1
    )
    print("[INFO] Emotion pipeline loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load emotion pipeline: {e}")
    emotion_classifier = None


def detect_emotion(text: str) -> Dict[str, Any]:
    """
    Classify the dominant emotion expressed in *text* using a HuggingFace Transformer.

    Args:
        text: The raw user input string.

    Returns:
        dict: A dictionary containing:
              - 'emotion': the mapped emotion string ("sad", "anxious", "angry", "happy", "neutral").
              - 'confidence': a float between 0.0 and 1.0 representing model confidence.
    """
    # 1. Normalize input (strip whitespace, lowercase)
    normalized_text = text.strip().lower()

    # Base case - if model failed to load or text is empty
    if emotion_classifier is None or not normalized_text:
        return {"emotion": _DEFAULT_EMOTION, "confidence": 0.0}

    try:
        # 2. Run model classification
        output: Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]] = emotion_classifier(normalized_text)
        
        # 3. Handle model output safely (handle both single and list of lists formats)
        prediction = None
        if isinstance(output, list) and len(output) > 0:
            if isinstance(output[0], list) and len(output[0]) > 0:
                prediction = output[0][0]
            elif isinstance(output[0], dict):
                prediction = output[0]
                
        if prediction is not None:
            raw_label = prediction.get("label", "neutral")
            confidence = prediction.get("score", 0.0)
        else:
            raw_label = "neutral"
            confidence = 0.0

        # 4. Map the raw label to system label
        mapped_emotion = LABEL_MAPPING.get(raw_label, _DEFAULT_EMOTION)
        
        # 5. Debug printing
        print(f"[DEBUG] Emotion: {mapped_emotion}, Confidence: {confidence}")
        
        return {
            "emotion": mapped_emotion,
            "confidence": confidence
        }

    except Exception as e:
        print(f"[ERROR] Emotion classification failed: {e}")
        return {"emotion": _DEFAULT_EMOTION, "confidence": 0.0}
