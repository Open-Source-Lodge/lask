"""
Configuration handling for lask.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, ClassVar, List
import configparser


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""

    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    streaming: bool = True
    system_prompt: Optional[str] = None

    # Provider-specific settings
    # AWS Bedrock specific
    model_id: Optional[str] = None
    region: Optional[str] = None

    # Azure OpenAI specific
    resource_name: Optional[str] = None
    deployment_id: Optional[str] = None
    api_version: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access to attributes."""
        return getattr(self, key) if hasattr(self, key) else None

    def get(self, key: str, default: Any = None) -> Any:
        """Mimic dict.get() method."""
        value = self.__getitem__(key)
        return default if value is None else value


@dataclass
class LaskConfig:
    """Configuration for lask."""

    # Default provider
    provider: str = "openai"
    # Provider-specific configurations
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    # Default system prompt
    system_prompt: Optional[str] = None
    # Smart command mode: true, false, or auto
    # auto = let the LLM decide if the prompt is a command request
    smart_command: str = "auto"
    # Whether to include previous commands in smart command LLM context
    smart_context_commands: str = "true"
    # Whether to include command output in smart command LLM context
    smart_context_output: str = "false"
    # Whether smart commands from the REPL are added to shell history
    repl_commands_to_shell_history: str = "false"
    # Whether the user has accepted/declined the shell hook install
    # None = not yet asked, "true" = accepted, "false" = declined
    shell_hook: Optional[str] = None

    # Class constants
    CONFIG_PATH: ClassVar[Path] = Path.home() / ".lask-config"
    SUPPORTED_PROVIDERS: ClassVar[List[str]] = ["openai", "anthropic", "aws", "azure"]

    @classmethod
    def config_exists(cls) -> bool:
        """Check if the config file exists."""
        return cls.CONFIG_PATH.exists()

    @classmethod
    def load(cls) -> "LaskConfig":
        """
        Load configuration from ~/.lask-config if it exists.

        Returns:
            LaskConfig: A configuration object.
        """
        config = cls()

        if cls.CONFIG_PATH.exists():
            try:
                parser = configparser.ConfigParser()
                parser.read(cls.CONFIG_PATH)

                # Load default section
                if "default" in parser:
                    for key, value in parser["default"].items():
                        if hasattr(config, key):
                            # Handle type conversion for specific fields
                            if key in ["system_prompt"]:
                                setattr(config, key, value)
                            elif key == "smart_command":
                                setattr(config, key, value.lower().strip())
                            elif key in (
                                "smart_context_commands",
                                "smart_context_output",
                                "repl_commands_to_shell_history",
                            ):
                                setattr(config, key, value.lower().strip())
                            elif key == "shell_hook":
                                setattr(config, key, value.lower().strip())
                            else:
                                setattr(config, key, value)

                # Load provider-specific sections
                for section in parser.sections():
                    if section != "default" and section in cls.SUPPORTED_PROVIDERS:
                        provider_config = ProviderConfig()
                        for key, value in parser[section].items():
                            if hasattr(provider_config, key):
                                # Convert types as needed
                                if key == "temperature" and value:
                                    setattr(provider_config, key, float(value))
                                elif key == "max_tokens" and value:
                                    setattr(provider_config, key, int(value))
                                elif key == "streaming" and value:
                                    setattr(
                                        provider_config, key, value.lower() == "true"
                                    )
                                elif key == "system_prompt" and value:
                                    setattr(provider_config, key, value)
                                else:
                                    setattr(provider_config, key, value)
                        config.providers[section] = provider_config

            except configparser.Error:
                print(
                    f"Warning: Could not parse {cls.CONFIG_PATH}. Using default configuration."
                )
            except Exception as e:
                print(
                    f"Warning: Error reading {cls.CONFIG_PATH}: {e}. Using default configuration."
                )
        else:
            # Config file doesn't exist - make sure default provider exists
            config.providers["openai"] = ProviderConfig(model="gpt-5.2", temperature=0.7)

        return config

    def get_provider_config(self, provider: str) -> ProviderConfig:
        """
        Get the configuration for a specific provider.

        Args:
            provider (str): The provider name

        Returns:
            ProviderConfig: Configuration for the specified provider
        """
        if provider not in self.providers:
            self.providers[provider] = ProviderConfig()
        return self.providers[provider]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key (str): The configuration key
            default (Any, optional): Default value if not found. Defaults to None.

        Returns:
            Any: The configuration value
        """
        return getattr(self, key, default) if hasattr(self, key) else default

    def save_setting(self, section: str, key: str, value: str) -> None:
        """
        Save a single setting to the config file, preserving existing content.

        Args:
            section (str): The config section (e.g. 'default')
            key (str): The setting key
            value (str): The setting value
        """
        parser = configparser.ConfigParser()
        if self.CONFIG_PATH.exists():
            parser.read(self.CONFIG_PATH)
        if section not in parser:
            parser[section] = {}
        parser[section][key] = value
        with open(self.CONFIG_PATH, "w") as f:
            parser.write(f)

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access to attributes."""
        if key == "providers":
            return self.providers
        return getattr(self, key) if hasattr(self, key) else None
