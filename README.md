# lask

A lightweight CLI tool to interact with OpenAI's ChatGPT and other LLMs directly from your terminal.

## Features

- Simple command-line interface to send prompts to GPT-4.1
- Minimal dependencies (only requires the `requests` library)
- Easy installation via pip
- Direct output to your terminal

## Installation

### Using pip (recommended)

```bash
pip install lask
```

(For dev, do `pip install .`)

For a user-specific installation:

```bash
pip install --user lask
```

### From source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lask.git
   ```

2. Navigate to the directory:
   ```bash
   cd lask
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Setup

Before using lask, you need to set up your OpenAI API key:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)

2. Set the environment variable:

   **Linux/macOS:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

   To make it permanent, add the above line to your `~/.bashrc`, `~/.zshrc`, or equivalent shell configuration file.

   **Windows (Command Prompt):**
   ```
   set OPENAI_API_KEY=your-api-key-here
   ```

   **Windows (PowerShell):**
   ```
   $env:OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

Simply run `lask` followed by your prompt in quotes:

```bash
lask "What is the capital of France?"
```

For multi-line or complex prompts:

```bash
lask "Explain the concept of recursion in programming.
Include a simple example in Python."
```

## Troubleshooting

### Command not found

If you get a "command not found" error after installation, ensure that your Python scripts directory is in your PATH.

For user installations, you may need to add the Python user bin directory to your PATH:

**Linux/macOS:**
```bash
# Add to your shell configuration file (~/.bashrc, ~/.zshrc, etc.)
export PATH="$HOME/.local/bin:$PATH"
```

**Windows:**
```
# Add to your PATH environment variable
%APPDATA%\Python\Python3X\Scripts
```
(Replace `Python3X` with your specific Python version)

### API Key Issues

If you see an error about the API key:

1. Double-check that you've correctly set the `OPENAI_API_KEY` environment variable
2. Verify your API key is valid and has enough credits


## Developing

### Build
To build the package, run:

```bash
uv build
```

### Install for development
To install the package in development mode, run:

```bash
pip install dist/lask-0.1.0-py3-none-any.whl
```

## License

GNU General Public License v3.0 (GPL-3.0)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
