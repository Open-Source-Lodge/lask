"""
End-to-end tests for provider API connections.

These tests validate that the application can connect to each provider's API
by making a simple request and checking for a valid response.

Tests are skipped if the required environment variables are not set.
"""

import os
import sys
import pytest
from typing import Optional
from pathlib import Path

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import LaskConfig
from src.providers import openai, anthropic, aws, azure


# Short, simple prompt for testing
TEST_PROMPT = "Hello, please respond with a single word."


def has_env_var(var_name: str) -> bool:
    """Check if an environment variable is set and not empty."""
    return bool(os.environ.get(var_name, ""))


# Skip markers for each provider
skip_if_no_openai = pytest.mark.skipif(
    not has_env_var("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY environment variable not set",
)

skip_if_no_anthropic = pytest.mark.skipif(
    not has_env_var("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY environment variable not set",
)

skip_if_no_aws_credentials = pytest.mark.skipif(
    not (has_env_var("AWS_ACCESS_KEY_ID") and has_env_var("AWS_SECRET_ACCESS_KEY")),
    reason="AWS credentials not set in environment variables",
)

skip_if_no_azure = pytest.mark.skipif(
    not (
        has_env_var("AZURE_OPENAI_API_KEY")
        and has_env_var("AZURE_OPENAI_RESOURCE_NAME")
        and has_env_var("AZURE_OPENAI_DEPLOYMENT_ID")
    ),
    reason="Required Azure OpenAI environment variables not set",
)


@skip_if_no_openai
def test_openai_ping():
    """Test that the OpenAI API can be pinged successfully."""
    # Create a minimal config with streaming disabled for easier testing
    config = LaskConfig()
    provider_config = config.get_provider_config("openai")
    provider_config.streaming = False

    # Get API key from environment variable
    # The provider will read from env vars if not explicitly set in config

    try:
        # Make a simple request and verify response
        response = openai.call_api(config, TEST_PROMPT)

        # Verify that we got a non-empty string response
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"OpenAI response: {response}")
    except Exception as e:
        pytest.fail(f"OpenAI API call failed: {str(e)}")


@skip_if_no_anthropic
def test_anthropic_ping():
    """Test that the Anthropic API can be pinged successfully."""
    # Create a minimal config with streaming disabled for easier testing
    config = LaskConfig()
    provider_config = config.get_provider_config("anthropic")
    provider_config.streaming = False

    try:
        # Make a simple request and verify response
        response = anthropic.call_api(config, TEST_PROMPT)

        # Verify that we got a non-empty string response
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"Anthropic response: {response}")
    except Exception as e:
        pytest.fail(f"Anthropic API call failed: {str(e)}")


@skip_if_no_aws_credentials
def test_aws_ping():
    """Test that the AWS Bedrock API can be pinged successfully."""
    # Create a minimal config with streaming disabled for easier testing
    config = LaskConfig()
    provider_config = config.get_provider_config("aws")
    provider_config.streaming = False

    # Set region if provided in environment
    if "AWS_REGION" in os.environ:
        provider_config.region = os.environ["AWS_REGION"]

    # Set model_id if provided in environment, otherwise use a default
    provider_config.model_id = os.environ.get(
        "AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
    )

    try:
        # Make a simple request and verify response
        response = aws.call_api(config, TEST_PROMPT)

        # Verify that we got a non-empty string response
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"AWS Bedrock response: {response}")
    except Exception as e:
        pytest.fail(f"AWS Bedrock API call failed: {str(e)}")


@skip_if_no_azure
def test_azure_ping():
    """Test that the Azure OpenAI API can be pinged successfully."""
    # Create a minimal config with streaming disabled for easier testing
    config = LaskConfig()
    provider_config = config.get_provider_config("azure")
    provider_config.streaming = False

    # Set Azure-specific parameters from environment variables
    provider_config.resource_name = os.environ["AZURE_OPENAI_RESOURCE_NAME"]
    provider_config.deployment_id = os.environ["AZURE_OPENAI_DEPLOYMENT_ID"]

    # Set API version if provided in environment
    if "AZURE_OPENAI_API_VERSION" in os.environ:
        provider_config.api_version = os.environ["AZURE_OPENAI_API_VERSION"]

    try:
        # Make a simple request and verify response
        response = azure.call_api(config, TEST_PROMPT)

        # Verify that we got a non-empty string response
        assert isinstance(response, str)
        assert len(response) > 0

        print(f"Azure OpenAI response: {response}")
    except Exception as e:
        pytest.fail(f"Azure OpenAI API call failed: {str(e)}")


# @pytest.mark.parametrize(
#     "provider_name,provider_module,skip_marker",
#     [
#         ("openai", openai, skip_if_no_openai),
#         ("anthropic", anthropic, skip_if_no_anthropic),
#         ("aws", aws, skip_if_no_aws_credentials),
#         ("azure", azure, skip_if_no_azure),
#     ],
# )
# def test_all_providers_parametrized(provider_name, provider_module, skip_marker):
#     """
#     Parameterized test for all providers.

#     This is an alternative way to test all providers with a single test function.
#     """
#     skip_marker.xfail_if(True, reason=f"Running parametrized test for {provider_name}")

#     # Create a minimal config with streaming disabled for easier testing
#     config = LaskConfig()
#     provider_config = config.get_provider_config(provider_name)
#     provider_config.streaming = False

#     # Set required parameters for specific providers
#     if provider_name == "azure":
#         if "AZURE_OPENAI_RESOURCE_NAME" in os.environ:
#             provider_config.resource_name = os.environ["AZURE_OPENAI_RESOURCE_NAME"]
#         if "AZURE_OPENAI_DEPLOYMENT_ID" in os.environ:
#             provider_config.deployment_id = os.environ["AZURE_OPENAI_DEPLOYMENT_ID"]
#     elif provider_name == "aws":
#         if "AWS_REGION" in os.environ:
#             provider_config.region = os.environ["AWS_REGION"]
#         provider_config.model_id = os.environ.get(
#             "AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
#         )

#     try:
#         # Make a simple request and verify response
#         response = provider_module.call_api(config, TEST_PROMPT)

#         # Verify that we got a non-empty string response
#         assert isinstance(response, str)
#         assert len(response) > 0

#         print(f"{provider_name.capitalize()} response: {response}")
#     except Exception as e:
#         pytest.fail(f"{provider_name.capitalize()} API call failed: {str(e)}")
