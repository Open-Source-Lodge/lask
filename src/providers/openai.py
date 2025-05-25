"""
OpenAI provider module for lask
"""

import os
import sys
from typing import Dict, Any, Optional
import requests

from src.config import LaskConfig


def call_api(config: LaskConfig, prompt: str) -> str:
    """
    Call the OpenAI API with the given prompt.

    Args:
        config (LaskConfig): Configuration object
        prompt (str): The user prompt

    Returns:
        str: The response from the OpenAI API
    """
    # Get provider-specific config
    openai_config = config.get_provider_config("openai")

    # Try to get API key from environment variable first, then from config
    api_key: Optional[str] = openai_config.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "Error: Please add 'api_key' under [default] or [openai] section in ~/.lask-config, or set the OPENAI_API_KEY environment variable in your shell."
        )
        sys.exit(1)

    # Get model from config or use default
    model: str = openai_config.model or "gpt-4.1"

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Add optional parameters if specified
    if openai_config.temperature is not None:
        data["temperature"] = openai_config.temperature
    if openai_config.max_tokens is not None:
        data["max_tokens"] = openai_config.max_tokens

    print(f"Prompting OpenAI API with model {data['model']}: {prompt}\n")
    response: requests.Response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)

    result: Dict[str, Any] = response.json()
    return result["choices"][0]["message"]["content"].strip()
