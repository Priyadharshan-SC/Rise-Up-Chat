"""
helpers.py
----------
Utility / helper functions shared across the Solace AI backend.

Functions here are intentionally generic so they can support multiple
services without creating circular imports.
"""

import re
from typing import List


def normalise_text(text: str) -> str:
    """
    Lowercase and strip extra whitespace from a string.

    This is used by both the safety checker and the emotion detector
    so that keyword matching is consistent regardless of user casing.

    Args:
        text: Raw input string.

    Returns:
        Cleaned, lowercased string.
    """
    text = text.lower().strip()
    # Collapse multiple spaces/newlines into a single space
    text = re.sub(r"\s+", " ", text)
    return text


def contains_any_keyword(text: str, keywords: List[str]) -> bool:
    """
    Check whether *text* contains at least one keyword from *keywords*.

    Uses whole-word matching to reduce false positives
    (e.g. "stressed" should not match the keyword "stress" unless
    configured to do so — adjust the regex flags as needed).

    Args:
        text:     The normalised input string.
        keywords: A list of keywords to search for.

    Returns:
        True if any keyword is found, False otherwise.
    """
    for keyword in keywords:
        # \b = word boundary for more precise matching
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text):
            return True
    return False


def build_error_response(detail: str, status_code: int = 400) -> dict:
    """
    Build a standardised error payload for HTTP exceptions.

    Args:
        detail:      Human-readable error description.
        status_code: HTTP status code (informational only in the dict).

    Returns:
        Dictionary with 'detail' and 'status_code' keys.
    """
    return {"detail": detail, "status_code": status_code}
