#!/usr/bin/env python3
"""
lask: A CLI tool to prompt ChatGPT and other LLMs from the terminal.
Usage:
    lask Your prompt here
This tool supports multiple LLM providers including OpenAI, Anthropic, and AWS Bedrock.
Configure your API keys and preferences in the ~/.lask-config file.
"""
import os
import sys
import json
import configparser
import requests
from pathlib import Path

def load_config():
    """Load configuration from ~/.lask-config if it exists."""
    config_path = Path.home() / ".lask-config"
    # Default configuration
    config = {
        'provider': 'openai',  # Default provider
        'model': 'gpt-4.1',    # Default model
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

def call_openai_api(config, prompt):
    """Call the OpenAI API with the given prompt."""
    # Try to get API key from environment variable first, then from config
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please add 'api_key' under [default] or [openai] section in ~/.lask-config, or set the OPENAI_API_KEY environment variable in your shell.")
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

    # Check if there are any OpenAI-specific configurations
    if 'providers' in config and 'openai' in config['providers']:
        openai_config = config['providers']['openai']
        if 'model' in openai_config:
            data['model'] = openai_config['model']
        if 'temperature' in openai_config:
            data['temperature'] = float(openai_config['temperature'])
        if 'max_tokens' in openai_config:
            data['max_tokens'] = int(openai_config['max_tokens'])

    print(f"Prompting OpenAI API with model {data['model']}: {prompt}\n")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def call_anthropic_api(config, prompt):
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

def call_aws_bedrock_api(config, prompt):
    """Call the AWS Bedrock API with the given prompt."""
    # We import boto3 only when needed to avoid requiring it for users who don't use AWS
    try:
        import boto3
    except ImportError:
        print("Error: boto3 is required for AWS Bedrock.")
        print("Install it with: pip install boto3")
        print("Or install lask with AWS support: pip install lask[aws]")
        sys.exit(1)

    # Check if we have provider-specific config
    aws_config = {}
    if 'providers' in config and 'aws' in config['providers']:
        aws_config = config['providers']['aws']

    # Get the model ID
    model_id = aws_config.get("model_id", "anthropic.claude-3-sonnet-20240229-v1:0")
    region = aws_config.get("region", "us-east-1")

    # Create a Bedrock Runtime client
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=region
    )

    # Prepare the request body based on the model provider
    if "anthropic" in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": int(aws_config.get("max_tokens", 4096)),
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        if 'temperature' in aws_config:
            body['temperature'] = float(aws_config['temperature'])
    elif "amazon" in model_id:
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": int(aws_config.get("max_tokens", 4096))
            }
        }
        if 'temperature' in aws_config:
            body['textGenerationConfig']['temperature'] = float(aws_config['temperature'])
    else:
        # Default format for other models
        body = {
            "prompt": prompt,
            "max_tokens": int(aws_config.get("max_tokens", 4096))
        }
        if 'temperature' in aws_config:
            body['temperature'] = float(aws_config['temperature'])

    print(f"Prompting AWS Bedrock with model {model_id}: {prompt}\n")
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        response_body = json.loads(response.get('body').read())

        # Extract the content based on the model provider
        if "anthropic" in model_id:
            return response_body.get('content')[0]['text']
        elif "amazon" in model_id:
            return response_body.get('results')[0]['outputText']
        else:
            return response_body.get('completion', response_body.get('generated_text', str(response_body)))
    except Exception as e:
        print(f"Error calling AWS Bedrock: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: lask 'Your prompt here'")
        sys.exit(1)

    # Load config from file
    config = load_config()

    # Get the prompt from command line arguments
    prompt = " ".join(sys.argv[1:])

    # Determine which provider to use
    provider = config.get("provider", "openai").lower()

    # Call the appropriate API based on the provider
    if provider == "openai":
        result = call_openai_api(config, prompt)
    elif provider == "anthropic":
        result = call_anthropic_api(config, prompt)
    elif provider == "aws":
        result = call_aws_bedrock_api(config, prompt)
    else:
        print(f"Error: Unsupported provider '{provider}'. Supported providers are: openai, anthropic, aws")
        sys.exit(1)

    print(result)

if __name__ == "__main__":
    main()
