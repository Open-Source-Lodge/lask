# Lask Tests

This directory contains tests for the Lask project.

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_file.py
```

## End-to-End Provider Tests

The `test_providers_e2e.py` file contains end-to-end tests that validate connectivity with each supported provider by making simple API requests.

These tests:
1. Read API keys from environment variables
2. Run a simple "ping" test to validate connectivity
3. Check for a valid response

### Required Environment Variables

To run these tests, you need to set the appropriate environment variables for each provider:

#### OpenAI
```bash
export OPENAI_API_KEY=your_openai_api_key
```

#### Anthropic
```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### AWS Bedrock
```bash
export AWS_ACCESS_KEY_ID=your_aws_access_key_id
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export AWS_REGION=your_aws_region  # Optional, defaults to us-east-1
export AWS_BEDROCK_MODEL_ID=your_model_id  # Optional, defaults to anthropic.claude-3-sonnet-20240229-v1:0
```

#### Azure OpenAI
```bash
export AZURE_OPENAI_API_KEY=your_azure_api_key
export AZURE_OPENAI_RESOURCE_NAME=your_resource_name
export AZURE_OPENAI_DEPLOYMENT_ID=your_deployment_id
export AZURE_OPENAI_API_VERSION=your_api_version  # Optional, defaults to 2023-05-15
```

### Running Specific Provider Tests

To run tests for a specific provider only:

```bash
# For OpenAI
pytest tests/test_providers_e2e.py::test_openai_ping -v

# For Anthropic
pytest tests/test_providers_e2e.py::test_anthropic_ping -v

# For AWS Bedrock
pytest tests/test_providers_e2e.py::test_aws_ping -v

# For Azure OpenAI
pytest tests/test_providers_e2e.py::test_azure_ping -v
```

### Test Behavior

- Tests are automatically skipped if the required environment variables are not set
- Each test makes a minimal API request to verify connectivity
- Tests validate that a non-empty response is received
- Errors are reported with detailed information about what went wrong