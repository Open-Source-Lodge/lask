"""
Anthropic provider module for lask
"""
import os
import sys
from typing import Dict, Any, Optional
import requests

from src.config import LaskConfig

def call_api(config: LaskConfig, prompt: str) -> str:
    """
    Call the Anthropic API with the given prompt.
    
    Args:
        config (LaskConfig): Configuration object
        prompt (str): The user prompt
        
    Returns:
        str: The response from the Anthropic API
        
    Raises:
        Exception: If there's an error calling the Anthropic API
    """
    # Get provider-specific config
    anthropic_config = config.get_provider_config("anthropic")

    # Get API key
    api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY") or anthropic_config.api_key or config.api_key
    if not api_key:
        print("Error: Please set the ANTHROPIC_API_KEY environment variable or add 'api_key' under [anthropic] section in ~/.lask-config")
        sys.exit(1)

    # Get model (Claude by default)
    model: str = anthropic_config.model or "claude-3-opus-20240229"

    headers: Dict[str, str] = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": anthropic_config.max_tokens or 4096
    }

    if anthropic_config.temperature is not None:
        data['temperature'] = anthropic_config.temperature

    print(f"Prompting Anthropic API with model {model}: {prompt}\n")
    response: requests.Response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)
    result: Dict[str, Any] = response.json()
    return result["content"][0]["text"]