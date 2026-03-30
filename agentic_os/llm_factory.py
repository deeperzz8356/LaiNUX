"""
LLM Factory for LaiNUX OS
Centralizes model creation.
Now reverting back to the official Mistral AI API for native, stable access.
"""
import os
from langchain_mistralai import ChatMistralAI


# ============================================================
# MISTRAL AI MODEL SELECTION
# Free API keys available at: https://console.mistral.ai/api-keys/
# ============================================================
# 
# FREE TIER OPTIONS:
# "mistral-small-latest"   <- Good for reasoning / planning
# "open-mistral-7b"        <- Very fast free loop agent
#
# PAID TIER OPTIONS:
# "mistral-large-latest"   <- Best overall intelligence
# "codestral-latest"       <- Best for coding / tool creation
# ============================================================

DEFAULT_REASONING_MODEL = os.getenv("LLM_MODEL", "mistral-small-latest")
DEFAULT_FAST_MODEL = os.getenv("FAST_LLM_MODEL", "open-mistral-7b")

def create_reasoning_llm() -> ChatMistralAI:
    """Creates the best available model for planning, critic, and evolving."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key or "YOUR_" in api_key:
        raise ValueError("MISTRAL_API_KEY is missing! Get one from console.mistral.ai")

    return ChatMistralAI(
        model=DEFAULT_REASONING_MODEL,
        mistral_api_key=api_key,
        temperature=0.3
    )

def create_fast_llm() -> ChatMistralAI:
    """Creates a fast, cheap model for the executor loops."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key or "YOUR_" in api_key:
        raise ValueError("MISTRAL_API_KEY is missing! Get one from console.mistral.ai")

    return ChatMistralAI(
        model=DEFAULT_FAST_MODEL,
        mistral_api_key=api_key,
        temperature=0.2
    )

