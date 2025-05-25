"""
Provider modules for lask
"""
from importlib import import_module

def get_provider_module(provider_name):
    """
    Dynamically import and return the provider module based on provider name.
    
    Args:
        provider_name (str): The name of the provider (e.g., 'openai', 'anthropic', 'aws', 'azure')
    
    Returns:
        module: The imported provider module
    
    Raises:
        ImportError: If the provider module cannot be imported
    """
    try:
        return import_module(f"src.providers.{provider_name}")
    except ImportError:
        raise ImportError(f"Provider '{provider_name}' is not supported. Make sure the module exists.")

def call_provider_api(provider_name, config, prompt):
    """
    Call the appropriate provider API based on the provider name.
    
    Args:
        provider_name (str): The name of the provider
        config (dict): Configuration dictionary
        prompt (str): The user prompt
    
    Returns:
        str: The response from the provider
    
    Raises:
        ImportError: If the provider is not supported
    """
    provider_module = get_provider_module(provider_name)
    return provider_module.call_api(config, prompt)