"""
Azure OpenAI provider module for lask
"""
import os
import sys
import requests

def call_api(config, prompt):
    """Call the Azure OpenAI API with the given prompt."""
    # Check if we have provider-specific config
    azure_config = {}
    if 'providers' in config and 'azure' in config['providers']:
        azure_config = config['providers']['azure']

    # Get API key
    api_key = os.getenv("AZURE_OPENAI_API_KEY") or azure_config.get("api_key") or config.get("api_key")
    if not api_key:
        print("Error: Please set the AZURE_OPENAI_API_KEY environment variable or add 'api_key' under [azure] section in ~/.lask-config")
        sys.exit(1)

    # Get required Azure-specific parameters
    resource_name = azure_config.get("resource_name")
    if not resource_name:
        print("Error: Please set 'resource_name' under [azure] section in ~/.lask-config")
        sys.exit(1)

    deployment_id = azure_config.get("deployment_id")
    if not deployment_id:
        print("Error: Please set 'deployment_id' under [azure] section in ~/.lask-config")
        sys.exit(1)

    api_version = azure_config.get("api_version", "2023-05-15")

    # Construct the API URL
    endpoint = f"https://{resource_name}.openai.azure.com/openai/deployments/{deployment_id}/chat/completions?api-version={api_version}"

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    # Add optional parameters if specified
    if 'temperature' in azure_config:
        data['temperature'] = float(azure_config['temperature'])
    if 'max_tokens' in azure_config:
        data['max_tokens'] = int(azure_config['max_tokens'])

    print(f"Prompting Azure OpenAI API with deployment {deployment_id}: {prompt}\n")
    response = requests.post(
        endpoint,
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        sys.exit(1)
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()