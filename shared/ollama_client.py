import requests
import json
import logging
from .settings import settings

def call_ollama(prompt: str, model: str = None) -> str:
    """
    Calls the Ollama /api/generate endpoint.
    """
    if not settings.OLLAMA_BASE_URL:
        raise ValueError("OLLAMA_BASE_URL is not configured")
        
    model = model or settings.OLLAMA_MODEL
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama call failed: {e}")
        raise e
