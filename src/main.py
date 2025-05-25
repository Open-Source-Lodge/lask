#!/usr/bin/env python3
"""
lask: A CLI tool to prompt ChatGPT and other LLMs from the terminal.
Usage:
    lask Your prompt here
This tool supports multiple LLM providers including OpenAI, Anthropic, and AWS Bedrock.
Configure your API keys and preferences in the ~/.lask-config file.
"""
import sys
import configparser
from pathlib import Path
from typing import Dict, Any, List

from src.providers import call_provider_api

def load_config() -> Dict[str, Any]:
    """
    Load configuration from ~/.lask-config if it exists.
    
    Returns:
        Dict[str, Any]: A dictionary containing the configuration.
    """
    config_path = Path.home() / ".lask-config"
    # Fallback configuration
    config: Dict[str, Any] = {
        'provider': 'openai',  # Fallback provider
        'model': 'gpt-4.1',    # Fallback model
        'providers': {}        # Provider-specific configs
    }

    if config_path.exists():
        try:
            parser = configparser.ConfigParser()
            parser.read(config_path)

            # Load default section
            if 'default' in parser:
                for key, value in parser['default'].items():
                    config[key] = value

            # Load provider-specific sections
            for section in parser.sections():
                if section != 'default':
                    config['providers'][section] = dict(parser[section])

        except configparser.Error:
            print(f"Warning: Could not parse {config_path}. Using default configuration.")
        except Exception as e:
            print(f"Warning: Error reading {config_path}: {e}. Using default configuration.")

    return config

def main() -> None:
    """
    Main entry point for the lask CLI tool.
    Parses command line arguments, loads configuration,
    and calls the appropriate provider API.
    """
    if len(sys.argv) < 2:
        print("Usage: lask 'Your prompt here'")
        sys.exit(1)

    # Load config from file
    config: Dict[str, Any] = load_config()

    # Get the prompt from command line arguments
    prompt: str = " ".join(sys.argv[1:])

    # Determine which provider to use
    provider: str = config.get("provider", "openai").lower()

    # List of supported providers
    supported_providers: List[str] = ["openai", "anthropic", "aws", "azure"]
    
    if provider not in supported_providers:
        print(f"Error: Unsupported provider '{provider}'. Supported providers are: {', '.join(supported_providers)}")
        sys.exit(1)

    try:
        # Call the appropriate API based on the provider using the provider modules
        result: str = call_provider_api(provider, config, prompt)
        print(result)
    except ImportError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()