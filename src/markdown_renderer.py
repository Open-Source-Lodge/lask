"""
Markdown renderer for terminal output in lask.
"""

import re
import io
import sys

# Define global variables for rich components
Console = None
Markdown = None
RICH_AVAILABLE = False

# Try to import rich, but gracefully handle if not available
try:
    from rich.console import Console
    from rich.markdown import Markdown

    RICH_AVAILABLE = True
except ImportError:
    # Rich library not available, will use fallback rendering
    pass

# Terminal color codes for basic formatting (fallback when rich is not available)
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",  # For code blocks
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    "bg_black": "\033[40m",
    "bg_bright_black": "\033[100m",  # For code block backgrounds
}


class MarkdownRenderer:
    """
    Renderer for Markdown text in the terminal.
    Can use rich if available, otherwise falls back to basic terminal colors.
    """

    def __init__(self, use_colors: bool = True, use_rich: bool = True):
        """
        Initialize the Markdown renderer.

        Args:
            use_colors (bool): Whether to use colors. Defaults to True.
            use_rich (bool): Whether to use rich for rendering if available. Defaults to True.
        """
        self.use_colors = use_colors
        self.use_rich = use_rich and RICH_AVAILABLE

        # Initialize rich console if available and enabled
        self.console = None
        if self.use_rich and RICH_AVAILABLE and Console is not None:
            self.console = Console(highlight=True)

        # Buffer for accumulating text in streaming mode
        self.buffer = io.StringIO()
        self.in_code_block = False
        self.code_fence_pattern = re.compile(r"^```(\w*)$", re.MULTILINE)

    def render_markdown(self, text: str) -> str:
        """
        Render Markdown text to colorized terminal output.

        Args:
            text (str): Markdown text to render

        Returns:
            str: Colorized terminal output
        """
        if not self.use_colors:
            return text

        if self.use_rich:
            # Use rich for rendering if available
            if RICH_AVAILABLE and Console is not None and Markdown is not None:
                with io.StringIO() as string_io:
                    # Redirect console output to string_io
                    console = Console(file=string_io, highlight=True)
                    console.print(Markdown(text))
                    return string_io.getvalue()
            else:
                return self._apply_basic_markdown(text)
        else:
            # Use basic terminal colors otherwise
            return self._apply_basic_markdown(text)

    def _apply_basic_markdown(self, text: str) -> str:
        """
        Apply basic Markdown formatting using terminal color codes.

        Args:
            text (str): Markdown text to format

        Returns:
            str: Text with terminal color codes
        """
        formatted = text

        # Headers
        for i in range(6, 0, -1):
            pattern = rf"^{'#' * i}\s+(.*?)$"
            repl = f"{COLORS['bold']}{COLORS['bright_cyan']}\\1{COLORS['reset']}"
            formatted = re.sub(pattern, repl, formatted, flags=re.MULTILINE)

        # Bold
        formatted = re.sub(
            r"\*\*(.*?)\*\*", f"{COLORS['bold']}\\1{COLORS['reset']}", formatted
        )
        formatted = re.sub(
            r"__(.*?)__", f"{COLORS['bold']}\\1{COLORS['reset']}", formatted
        )

        # Italic
        formatted = re.sub(
            r"\*(.*?)\*", f"{COLORS['italic']}\\1{COLORS['reset']}", formatted
        )
        formatted = re.sub(
            r"_(.*?)_", f"{COLORS['italic']}\\1{COLORS['reset']}", formatted
        )

        # Code blocks
        def replace_code_block(match):
            _language = match.group(1)  # We capture but don't currently use the language
            content = match.group(2)
            lines = content.split("\n")
            formatted_lines = [
                f"{COLORS['bg_bright_black']}{COLORS['bright_white']}{line}{COLORS['reset']}"
                for line in lines
            ]
            return "\n".join(formatted_lines)

        formatted = re.sub(
            r"```(\w*)\n(.*?)\n```", replace_code_block, formatted, flags=re.DOTALL
        )

        # Inline code
        formatted = re.sub(
            r"`(.*?)`", f"{COLORS['bright_black']}\\1{COLORS['reset']}", formatted
        )

        # Lists
        formatted = re.sub(
            r"^(\s*)-\s+(.*?)$",
            f"\\1{COLORS['bright_yellow']}-{COLORS['reset']} \\2",
            formatted,
            flags=re.MULTILINE,
        )
        formatted = re.sub(
            r"^(\s*)\*\s+(.*?)$",
            f"\\1{COLORS['bright_yellow']}*{COLORS['reset']} \\2",
            formatted,
            flags=re.MULTILINE,
        )
        formatted = re.sub(
            r"^(\s*)\d+\.\s+(.*?)$",
            f"\\1{COLORS['bright_yellow']}\\1.{COLORS['reset']} \\2",
            formatted,
            flags=re.MULTILINE,
        )

        # Links
        formatted = re.sub(
            r"\[(.*?)\]\((.*?)\)",
            f"{COLORS['bright_blue']}\\1{COLORS['reset']} ({COLORS['blue']}\\2{COLORS['reset']})",
            formatted,
        )

        # Blockquotes
        formatted = re.sub(
            r"^>\s+(.*?)$",
            f"{COLORS['green']}> \\1{COLORS['reset']}",
            formatted,
            flags=re.MULTILINE,
        )

        return formatted

    def render_streaming_chunk(self, chunk: str) -> str:
        """
        Render a streaming chunk of text with partial Markdown formatting.

        This is optimized for streaming output where we get chunks of text
        that may cut across Markdown elements.

        Args:
            chunk (str): A chunk of text from a streaming response

        Returns:
            str: The rendered chunk with appropriate formatting
        """
        if not self.use_colors:
            return chunk

        # Add the chunk to our buffer
        self.buffer.write(chunk)
        buffer_content = self.buffer.getvalue()

        if self.use_rich:
            # For rich, we'll only do minimal formatting in streaming mode
            # since we can't reliably parse partial Markdown

            # Handle code blocks specially
            code_matches = list(self.code_fence_pattern.finditer(buffer_content))
            if len(code_matches) % 2 == 1:
                # We're in a code block
                if not self.in_code_block:
                    # Just entered a code block
                    self.in_code_block = True
                    return (
                        f"\n{COLORS['bg_bright_black']}{COLORS['bright_white']}{chunk}"
                    )
                else:
                    # Still in a code block
                    return f"{COLORS['bg_bright_black']}{COLORS['bright_white']}{chunk}"
            else:
                # We're not in a code block
                if self.in_code_block:
                    # Just exited a code block
                    self.in_code_block = False
                    return f"{chunk}{COLORS['reset']}\n"
                else:
                    # Normal text outside code block
                    return self._apply_streaming_markdown(chunk)
        else:
            # Apply basic formatting for streaming
            return self._apply_streaming_markdown(chunk)

    def _apply_streaming_markdown(self, chunk: str) -> str:
        """
        Apply limited Markdown formatting to a streaming chunk.

        Args:
            chunk (str): Text chunk to format

        Returns:
            str: Formatted text chunk
        """
        formatted = chunk

        # Only apply formatting that can be done safely on partial text

        # Bold (only if complete markers are in the chunk)
        if "**" in formatted:
            formatted = re.sub(
                r"\*\*(.*?)\*\*", f"{COLORS['bold']}\\1{COLORS['reset']}", formatted
            )

        # Italic (only if complete markers are in the chunk)
        if "*" in formatted and "**" not in formatted:
            formatted = re.sub(
                r"\*(.*?)\*", f"{COLORS['italic']}\\1{COLORS['reset']}", formatted
            )

        # Inline code (only if complete markers are in the chunk)
        if "`" in formatted and "```" not in formatted:
            formatted = re.sub(
                r"`(.*?)`", f"{COLORS['bright_black']}\\1{COLORS['reset']}", formatted
            )

        return formatted

    def reset_buffer(self) -> None:
        """Reset the internal buffer after a complete response."""
        self.buffer = io.StringIO()
        self.in_code_block = False


def get_markdown_renderer(config) -> MarkdownRenderer:
    """
    Get a markdown renderer based on configuration.

    Args:
        config: The application configuration

    Returns:
        MarkdownRenderer: A configured markdown renderer
    """
    # Get markdown rendering settings from config
    use_colors = config.get("use_colors", True)
    use_rich = config.get("use_rich", True)

    # Print a warning if rich was requested but not available
    if use_rich and not RICH_AVAILABLE:
        print(
            "Warning: Rich library requested but not installed. Using basic terminal colors instead.",
            file=sys.stderr,
        )
        print("Install rich with: pip install rich", file=sys.stderr)

    return MarkdownRenderer(use_colors=use_colors, use_rich=use_rich)


def colorize_markdown(text: str, config) -> str:
    """
    Colorize markdown text based on configuration.

    Args:
        text (str): Markdown text to colorize
        config: The application configuration

    Returns:
        str: Colorized text
    """
    renderer = get_markdown_renderer(config)
    return renderer.render_markdown(text)


def colorize_streaming_chunk(chunk: str, renderer: MarkdownRenderer) -> str:
    """
    Colorize a streaming chunk of markdown text.

    Args:
        chunk (str): Text chunk to colorize
        renderer (MarkdownRenderer): The markdown renderer to use

    Returns:
        str: Colorized text chunk
    """
    return renderer.render_streaming_chunk(chunk)
