#!/usr/bin/env python3
# repl_test.py - Test for line wrapping in REPL mode

import os
import sys
import code
import readline
import shutil
import atexit

def get_terminal_width():
    """Get the current terminal width"""
    try:
        return shutil.get_terminal_size().columns
    except (AttributeError, ValueError, OSError):
        return 80  # Default fallback value

def setup_readline():
    """Set up readline with history and proper line wrapping"""
    # Set up history file
    history_file = os.path.join(os.path.expanduser("~"), ".repl_test_history")

    try:
        readline.read_history_file(history_file)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    # Save history on exit
    atexit.register(readline.write_history_file, history_file)

    # Configure readline for proper line wrapping
    readline.parse_and_bind('set horizontal-scroll-mode off')
    readline.parse_and_bind('set editing-mode emacs')
    readline.parse_and_bind('set mark-modified-lines on')

    # Set terminal width
    os.environ["COLUMNS"] = str(get_terminal_width())

class WrappingConsole(code.InteractiveConsole):
    """An interactive console with improved line wrapping for long inputs"""

    def __init__(self, locals=None):
        super().__init__(locals=locals)
        self.ps1 = "\033[1;32m>\033[0m "  # Green prompt
        self.ps2 = "... "  # Continuation prompt

    def raw_input(self, prompt=""):
        """Override to ensure we have a newline after input for clean separation"""
        result = super().raw_input(prompt)
        # Add a newline after long inputs for better readability
        if len(result) > get_terminal_width() // 3:
            print()
        return result

    def runsource(self, source, filename="<input>", symbol="single"):
        """Process input and demonstrate line wrapping"""
        # Handle exit command
        if source.strip().lower() in ("exit", "quit"):
            raise SystemExit

        # Echo the input to demonstrate it was received correctly
        print(f"You entered: {source}")

        # Generate a long response to demonstrate output wrapping
        if "long" in source.lower():
            # Generate a long paragraph to demonstrate output wrapping
            words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
                    "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
                    "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"]
            long_text = " ".join([words[i % len(words)] for i in range(100)])
            print(f"Generated long text:\n{long_text}")

        return False  # Don't try to execute as Python code

def main():
    """Run the wrapping console test"""
    setup_readline()

    print("\n==== REPL Line Wrapping Test ====")
    print(f"Terminal width: {get_terminal_width()} columns")
    print("Type a long line to test line wrapping")
    print("Type 'long' to generate a long response")
    print("Type 'exit' or 'quit' to exit")

    console = WrappingConsole()
    try:
        console.interact(banner="", exitmsg="\nExiting REPL test...")
    except (KeyboardInterrupt, SystemExit):
        print("\nExiting...")

if __name__ == "__main__":
    main()
