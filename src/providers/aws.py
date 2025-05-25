"""
AWS Bedrock provider module for lask
"""

import sys
import json
from typing import Dict, Any, cast

from src.config import LaskConfig


def call_api(config: LaskConfig, prompt: str) -> str:
    """
    Call the AWS Bedrock API with the given prompt.

    Args:
        config (LaskConfig): Configuration object
        prompt (str): The user prompt

    Returns:
        str: The response from the AWS Bedrock API

    Raises:
        ImportError: If boto3 is not installed
        Exception: If there's an error calling the AWS Bedrock API
    """
    # We import boto3 only when needed to avoid requiring it for users who don't use AWS
    try:
        import boto3
    except ImportError:
        print("Error: boto3 is required for AWS Bedrock.")
        print("Install it with: pip install boto3")
        print("Or install lask with AWS support: pip install lask[aws]")
        sys.exit(1)

    # Get provider-specific config
    aws_config = config.get_provider_config("aws")

    # Get the model ID
    model_id: str = aws_config.model_id or "anthropic.claude-3-sonnet-20240229-v1:0"
    region: str = aws_config.region or "us-east-1"

    # Create a Bedrock Runtime client
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=region)

    # Prepare the request body based on the model provider
    body: Dict[str, Any] = {}

    if "anthropic" in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": aws_config.max_tokens or 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if aws_config.temperature is not None:
            body["temperature"] = aws_config.temperature
    elif "amazon" in model_id:
        body = {
            "inputText": prompt,
            "textGenerationConfig": {"maxTokenCount": aws_config.max_tokens or 4096},
        }
        if aws_config.temperature is not None:
            body["textGenerationConfig"]["temperature"] = aws_config.temperature
    else:
        # Default format for other models
        body = {"prompt": prompt, "max_tokens": aws_config.max_tokens or 4096}
        if aws_config.temperature is not None:
            body["temperature"] = aws_config.temperature

    print(f"Prompting AWS Bedrock with model {model_id}: {prompt}\n")
    try:
        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
        response_body: Dict[str, Any] = json.loads(response.get("body").read())

        # Extract the content based on the model provider
        if "anthropic" in model_id:
            return response_body.get("content")[0]["text"]
        elif "amazon" in model_id:
            return response_body.get("results")[0]["outputText"]
        else:
            return cast(
                str,
                response_body.get(
                    "completion",
                    response_body.get("generated_text", str(response_body)),
                ),
            )
    except Exception as e:
        print(f"Error calling AWS Bedrock: {str(e)}")
        sys.exit(1)
