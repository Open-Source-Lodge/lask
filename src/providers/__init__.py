"""
Provider modules for lask
"""
from importlib import import_module
from typing import Dict, Any, cast
from types import ModuleType

def get_provider_module(provider_name: str) -> ModuleType:
    """
    Dynamically import and return the provider module based on provider name.
    
    Args:
        provider_name (str): The name of the provider (e.g., 'openai', 'anthropic', 'aws', 'azure')
    
    Returns:
        ModuleType: The imported provider module
    
    Raises:
        ImportError: If the provider module cannot be imported
    """
    try:
        return import_module(f"src.providers.{provider_name}")
    except ImportError:
        raise ImportError(f"Provider '{provider_name}' is not supported. Make sure the module exists.")

def call_provider_api(provider_name: str, config: Dict[str, Any], prompt: str) -> str:
    """
    Call the appropriate provider API based on the provider name.
    
    Args:
        provider_name (str): The name of the provider
        config (Dict[str, Any]): Configuration dictionary
        prompt (str): The user prompt
    
    Returns:
        str: The response from the provider
    
    Raises:
        ImportError: If the provider is not supported
    """
    provider_module = get_provider_module(provider_name)
    return cast(str, provider_module.call_api(config, prompt))