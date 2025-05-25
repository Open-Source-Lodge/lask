#!/usr/bin/env python3
"""
lask: A CLI tool to prompt ChatGPT and other LLMs from the terminal.
Usage:
    lask "Your prompt here"
This is a minimal implementation using OpenAI's API. Set your API key in the OPENAI_API_KEY environment variable
or in the ~/.lask-config file.
"""
import os
import sys
import configparser
import requests
from pathlib import Path

def load_config():
    """Load configuration from ~/.lask-config if it exists."""
    config_path = Path.home() / ".lask-config"
    config = {}
    
    if config_path.exists():
        try:
            parser = configparser.ConfigParser()
            parser.read(config_path)
            
            if 'default' in parser:
                for key, value in parser['default'].items():
                    config[key] = value
                    
        except configparser.Error:
            print(f"Warning: Could not parse {config_path}. Using default configuration.")
        except Exception as e:
            print(f"Warning: Error reading {config_path}: {e}. Using default configuration.")
            
    return config

def main():
    if len(sys.argv) < 2:
        print("Usage: lask 'Your prompt here'")
        sys.exit(1)

    # Load config from file
    config = load_config()

    prompt = " ".join(sys.argv[1:])
    # Try to get API key from environment variable first, then from config
    api_key = os.getenv("OPENAI_API_KEY") or config.get("api_key")
    if not api_key:
        print("Error: Please set the OPENAI_API_KEY environment variable or add 'api_key' under [default] section in ~/.lask-config")
        sys.exit(1)

    # Get model from config or use default
    model = config.get("model", "gpt-4.1")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    print(f"Prompting OpenAI API with: {prompt}\n")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)
    result = response.json()
    print(result["choices"][0]["message"]["content"].strip())

if __name__ == "__main__":
    main()
