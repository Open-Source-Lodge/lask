"""
Tests for the ChatHistory class to ensure consistent chat history management.
"""

import sys
from pathlib import Path

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import LaskConfig, ProviderConfig
from src.chat_history import ChatHistory


def _make_config(
    provider: str = "openai",
    default_system_prompt: str | None = None,
    provider_system_prompt: str | None = None,
    smart_context_commands: str = "true",
    smart_context_output: str = "false",
) -> LaskConfig:
    """Helper to build a LaskConfig for testing."""
    config = LaskConfig()
    config.provider = provider
    config.system_prompt = default_system_prompt
    config.smart_context_commands = smart_context_commands
    config.smart_context_output = smart_context_output
    pc = ProviderConfig(system_prompt=provider_system_prompt)
    config.providers[provider] = pc
    return config


class TestChatHistoryInit:
    """Tests for ChatHistory initialization and system prompt handling."""

    def test_no_system_prompt(self):
        config = _make_config()
        history = ChatHistory(config, "openai")
        assert history.messages == []

    def test_default_system_prompt(self):
        config = _make_config(default_system_prompt="Be concise.")
        history = ChatHistory(config, "openai")
        assert len(history.messages) == 1
        assert history.messages[0] == {"role": "system", "content": "Be concise."}

    def test_provider_system_prompt_takes_precedence(self):
        config = _make_config(
            default_system_prompt="default prompt",
            provider_system_prompt="provider prompt",
        )
        history = ChatHistory(config, "openai")
        assert len(history.messages) == 1
        assert history.messages[0]["content"] == "provider prompt"

    def test_empty_command_history_on_init(self):
        config = _make_config()
        history = ChatHistory(config, "openai")
        assert history.command_history == []


class TestChatHistoryMessages:
    """Tests for adding messages to the conversation."""

    def test_add_user_message(self):
        config = _make_config()
        history = ChatHistory(config, "openai")
        history.add_user_message("Hello")
        assert history.messages == [{"role": "user", "content": "Hello"}]

    def test_add_assistant_message(self):
        config = _make_config()
        history = ChatHistory(config, "openai")
        history.add_assistant_message("Hi there")
        assert history.messages == [{"role": "assistant", "content": "Hi there"}]

    def test_multi_turn_conversation(self):
        config = _make_config(default_system_prompt="System")
        history = ChatHistory(config, "openai")
        history.add_user_message("Q1")
        history.add_assistant_message("A1")
        history.add_user_message("Q2")
        history.add_assistant_message("A2")

        assert len(history.messages) == 5
        assert history.messages[0]["role"] == "system"
        assert history.messages[1] == {"role": "user", "content": "Q1"}
        assert history.messages[2] == {"role": "assistant", "content": "A1"}
        assert history.messages[3] == {"role": "user", "content": "Q2"}
        assert history.messages[4] == {"role": "assistant", "content": "A2"}


class TestChatHistorySmartCommands:
    """Tests for smart command history management."""

    def test_add_command_entry(self):
        config = _make_config()
        history = ChatHistory(config, "openai")
        entry = {"prompt": "list files", "command": "ls", "output": "file.txt"}
        history.add_command_entry(entry)

        assert len(history.command_history) == 1
        assert history.command_history[0] == entry

    def test_add_smart_command_context_with_all_enabled(self):
        config = _make_config(
            smart_context_commands="true",
            smart_context_output="true",
        )
        history = ChatHistory(config, "openai")
        entry = {
            "prompt": "list files",
            "command": "ls -la",
            "output": "total 8\nfile.txt",
        }
        history.add_smart_command_context(entry)

        assert len(history.messages) == 1
        msg = history.messages[0]
        assert msg["role"] == "assistant"
        assert "[Ran command: ls -la]" in msg["content"]
        assert "[Output:" in msg["content"]
        assert "file.txt" in msg["content"]

    def test_add_smart_command_context_commands_disabled(self):
        config = _make_config(
            smart_context_commands="false",
            smart_context_output="true",
        )
        history = ChatHistory(config, "openai")
        entry = {"prompt": "list files", "command": "ls", "output": "file.txt"}
        history.add_smart_command_context(entry)

        msg = history.messages[0]
        assert "command context is disabled" in msg["content"]
        assert "[Output:" in msg["content"]

    def test_add_smart_command_context_output_disabled(self):
        config = _make_config(
            smart_context_commands="true",
            smart_context_output="false",
        )
        history = ChatHistory(config, "openai")
        entry = {"prompt": "list files", "command": "ls", "output": "file.txt"}
        history.add_smart_command_context(entry)

        msg = history.messages[0]
        assert "[Ran command: ls]" in msg["content"]
        assert "output context is disabled" in msg["content"]

    def test_add_smart_command_context_no_output(self):
        config = _make_config(
            smart_context_commands="true",
            smart_context_output="true",
        )
        history = ChatHistory(config, "openai")
        entry = {"prompt": "list files", "command": "ls"}
        history.add_smart_command_context(entry)

        msg = history.messages[0]
        assert "[Ran command: ls]" in msg["content"]
        # No output in entry → output context disabled message
        assert "output context is disabled" in msg["content"]

    def test_command_entry_and_context_together(self):
        """Smart command adds both to command_history and to messages."""
        config = _make_config(
            smart_context_commands="true",
            smart_context_output="true",
        )
        history = ChatHistory(config, "openai")
        entry = {"prompt": "list files", "command": "ls", "output": "a.py"}
        history.add_command_entry(entry)
        history.add_smart_command_context(entry)

        assert len(history.command_history) == 1
        assert len(history.messages) == 1
        assert history.messages[0]["role"] == "assistant"


class TestChatHistoryConsistency:
    """Ensure the same ChatHistory works for both REPL-like and one-off-like usage."""

    def test_one_off_pattern(self):
        """Simulates the one-off prompt pattern: system prompt + single user message."""
        config = _make_config(default_system_prompt="Be helpful.")
        history = ChatHistory(config, "openai")
        history.add_user_message("What is Python?")

        assert len(history.messages) == 2
        assert history.messages[0]["role"] == "system"
        assert history.messages[1]["role"] == "user"

    def test_repl_pattern(self):
        """Simulates the REPL pattern: system prompt + multi-turn + smart commands."""
        config = _make_config(
            default_system_prompt="System",
            smart_context_commands="true",
            smart_context_output="true",
        )
        history = ChatHistory(config, "openai")

        # First turn: normal prompt
        history.add_user_message("Hello")
        history.add_assistant_message("Hi!")

        # Second turn: smart command
        entry = {"prompt": "list files", "command": "ls", "output": "a.py"}
        history.add_command_entry(entry)
        history.add_smart_command_context(entry)

        # Third turn: normal prompt referencing the command
        history.add_user_message("What does a.py do?")
        history.add_assistant_message("It does things.")

        assert len(history.messages) == 6
        roles = [m["role"] for m in history.messages]
        assert roles == [
            "system",
            "user",
            "assistant",
            "assistant",
            "user",
            "assistant",
        ]
        assert len(history.command_history) == 1
