"""
Azure OpenAI provider module for lask
"""

import os
import sys
from typing import Dict, Any, Optional
import requests

from src.config import LaskConfig


def call_api(config: LaskConfig, prompt: str) -> str:
    """
    Call the Azure OpenAI API with the given prompt.

    Args:
        config (LaskConfig): Configuration object
        prompt (str): The user prompt

    Returns:
        str: The response from the Azure OpenAI API

    Raises:
        Exception: If there's an error calling the Azure OpenAI API
    """
    # Get provider-specific config
    azure_config = config.get_provider_config("azure")

    # Get API key
    api_key: Optional[str] = (
        os.getenv("AZURE_OPENAI_API_KEY") or azure_config.api_key
    )
    if not api_key:
        print(
            "Error: Please set the AZURE_OPENAI_API_KEY environment variable or add 'api_key' under [azure] section in ~/.lask-config"
        )
        sys.exit(1)

    # Get required Azure-specific parameters
    resource_name: Optional[str] = azure_config.resource_name
    if not resource_name:
        print(
            "Error: Please set 'resource_name' under [azure] section in ~/.lask-config"
        )
        sys.exit(1)

    deployment_id: Optional[str] = azure_config.deployment_id
    if not deployment_id:
        print(
            "Error: Please set 'deployment_id' under [azure] section in ~/.lask-config"
        )
        sys.exit(1)

    api_version: str = azure_config.api_version or "2023-05-15"

    # Construct the API URL
    endpoint: str = f"https://{resource_name}.openai.azure.com/openai/deployments/{deployment_id}/chat/completions?api-version={api_version}"

    headers: Dict[str, str] = {"api-key": api_key, "Content-Type": "application/json"}

    data: Dict[str, Any] = {"messages": [{"role": "user", "content": prompt}]}

    # Add optional parameters if specified
    if azure_config.temperature is not None:
        data["temperature"] = azure_config.temperature
    if azure_config.max_tokens is not None:
        data["max_tokens"] = azure_config.max_tokens

    print(f"Prompting Azure OpenAI API with deployment {deployment_id}: {prompt}\n")
    response: requests.Response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)
    result: Dict[str, Any] = response.json()
    return result["choices"][0]["message"]["content"].strip()
