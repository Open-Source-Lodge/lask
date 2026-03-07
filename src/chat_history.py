"""
Chat history management for lask.

Provides a consistent ChatHistory class used across REPL and one-off modes
to manage conversation messages, system prompts, and smart command context.
"""

from typing import List, Dict

from src.config import LaskConfig


class ChatHistory:
    """
    Manages conversation history for consistent chat context across modes.

    Encapsulates the conversation messages list and smart command history,
    handling system prompt initialization, message tracking, and smart
    command context assembly.
    """

    def __init__(self, config: LaskConfig, provider: str) -> None:
        self._messages: List[Dict[str, str]] = []
        self._command_history: List[Dict[str, str]] = []
        self._config = config
        self._provider = provider
        self._init_system_prompt()

    def _init_system_prompt(self) -> None:
        """Add system prompt from config if available.

        Provider-specific system prompts take precedence over the default.
        """
        provider_config = self._config.get_provider_config(self._provider)
        provider_system_prompt = provider_config.system_prompt
        default_system_prompt = self._config.system_prompt

        if provider_system_prompt is not None:
            self._messages.append({"role": "system", "content": provider_system_prompt})
        elif default_system_prompt is not None:
            self._messages.append({"role": "system", "content": default_system_prompt})

    @property
    def messages(self) -> List[Dict[str, str]]:
        """The full list of conversation messages."""
        return self._messages

    @property
    def command_history(self) -> List[Dict[str, str]]:
        """History of smart command interactions."""
        return self._command_history

    def add_user_message(self, content: str) -> None:
        """Append a user message to the conversation."""
        self._messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Append an assistant message to the conversation."""
        self._messages.append({"role": "assistant", "content": content})

    def add_command_entry(self, entry: Dict[str, str]) -> None:
        """Record a smart command interaction in the command history.

        Args:
            entry: Dict with keys 'prompt', 'command', and optionally 'output'.
        """
        self._command_history.append(entry)

    def add_smart_command_context(self, entry: Dict[str, str]) -> None:
        """Add smart command result to conversation for follow-up context.

        This allows follow-up questions to reference the command and its output.

        Args:
            entry: Dict with keys 'prompt', 'command', and optionally 'output'.
        """
        parts: List[str] = []

        if self._config.smart_context_commands == "true":
            parts.append(f"[Ran command: {entry['command']}]")
        else:
            parts.append(
                "[A command was executed but command context is disabled. "
                "Enable with smart_context_commands=true]"
            )

        if self._config.smart_context_output == "true" and entry.get("output"):
            parts.append(f"[Output:\n{entry['output']}\n]")
        else:
            parts.append(
                "[Command output context is disabled. "
                "Enable with smart_context_output=true]"
            )

        self._messages.append({"role": "assistant", "content": "\n".join(parts)})
