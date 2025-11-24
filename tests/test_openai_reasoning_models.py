"""
Tests for OpenAI reasoning models (o1, o3, o4 series) handling.
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.providers.openai import is_reasoning_model


def get_request_data(mock_function):
    """
    Helper function to extract request data from a mocked function call.
    
    Args:
        mock_function: The mocked function (e.g., non_streaming_openai_response)
        
    Returns:
        dict: The data dictionary passed to the function
    """
    call_args = mock_function.call_args
    # The second positional argument (index 1) is the data dict containing
    # model, messages, stream, temperature, and other API parameters
    return call_args[0][1]


def test_is_reasoning_model_o1_series():
    """Test that o1 series models are correctly identified as reasoning models."""
    assert is_reasoning_model("o1-preview") is True
    assert is_reasoning_model("o1-mini") is True
    assert is_reasoning_model("o1") is True
    assert is_reasoning_model("O1-PREVIEW") is True  # Case insensitive


def test_is_reasoning_model_o3_series():
    """Test that o3 series models are correctly identified as reasoning models."""
    assert is_reasoning_model("o3") is True
    assert is_reasoning_model("o3-mini") is True
    assert is_reasoning_model("o3-pro") is True
    assert is_reasoning_model("O3-MINI") is True  # Case insensitive


def test_is_reasoning_model_o4_series():
    """Test that o4 series models are correctly identified as reasoning models."""
    assert is_reasoning_model("o4-mini") is True
    assert is_reasoning_model("O4-MINI") is True  # Case insensitive


def test_is_reasoning_model_regular_models():
    """Test that regular GPT models are NOT identified as reasoning models."""
    assert is_reasoning_model("gpt-4") is False
    assert is_reasoning_model("gpt-4o") is False
    assert is_reasoning_model("gpt-4o-mini") is False
    assert is_reasoning_model("gpt-4.1") is False
    assert is_reasoning_model("gpt-3.5-turbo") is False
    assert is_reasoning_model("gpt-4-turbo") is False
    assert is_reasoning_model("GPT-4") is False  # Case insensitive


def test_is_reasoning_model_edge_cases():
    """Test edge cases for reasoning model detection."""
    # Models that start with similar letters but aren't reasoning models
    assert is_reasoning_model("other-model") is False
    assert is_reasoning_model("openai-model") is False
    
    # Empty string
    assert is_reasoning_model("") is False
    
    # Models with similar but different numbering
    assert is_reasoning_model("o2-model") is False
    assert is_reasoning_model("o5-model") is False
    assert is_reasoning_model("o") is False


def test_reasoning_model_no_system_message():
    """Test that reasoning models don't include system messages in the request."""
    from src.providers.openai import call_api
    from src.config import LaskConfig, ProviderConfig
    
    # Create a config with a system prompt and streaming disabled
    config = LaskConfig()
    config.system_prompt = "You are a helpful assistant"
    config.providers["openai"] = ProviderConfig(
        api_key="test-key",
        model="o1-preview",
        streaming=False
    )
    
    # Mock both streaming and non-streaming functions
    with patch('src.providers.openai.non_streaming_openai_response') as mock_non_streaming:
        mock_non_streaming.return_value = "Test response"
        
        call_api(config, "Test prompt")
        
        # Check that the function was called
        assert mock_non_streaming.called
        
        # Get the data argument using helper function
        data = get_request_data(mock_non_streaming)
        messages = data.get('messages', [])
        
        # Verify no system message in messages
        for msg in messages:
            assert msg.get('role') != 'system', "System message should not be included for reasoning models"
        
        # Verify user message is present
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        assert len(user_messages) > 0, "User message should be present"


def test_reasoning_model_no_temperature():
    """Test that reasoning models don't include temperature parameter in the request."""
    from src.providers.openai import call_api
    from src.config import LaskConfig, ProviderConfig
    
    # Create a config with temperature and streaming disabled
    config = LaskConfig()
    config.providers["openai"] = ProviderConfig(
        api_key="test-key",
        model="o1-mini",
        temperature=0.7,
        streaming=False
    )
    
    # Mock the non-streaming function
    with patch('src.providers.openai.non_streaming_openai_response') as mock_non_streaming:
        mock_non_streaming.return_value = "Test response"
        
        call_api(config, "Test prompt")
        
        # Check that the function was called
        assert mock_non_streaming.called
        
        # Get the data argument using helper function
        data = get_request_data(mock_non_streaming)
        
        # Verify temperature is not in the request
        assert 'temperature' not in data, "Temperature should not be included for reasoning models"


def test_regular_model_includes_system_message():
    """Test that regular models DO include system messages in the request."""
    from src.providers.openai import call_api
    from src.config import LaskConfig, ProviderConfig
    
    # Create a config with a system prompt and streaming disabled
    config = LaskConfig()
    config.system_prompt = "You are a helpful assistant"
    config.providers["openai"] = ProviderConfig(
        api_key="test-key",
        model="gpt-4o",
        streaming=False
    )
    
    # Mock the non-streaming function
    with patch('src.providers.openai.non_streaming_openai_response') as mock_non_streaming:
        mock_non_streaming.return_value = "Test response"
        
        call_api(config, "Test prompt")
        
        # Check that the function was called
        assert mock_non_streaming.called
        
        # Get the data argument using helper function
        data = get_request_data(mock_non_streaming)
        messages = data.get('messages', [])
        
        # Verify system message is present
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        assert len(system_messages) > 0, "System message should be included for regular models"
        assert system_messages[0].get('content') == "You are a helpful assistant"


def test_regular_model_includes_temperature():
    """Test that regular models DO include temperature parameter in the request."""
    from src.providers.openai import call_api
    from src.config import LaskConfig, ProviderConfig
    
    # Create a config with temperature and streaming disabled
    config = LaskConfig()
    config.providers["openai"] = ProviderConfig(
        api_key="test-key",
        model="gpt-4o",
        temperature=0.7,
        streaming=False
    )
    
    # Mock the non-streaming function
    with patch('src.providers.openai.non_streaming_openai_response') as mock_non_streaming:
        mock_non_streaming.return_value = "Test response"
        
        call_api(config, "Test prompt")
        
        # Check that the function was called
        assert mock_non_streaming.called
        
        # Get the data argument using helper function
        data = get_request_data(mock_non_streaming)
        
        # Verify temperature is in the request
        assert 'temperature' in data, "Temperature should be included for regular models"
        assert data['temperature'] == 0.7
