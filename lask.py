#!/usr/bin/env python3
"""
lask: A CLI tool to prompt ChatGPT and other LLMs from the terminal.
Usage:
    lask Your prompt here
    echo "Your prompt here" | lask
This tool supports multiple LLM providers including OpenAI, Anthropic, AWS Bedrock, and Azure.
Configure your API keys and preferences in the ~/.lask-config file.
"""

from src.main import main

if __name__ == "__main__":
    main()
