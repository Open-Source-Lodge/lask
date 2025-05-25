"""
Anthropic provider module for lask
"""
import os
import sys
import requests

def call_api(config, prompt):
    """Call the Anthropic API with the given prompt."""
    # Check if we have provider-specific config
    anthropic_config = {}
    if 'providers' in config and 'anthropic' in config['providers']:
        anthropic_config = config['providers']['anthropic']

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY") or anthropic_config.get("api_key") or config.get("api_key")
    if not api_key:
        print("Error: Please set the ANTHROPIC_API_KEY environment variable or add 'api_key' under [anthropic] section in ~/.lask-config")
        sys.exit(1)

    # Get model (Claude by default)
    model = anthropic_config.get("model", "claude-3-opus-20240229")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": int(anthropic_config.get("max_tokens", 4096))
    }

    if 'temperature' in anthropic_config:
        data['temperature'] = float(anthropic_config['temperature'])

    print(f"Prompting Anthropic API with model {model}: {prompt}\n")
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)
    result = response.json()
    return result["content"][0]["text"]